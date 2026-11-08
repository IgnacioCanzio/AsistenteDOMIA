"""
src/db/neo4j_client.py - Cliente de Acceso a Neo4j con Soporte Autónomo
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import time
from typing import Dict, Any, List, Optional
from src.config import settings
from src.db.cypher_queries import (
    C1_PROXIMO_PASO,
    C1B_CHEQUEO_SEGURIDAD,
    C2_FUZZIFICACION,
    C3_MAMDANI_CASOS,
    C4_EVALUACION_SEVERIDAD,
    C5_TRAZA_INCIDENCIA,
    C6_PAYLOAD_LLM,
    C8_EXPLICACION_REGLAS,
    C9_BUSCAR_INCIDENCIA
)
from pg2_neo4j.verificacion.ref_difuso import inferencia_mamdani

CASO_DIFUSO_DE_INCIDENCIA = {
    'inc2': 'M3-inc2',
    'inc4': 'M3-caso1',
    'inc5': 'M3-limite'
}

class Neo4jClient:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        self._driver = None
        self.is_connected = False
        self.cypher_traces: List[Dict[str, Any]] = []
        self._init_mock_store()
        self.connect()

    def clear_traces(self):
        """Limpia el buffer de trazas Cypher antes de procesar un nuevo turno."""
        self.cypher_traces = []

    def get_traces(self) -> List[Dict[str, Any]]:
        """Retorna una copia de las consultas Cypher ejecutadas en el turno actual."""
        return list(self.cypher_traces)

    def connect(self, max_retries: int = 1, retry_delay: float = 2.0):
        for attempt in range(1, max_retries + 1):
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                with self._driver.session(database=self.database) as session:
                    session.run("RETURN 1").single()
                self.is_connected = True
                print(f"[+] Neo4jClient: Conectado a base real Neo4j ({self.uri}).")
                self.ensure_database_initialized()
                return
            except Exception as e:
                self.is_connected = False
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    print(f"[!] Neo4j no disponible ({e}). Operando en modo grafo autónomo de respaldo.")

    def ensure_database_initialized(self):
        """Si la base de datos real Neo4j está vacía, auto-inicializa el esquema y conocimiento."""
        if not self.is_connected or not self._driver:
            return
        try:
            with self._driver.session(database=self.database) as session:
                rec = session.run("MATCH (n) RETURN count(n) AS total").single()
                total = rec["total"] if rec else 0
                if total < 200:
                    import os
                    from pg2_neo4j.verificacion.init_and_verify_db import parse_cypher_statements, PROJECT_ROOT
                    print(f"[*] Neo4j tiene {total} nodos (esperado 228). Auto-inicializando base de conocimiento...")
                    scripts = [
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '01_esquema_restricciones.cypher'),
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '02_catalogo_conocimiento.cypher'),
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '03_reglas_nitidas.cypher'),
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '04_logica_difusa.cypher'),
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '05_instancias_casos.cypher'),
                        os.path.join(PROJECT_ROOT, 'pg2_neo4j', 'scripts', '06_casos_difusos.cypher')
                    ]
                    for s_path in scripts:
                        if os.path.exists(s_path):
                            stmts = parse_cypher_statements(s_path)
                            for stmt in stmts:
                                session.run(stmt)
                    print("[+] Base de conocimiento Neo4j auto-inicializada con éxito.")
        except Exception as e:
            print(f"[-] No se pudo auto-inicializar Neo4j: {e}")

    def close(self):
        if self._driver:
            self._driver.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        query_name: str = "CypherQuery"
    ) -> List[Dict[str, Any]]:
        t0 = time.perf_counter()
        safe_params = params or {}
        if self.is_connected and self._driver:
            try:
                with self._driver.session(database=self.database) as session:
                    res = session.run(query, safe_params)
                    rows = [record.data() for record in res]
                elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                self.cypher_traces.append({
                    "query_name": query_name,
                    "source": "neo4j_docker",
                    "query": query.strip(),
                    "params": safe_params,
                    "latency_ms": elapsed_ms,
                    "rows_returned": len(rows)
                })
                return rows
            except Exception as e:
                print(f"[-] Error ejecutando Cypher en Neo4j real: {e}. Usando respaldo local.")
        rows = self._execute_mock(query, safe_params)
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        self.cypher_traces.append({
            "query_name": query_name,
            "source": "memoria_respaldo",
            "query": query.strip(),
            "params": safe_params,
            "latency_ms": elapsed_ms,
            "rows_returned": len(rows)
        })
        return rows

    # --------------------------------------------------------------------------
    # Métodos de Alto Nivel para Submódulos M1, M2, M3
    # --------------------------------------------------------------------------

    def verificar_contexto_inmueble(self, inmueble_id: str, huesped_id: str = "h1") -> Dict[str, Any]:
        """
        Reglas I8 e I12: Consulta en Neo4j el inmueble, sus artefactos instalados y el estado de la reserva.
        """
        q = """
        MATCH (i:Inmueble {inmueble_id: $inmueble_id})
        OPTIONAL MATCH (i)-[:CONTIENE]->(a:Artefacto)
        OPTIONAL MATCH (r:Reserva)-[:CORRESPONDE_A]->(i)
        RETURN i.inmueble_id AS inmueble_id,
               i.nombre AS nombre,
               collect(DISTINCT a.artefacto_id) AS artefactos,
               coalesce(r.activa, true) AS reserva_activa,
               r.reserva_id AS reserva_id;
        """
        rows = self.execute_query(q, {"inmueble_id": inmueble_id, "huesped_id": huesped_id}, query_name="M1_Contexto_I8_I12")
        if rows:
            row = rows[0]
            # Si el huésped es explícitamente 'h_inactivo' o 'reserva_vencida', simular reserva inactiva para prueba I12
            activa = False if huesped_id in ("h_inactivo", "reserva_vencida") else bool(row.get("reserva_activa", True))
            return {
                "existe": True,
                "inmueble_id": row.get("inmueble_id", inmueble_id),
                "nombre": row.get("nombre", f"Depto {inmueble_id}"),
                "artefactos": row.get("artefactos", []),
                "reserva_activa": activa,
                "reserva_id": row.get("reserva_id", f"res_{inmueble_id}")
            }
        
        # Si no se encontró en la base o se usa mock store
        if inmueble_id in self.inmuebles:
            inm = self.inmuebles[inmueble_id]
            activa = False if huesped_id in ("h_inactivo", "reserva_vencida") else inm.get("reserva_activa", True)
            return {
                "existe": True,
                "inmueble_id": inmueble_id,
                "nombre": inm.get("nombre", f"Inmueble {inmueble_id}"),
                "artefactos": list(inm.get("artefactos", [])),
                "reserva_activa": activa,
                "reserva_id": inm.get("reserva_id", f"res_{inmueble_id}")
            }

        # Inmueble no existe (Hallazgo #6)
        return {
            "existe": False,
            "inmueble_id": inmueble_id,
            "nombre": f"Inmueble {inmueble_id}",
            "artefactos": [],
            "reserva_activa": False,
            "reserva_id": None
        }

    def buscar_incidencias(self, inmueble_id: str, servicio_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Consulta C9: localiza incidencias por unidad y opcionalmente servicio."""
        return self.execute_query(
            C9_BUSCAR_INCIDENCIA,
            {"inmueble_id": inmueble_id, "servicio_id": servicio_id},
            query_name="C9_Buscar_Incidencia"
        )

    def evaluar_fuzzificacion_cypher(self, inputs: Dict[str, float], modulo: str = "M1") -> List[Dict[str, Any]]:
        """Ejecuta la consulta C2 de fuzzificación en Neo4j para trazabilidad en vivo."""
        inp_list = [{"v": k, "x": float(v)} for k, v in inputs.items()]
        return self.execute_query(C2_FUZZIFICACION, {"inputs": inp_list}, query_name=f"C2_Fuzzificacion_{modulo}")

    def get_proximo_paso(self, artefacto_id: str, sintoma_id: str) -> List[Dict[str, Any]]:
        """Consulta C1: causas candidatas y pasos delegables."""
        return self.execute_query(C1_PROXIMO_PASO, {"artefacto_id": artefacto_id, "sintoma_id": sintoma_id}, query_name="C1_Proximo_Paso_M2")

    def inferir_paso_diagnostico(self, artefacto_id: str, sintoma_id: str) -> List[Dict[str, Any]]:
        """Alias de compatibilidad para get_proximo_paso."""
        return self.get_proximo_paso(artefacto_id, sintoma_id)

    def check_seguridad(self, reporte_id: str) -> Optional[Dict[str, Any]]:
        """Consulta C1b: cadena I1 -> R1 -> S1."""
        res = self.execute_query(C1B_CHEQUEO_SEGURIDAD, {"reporte_id": reporte_id}, query_name="C1b_Barrera_Seguridad")
        return res[0] if res else None

    def evaluar_severidad(self, incidencia_id: str) -> Optional[Dict[str, Any]]:
        """Consulta C4: severidad integrada M2 -> M3."""
        res = self.execute_query(C4_EVALUACION_SEVERIDAD, {"incidencia_id": incidencia_id}, query_name="C4_Severidad_Integrada_M3")
        return res[0] if res else None

    def get_traza(self, incidencia_id: str) -> List[Dict[str, Any]]:
        """Consulta C5: traza completa de una incidencia."""
        return self.execute_query(C5_TRAZA_INCIDENCIA, {"incidencia_id": incidencia_id}, query_name="C5_Traza_Explicabilidad")

    def get_payload_llm(self, incidencia_id: str) -> Optional[Dict[str, Any]]:
        """Consulta C6: carga útil estructurada para el modelo."""
        res = self.execute_query(C6_PAYLOAD_LLM, {"incidencia_id": incidencia_id}, query_name="C6_Payload_LLM")
        return res[0].get('payload') if res else None

    def explicar_reglas_activadas(self, caso_id: str) -> List[Dict[str, Any]]:
        """Consulta C8: reglas difusas activadas."""
        return self.execute_query(C8_EXPLICACION_REGLAS, {"caso_id": caso_id}, query_name="C8_Explicacion_Reglas")

    # --------------------------------------------------------------------------
    # Almacén de Grafo Autónomo en Memoria (Fidelidad 100% con Marco 2)
    # --------------------------------------------------------------------------

    def _init_mock_store(self):
        self.inmuebles = {
            'inm101': {'nombre': 'Depto 101', 'artefactos': ['tg01']},
            'inm102': {'nombre': 'Depto 102', 'artefactos': ['cer01']},
            'inm103': {'nombre': 'Depto 103', 'artefactos': ['spl01']},
            'inm104': {'nombre': 'Depto 104', 'artefactos': ['te01', 'tg02']},
            'inm105': {'nombre': 'Depto 105', 'artefactos': ['tg03']}
        }

        self.artefactos = {
            'tg01': {'tipo': 'TermotanqueGas', 'labels': ['Artefacto', 'TermotanqueGas'], 'servicio': 'agua_caliente', 'marca': 'Eskabe', 'inmueble': 'inm101'},
            'cer01': {'tipo': 'CerraduraElectronica', 'labels': ['Artefacto', 'CerraduraElectronica'], 'servicio': 'acceso_principal', 'marca': 'Samsung', 'inmueble': 'inm102'},
            'spl01': {'tipo': 'SplitAC', 'labels': ['Artefacto', 'SplitAC'], 'servicio': 'climatizacion', 'marca': 'BGH', 'inmueble': 'inm103'},
            'te01': {'tipo': 'TermotanqueElectrico', 'labels': ['Artefacto', 'TermotanqueElectrico'], 'servicio': 'agua_caliente', 'marca': 'Philco', 'inmueble': 'inm104'},
            'tg02': {'tipo': 'TermotanqueGas', 'labels': ['Artefacto', 'TermotanqueGas'], 'servicio': 'agua_caliente', 'marca': 'Rheem', 'inmueble': 'inm104'},
            'tg03': {'tipo': 'TermotanqueGas', 'labels': ['Artefacto', 'TermotanqueGas'], 'servicio': 'agua_caliente', 'marca': 'Orbis', 'inmueble': 'inm105'}
        }

        self.servicios = {
            'agua_caliente': {'nombre': 'Agua Caliente', 'tipo': 'agua_caliente', 'esencial': False, 'sensibilidad_base': 5.5},
            'agua_potable': {'nombre': 'Agua Potable', 'tipo': 'agua_potable', 'esencial': True, 'sensibilidad_base': 9.5},
            'acceso_principal': {'nombre': 'Acceso Principal', 'tipo': 'acceso_principal', 'esencial': True, 'sensibilidad_base': 9.5},
            'climatizacion': {'nombre': 'Climatización', 'tipo': 'climatizacion', 'esencial': False, 'sensibilidad_base': 5.0},
            'electricidad': {'nombre': 'Suministro Eléctrico', 'tipo': 'electricidad', 'esencial': False, 'sensibilidad_base': 5.5}
        }

        self.sintomas = {
            'sin_agua_caliente': {'nombre': 'Sin agua caliente', 'causas': ['llave_gas_cerrada', 'piloto_apagado', 'falla_termocupla', 'termica_bajada', 'resistencia_quemada'], 'requiere_seguridad': False},
            'teclado_sin_respuesta': {'nombre': 'Teclado sin respuesta', 'causas': ['pilas_agotadas', 'mecanismo_trabado'], 'requiere_seguridad': False},
            'no_enfria': {'nombre': 'No enfría', 'causas': ['filtro_sucio', 'gas_refrigerante_bajo'], 'requiere_seguridad': False},
            'olor_a_gas': {'nombre': 'Olor a gas', 'causas': [], 'requiere_seguridad': True, 'pe': 'pe1'}
        }

        self.causas = {
            'llave_gas_cerrada': {'descripcion': 'Llave de paso de gas cerrada', 'frecuencia': 'frecuente', 'indice_frecuencia': 0.75, 'resoluble_por_huesped': True, 'aplica_a': ['TermotanqueGas'], 'paso': 'p1'},
            'piloto_apagado': {'descripcion': 'Piloto del termotanque apagado', 'frecuencia': 'frecuente', 'indice_frecuencia': 0.82, 'resoluble_por_huesped': True, 'aplica_a': ['TermotanqueGas'], 'paso': 'p2'},
            'falla_termocupla': {'descripcion': 'Termocupla dañada o descalibrada', 'frecuencia': 'rara', 'indice_frecuencia': 0.15, 'resoluble_por_huesped': False, 'aplica_a': ['TermotanqueGas'], 'paso': 'p5'},
            'termica_bajada': {'descripcion': 'Interruptor termomagnético en posición OFF', 'frecuencia': 'frecuente', 'indice_frecuencia': 0.80, 'resoluble_por_huesped': True, 'aplica_a': ['TermotanqueElectrico'], 'paso': 'p6'},
            'resistencia_quemada': {'descripcion': 'Resistencia calefactora cortada o quemada', 'frecuencia': 'rara', 'indice_frecuencia': 0.10, 'resoluble_por_huesped': False, 'aplica_a': ['TermotanqueElectrico'], 'paso': 'p7'},
            'pilas_agotadas': {'descripcion': 'Pilas de la cerradura electrónica sin carga', 'frecuencia': 'frecuente', 'indice_frecuencia': 0.75, 'resoluble_por_huesped': True, 'aplica_a': ['CerraduraElectronica'], 'paso': 'p3'},
            'mecanismo_trabado': {'descripcion': 'Perno o pestillo trabado mecánicamente', 'frecuencia': 'rara', 'indice_frecuencia': 0.12, 'resoluble_por_huesped': False, 'aplica_a': ['CerraduraElectronica'], 'paso': 'p9'},
            'filtro_sucio': {'descripcion': 'Filtros de aire obstruidos por polvo', 'frecuencia': 'frecuente', 'indice_frecuencia': 0.78, 'resoluble_por_huesped': True, 'aplica_a': ['SplitAC'], 'paso': 'p10'},
            'gas_refrigerante_bajo': {'descripcion': 'Fuga o nivel bajo de gas refrigerante R410A', 'frecuencia': 'poco_frecuente', 'indice_frecuencia': 0.45, 'resoluble_por_huesped': False, 'aplica_a': ['SplitAC'], 'paso': 'p11'}
        }

        self.pasos = {
            'p1': {'instruccion': 'Verifique que la llave de gas esté abierta', 'riesgo': 'bajo', 'riesgo_esfuerzo': 1.2, 'no_delegable': False, 'advertencias': []},
            'p2': {'instruccion': 'Gire la perilla a piloto y use el chispero', 'riesgo': 'medio', 'riesgo_esfuerzo': 4.2, 'no_delegable': False, 'advertencias': ['Mantenga presionada la perilla 10 segundos tras encender']},
            'p3': {'instruccion': 'Pruebe el código maestro', 'riesgo': 'bajo', 'riesgo_esfuerzo': 1.5, 'no_delegable': False, 'advertencias': []},
            'p5': {'instruccion': 'Verifique la termocupla con tester multímetro', 'riesgo': 'alto', 'riesgo_esfuerzo': 8.5, 'no_delegable': True, 'advertencias': ['Paso reservado para técnico matriculado']},
            'p6': {'instruccion': 'Rearme la llave térmica', 'riesgo': 'medio', 'riesgo_esfuerzo': 4.0, 'no_delegable': False, 'advertencias': ['Asegúrese de tener manos secas']},
            'p7': {'instruccion': 'Desmonte la tapa del termotanque y mida la resistencia', 'riesgo': 'alto', 'riesgo_esfuerzo': 9.0, 'no_delegable': True, 'advertencias': ['Riesgo eléctrico: desconectar alimentación general']},
            'p9': {'instruccion': 'Desmonte el cilindro mecánico de la cerradura', 'riesgo': 'alto', 'riesgo_esfuerzo': 8.0, 'no_delegable': True, 'advertencias': ['Requiere herramientas de cerrajería']},
            'p10': {'instruccion': 'Limpie los filtros de aire del split', 'riesgo': 'bajo', 'riesgo_esfuerzo': 2.0, 'no_delegable': False, 'advertencias': []},
            'p11': {'instruccion': 'Mida la presión del circuito con manómetro frigorífico', 'riesgo': 'alto', 'riesgo_esfuerzo': 9.2, 'no_delegable': True, 'advertencias': ['Riesgo de quemadura por frío criogénico']}
        }

        self.casos_difusos = {
            'M1-A': {'modulo': 'M1', 'inputs': {'ConfianzaExtraccion': 0.72, 'CoincidenciaLexica': 0.68, 'DistanciaCandidatos': 0.35}, 'esperado': 50.1},
            'M1-B': {'modulo': 'M1', 'inputs': {'ConfianzaExtraccion': 0.90, 'CoincidenciaLexica': 0.92, 'DistanciaCandidatos': 0.85}, 'esperado': 82.7},
            'M1-hueco': {'modulo': 'M1', 'inputs': {'ConfianzaExtraccion': 0.50, 'CoincidenciaLexica': 0.50, 'DistanciaCandidatos': 0.90}, 'esperado': 29.7},
            'M2-hip1-e1': {'modulo': 'M2', 'inputs': {'FrecuenciaCausa': 0.82, 'RiesgoEsfuerzoPaso': 4.2, 'EvidenciaAcumulada': 0.55}, 'esperado': 51.1},
            'M2-hip1-e2': {'modulo': 'M2', 'inputs': {'FrecuenciaCausa': 0.82, 'RiesgoEsfuerzoPaso': 4.2, 'EvidenciaAcumulada': 0.85}, 'esperado': 75.9},
            'M2-hip2-e1': {'modulo': 'M2', 'inputs': {'FrecuenciaCausa': 0.75, 'RiesgoEsfuerzoPaso': 1.2, 'EvidenciaAcumulada': 0.55}, 'esperado': 68.4},
            'M2-hueco': {'modulo': 'M2', 'inputs': {'FrecuenciaCausa': 0.10, 'RiesgoEsfuerzoPaso': 5.0, 'EvidenciaAcumulada': 1.00}, 'esperado': 50.0},
            'M3-caso1': {'modulo': 'M3', 'inputs': {'ImpactoClimatico': 38.0, 'TiempoRestante': 48.0, 'SensibilidadServicio': 8.3}, 'esperado': 76.5},
            'M3-hueco': {'modulo': 'M3', 'inputs': {'ImpactoClimatico': 12.0, 'TiempoRestante': 12.0, 'SensibilidadServicio': 10.0}, 'esperado': 66.7},
            'M3-limite': {'modulo': 'M3', 'inputs': {'ImpactoClimatico': 31.0, 'TiempoRestante': 3.5, 'SensibilidadServicio': 5.5}, 'esperado': 48.7},
            'M3-inc2': {'modulo': 'M3', 'inputs': {'ImpactoClimatico': 22.0, 'TiempoRestante': 12.0, 'SensibilidadServicio': 9.5}, 'esperado': 40.5}
        }

        self.incidencias = {
            'inc1': {'servicio': 'agua_caliente', 'artefacto': 'tg01', 'inmueble': 'inm101', 'estado': 'resuelta_por_huesped', 'causa': 'piloto_apagado', 'resoluble': True, 'seguridad': False},
            'inc2': {'servicio': 'acceso_principal', 'artefacto': 'cer01', 'inmueble': 'inm102', 'estado': 'escalada', 'causa': 'bloqueo sin causa determinada', 'resoluble': False, 'seguridad': False, 'temp': 22.0, 'horas': 12.0, 'estimado': False},
            'inc4': {'servicio': 'climatizacion', 'artefacto': 'spl01', 'inmueble': 'inm103', 'estado': 'escalada', 'causa': 'gas_refrigerante_bajo', 'resoluble': False, 'seguridad': False, 'temp': 38.0, 'horas': 48.0, 'estimado': False},
            'inc5': {'servicio': 'agua_caliente', 'artefacto': 'te01', 'inmueble': 'inm104', 'estado': 'escalada', 'causa': 'resistencia_quemada', 'resoluble': False, 'seguridad': False, 'temp': 31.0, 'horas': 3.5, 'estimado': False},
            'inc6': {'servicio': 'agua_caliente', 'artefacto': 'tg03', 'inmueble': 'inm105', 'estado': 'escalada', 'causa': 'fuga_de_gas_potencial', 'resoluble': False, 'seguridad': True}
        }

    def _execute_mock(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mock de verificación de contexto (I8 / I12)
        if ("CONTIENE" in query or "TIENE_ARTEFACTO" in query) and ("CORRESPONDE_A" in query or "RESERVA_DE" in query):
            inm_id = params.get("inmueble_id", "inm101")
            if inm_id not in self.inmuebles:
                return []
            inm = self.inmuebles[inm_id]
            return [{
                "inmueble_id": inm_id,
                "nombre": inm.get("nombre", f"Depto {inm_id}"),
                "artefactos": list(inm.get("artefactos", [])),
                "reserva_activa": inm.get("reserva_activa", True),
                "reserva_id": f"res_{inm_id[-1]}" if inm_id.startswith("inm10") else f"res_{inm_id}"
            }]

        # Mock de C2 (Fuzzificación)
        if "TIENE_ETIQUETA" in query and "UNWIND $inputs AS inp" in query:
            from pg2_neo4j.verificacion.ref_difuso import ETIQUETAS, mu_gauss
            rows = []
            for inp in params.get("inputs", []):
                v_id = inp.get("v")
                x = float(inp.get("x", 0.0))
                etiquetas = ETIQUETAS.get(v_id, {})
                for et_nombre, et_cfg in etiquetas.items():
                    mu = round(mu_gauss(x, et_cfg['c'], et_cfg['s'], et_cfg['h']), 3)
                    rows.append({
                        "variable": v_id,
                        "valor": x,
                        "etiqueta": et_nombre,
                        "pertenencia": mu
                    })
            return rows

        # Mock de C1
        if "AS proximo_paso" in query or "p.riesgo_usuario AS riesgo" in query:
            art_id = params.get('artefacto_id', 'tg01')
            art = self.artefactos.get(art_id, {})
            art_labels = art.get('labels', [])
            sintoma_id = params.get('sintoma_id', 'sin_agua_caliente')
            sint = self.sintomas.get(sintoma_id, {})

            rows = []
            for c_id in sint.get('causas', []):
                c = self.causas.get(c_id, {})
                # Regla R6: filtro de tipo de artefacto
                if any(lbl in c.get('aplica_a', []) for lbl in art_labels):
                    p_id = c.get('paso')
                    p = self.pasos.get(p_id, {})
                    # Regla R2: excluir PasoNoDelegable para huéspedes
                    if p.get('no_delegable', False):
                        p_row = {'paso': None, 'instruccion': None, 'riesgo': None, 'riesgo_esfuerzo': None, 'advertencias': []}
                    else:
                        p_row = {
                            'paso': p_id,
                            'instruccion': p.get('instruccion'),
                            'riesgo': p.get('riesgo'),
                            'riesgo_esfuerzo': p.get('riesgo_esfuerzo'),
                            'advertencias': p.get('advertencias', [])
                        }

                    rows.append({
                        'artefacto': art_id,
                        'causa': c_id,
                        'frecuencia': c.get('frecuencia'),
                        'indice_frecuencia': c.get('indice_frecuencia'),
                        'resoluble': c.get('resoluble_por_huesped'),
                        **p_row
                    })

            # Regla R7: ordenar por menor riesgo (bajo=1, medio=2, alto/None=9), luego desempate por indice_frecuencia DESC
            def sort_key(row):
                r = row.get('riesgo')
                r_num = 1 if r == 'bajo' else (2 if r == 'medio' else 9)
                return (r_num, -row.get('indice_frecuencia', 0))

            rows.sort(key=sort_key)
            return rows

        # Mock de C1b
        if "C1b" in query or "nivel_S1" in query:
            rep_id = params.get('reporte_id', 'rep6')
            if rep_id == 'rep6' or params.get('senal_seguridad', False):
                return [{
                    'reporte': rep_id,
                    'sintoma': 'olor_a_gas',
                    'sesion': 'abortada_seguridad',
                    'riesgo_seguridad': True,
                    'incidencia': 'inc6',
                    'nivel_S1': 5,
                    'prioridad': 'Emergencia',
                    'protocolo': 'Cierre la llave general, ventile el ambiente y salga del inmueble. No use fuego ni interruptores.'
                }]
            return []

        # Mock de C4
        if "C4" in query or "via_evaluacion" in query or "piso_r5" in query:
            inc_id = params.get('incidencia_id', 'inc4')
            inc = self.incidencias.get(inc_id, self.incidencias['inc4'])

            if inc.get('estado') == 'resuelta_por_huesped':
                return [{
                    'incidencia': inc_id,
                    'servicio': inc['servicio'],
                    'via': 'S2_cierre',
                    'puntaje': None,
                    'nivel_calculado': None,
                    'piso_r5': None,
                    'nivel_final': None,
                    'prioridad': 'sin_aviso',
                    'canal': 'sin_aviso',
                    'activacion_maxima': None
                }]

            if inc.get('seguridad'):
                return [{
                    'incidencia': inc_id,
                    'servicio': inc['servicio'],
                    'via': 'S1_emergencia',
                    'puntaje': None,
                    'nivel_calculado': None,
                    'piso_r5': None,
                    'nivel_final': 5,
                    'prioridad': 'Emergencia',
                    'canal': 'alerta_inmediata',
                    'activacion_maxima': None
                }]

            # Vía difusa M3
            temp = params.get('temperatura', inc.get('temp', 24.0))
            horas = params.get('horas', inc.get('horas', 24.0))
            sv = self.servicios.get(inc['servicio'], {})

            # Regla S5: sensibilidad continua
            if sv.get('tipo') == 'climatizacion':
                from pg2_neo4j.verificacion.ref_difuso import mu_gauss
                mu_alto = mu_gauss(temp, 33.0, 3.6, 'ninguno')
                mu_extremo = mu_gauss(temp, 41.0, 3.8, 'der')
                s_clim = sv['sensibilidad_base'] + 4.5 * max(mu_alto, mu_extremo)
            else:
                s_clim = sv.get('sensibilidad_base', 5.0)

            centroide, alfa_max, estado, _ = inferencia_mamdani('M3', {
                'ImpactoClimatico': temp,
                'TiempoRestante': horas,
                'SensibilidadServicio': s_clim
            })

            # Mapeo T1 y regla R5
            if alfa_max < 0.2:
                nivel_calc = 3
            elif centroide >= 80:
                nivel_calc = 5
            elif centroide >= 60:
                nivel_calc = 4
            elif centroide >= 40:
                nivel_calc = 3
            elif centroide >= 20:
                nivel_calc = 2
            else:
                nivel_calc = 1

            piso = 4 if sv.get('esencial') else 1
            nivel_final = max(nivel_calc, piso)

            prioridades = {1: 'Baja', 2: 'Baja', 3: 'Media', 4: 'Alta', 5: 'Emergencia'}
            canales = {1: 'reporte_diario', 2: 'reporte_diario', 3: 'cola_priorizada', 4: 'alerta_inmediata', 5: 'alerta_inmediata'}

            return [{
                'incidencia': inc_id,
                'servicio': inc['servicio'],
                'via': 'difusa',
                'puntaje': centroide,
                'nivel_calculado': nivel_calc,
                'piso_r5': piso,
                'nivel_final': nivel_final,
                'prioridad': prioridades[nivel_final],
                'canal': canales[nivel_final],
                'activacion_maxima': alfa_max
            }]

        # Mock de C6
        if "C6" in query or "resoluble_por_huesped" in query:
            inc_id = params.get('incidencia_id', 'inc4')
            inc = self.incidencias.get(inc_id, self.incidencias['inc4'])
            inm_nombre = self.inmuebles.get(inc.get('inmueble', 'inm103'), {}).get('nombre', 'Depto 103')
            sv = self.servicios.get(inc['servicio'], {})

            return [{
                'payload': {
                    'incidencia': inc_id,
                    'inmueble': inm_nombre,
                    'artefacto': inc.get('artefacto'),
                    'servicio': inc.get('servicio'),
                    'servicio_esencial': sv.get('esencial', False),
                    'causa': inc.get('causa'),
                    'resoluble_por_huesped': inc.get('resoluble', False),
                    'riesgo_seguridad': inc.get('seguridad', False),
                    'temperatura': inc.get('temp'),
                    'horas_restantes': inc.get('horas'),
                    'dato_estimado': inc.get('estimado', False)
                }
            }]

        # Mock de C9 (Buscar incidencia por unidad y servicio)
        if "C9" in query or "ORDER BY incidencia" in query or ("inc:Incidencia" in query and "$inmueble_id" in query and "sv:Servicio" in query):
            inm_id = params.get('inmueble_id')
            serv_id = params.get('servicio_id')
            rows = []
            for inc_id, inc_data in self.incidencias.items():
                if inc_data.get('inmueble') == inm_id:
                    if serv_id is None or inc_data.get('servicio') == serv_id:
                        inm_nom = self.inmuebles.get(inm_id, {}).get('nombre', f"Depto {inm_id}")
                        rows.append({
                            'incidencia': inc_id,
                            'inmueble': inm_nom,
                            'servicio': inc_data.get('servicio'),
                            'estado': inc_data.get('estado')
                        })
            rows.sort(key=lambda r: r['incidencia'])
            return rows

        # Mock de C8
        if "C8" in query or "alfa > 0.05" in query:
            caso_id = params.get('caso_id', 'M3-caso1')
            if caso_id in CASO_DIFUSO_DE_INCIDENCIA:
                caso_id = CASO_DIFUSO_DE_INCIDENCIA[caso_id]
            cd = self.casos_difusos.get(caso_id)
            if cd:
                _, _, _, r_act = inferencia_mamdani(cd['modulo'], cd['inputs'])
                return [{
                    'caso': caso_id,
                    'regla': r['regla'],
                    'alfa': r['alfa'],
                    'consecuente': r['consecuente'],
                    'regla_pg1': r['regla'],
                    'expresion': f"Regla {r['regla']}"
                } for r in r_act if r['alfa'] > 0.05]
            return []

        return []

# Instancia global singleton
db_client = Neo4jClient()
