"""
src/modules/m2_diagnostico.py - Submódulo M2: Diagnóstico y Resolución Asistida
Responsable de diseño: Nicolás López
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026

Reglas implementadas:
- R6: Filtrado estructural de compatibilidad causa-artefacto.
- R2: Exclusión de pasos no delegables (:PasoNoDelegable) al huésped.
- Priorización difusa M2 Mamdani: FrecuenciaCausa, RiesgoEsfuerzoPaso, EvidenciaAcumulada.
- R11: Descarte de hipótesis y acumulación de evidencia.
- R3: Confirmación de resolución exitosa.
- R8: Límite de presupuesto de 4 pasos o 2 'no puedo' consecutivos -> escalada.
- R4: Protocolo de bloqueo para cerradura electrónica.
- R7: Inyección de advertencias técnicas de seguridad.
- Verbalización controlada con Gemini según principio I10 (fidelidad al payload).
"""

import uuid
from typing import Dict, Any, Optional, Tuple, List
from src.models.schemas import (
    ReporteEstructurado,
    InstruccionEstructurada,
    DiagnosticoFinal
)
from src.db.neo4j_client import db_client
from src.llm.gemini_client import gemini_client
from pg2_neo4j.verificacion.ref_difuso import inferencia_mamdani

class SesionDiagnostico:
    def __init__(
        self,
        sesion_id: str,
        inmueble_id: str,
        huesped_id: Optional[str],
        reporte_id: str,
        artefacto_id: str,
        sintoma_id: str,
        servicio_id: str
    ):
        self.sesion_id = sesion_id
        self.inmueble_id = inmueble_id
        self.huesped_id = huesped_id
        self.reporte_id = reporte_id
        self.artefacto_id = artefacto_id
        self.sintoma_id = sintoma_id
        self.servicio_id = servicio_id

        self.causas_evaluadas: List[str] = []
        self.causas_descartadas: List[str] = []
        self.pasos_realizados: List[str] = []
        self.pasos_intentados: int = 0
        self.consecutivos_no_puedo: int = 0
        self.paso_actual_id: Optional[str] = None
        self.causa_actual_id: Optional[str] = None
        self.estado: str = 'en_curso'
        self.diagnostico_final: Optional[DiagnosticoFinal] = None

class ModuloM2Diagnostico:
    def __init__(self):
        self.db = db_client
        self.llm = gemini_client
        self.sesiones: Dict[str, SesionDiagnostico] = {}

    def iniciar_diagnostico(
        self,
        reporte: ReporteEstructurado
    ) -> Tuple[str, Optional[InstruccionEstructurada], Optional[DiagnosticoFinal], Dict[str, Any]]:
        """
        Inicia una sesión de diagnóstico a partir del ReporteEstructurado de M1.
        Retorna: (tipo_evento, instruccion, diagnostico_final, trazabilidad)
        """
        sesion_id = f"ses_{reporte.inmueble_id}_{uuid.uuid4().hex[:6]}"
        
        # Obtener servicio asociado al artefacto
        if reporte.sintoma_id == 'disparo_repetido_disyuntor' or reporte.artefacto_id == 'tab01':
            servicio_id = 'electricidad'
        elif reporte.sintoma_id == 'sin_suministro_agua_potable' or reporte.artefacto_id == 'red_agua':
            servicio_id = 'agua_potable'
        else:
            artefacto_info = self.db.artefactos.get(reporte.artefacto_id, {})
            servicio_id = artefacto_info.get('servicio', 'agua_caliente')

        sesion = SesionDiagnostico(
            sesion_id=sesion_id,
            inmueble_id=reporte.inmueble_id,
            huesped_id=reporte.huesped_id,
            reporte_id=reporte.reporte_id,
            artefacto_id=reporte.artefacto_id,
            sintoma_id=reporte.sintoma_id,
            servicio_id=servicio_id
        )
        self.sesiones[sesion_id] = sesion

        # 1. Regla I1, R1, S1: Si es señal de alarma o fuga de gas, abortar inmediatamente con seguridad
        if reporte.senal_seguridad or reporte.sintoma_id == 'olor_a_gas':
            sesion.estado = 'abortada_seguridad'
            diag_final = DiagnosticoFinal(
                diagnostico_id=f"diag_{sesion_id}",
                sesion_id=sesion_id,
                inmueble_id=reporte.inmueble_id,
                artefacto_id=reporte.artefacto_id,
                servicio_id=servicio_id,
                causa_diagnosticada='fuga_de_gas_potencial',
                resoluble_por_huesped=False,
                riesgo_seguridad=True,
                pasos_realizados=[],
                estado_cierre='abortada_seguridad'
            )
            sesion.diagnostico_final = diag_final
            return 'emergencia', None, diag_final, {
                'motivo': 'Alarma de seguridad crítica (R1/S1)',
                'causa': 'fuga_de_gas_potencial'
            }

        # 1b. Regla R9: Disparo repetido de disyuntor / llave térmica en TableroEléctrico
        if reporte.sintoma_id == 'disparo_repetido_disyuntor' or reporte.artefacto_id == 'tab01':
            return self._escalar_anfitrion(
                sesion,
                motivo="Disparo repetido de protección diferencial/térmica en Tablero Eléctrico. Prohibido rearmar nuevamente por riesgo eléctrico (Regla R9)",
                causa_final="fuga_electrica_o_cortocircuito"
            )

        # 1c. Regla R10: Causa común en servicio compartido / suministro general
        if reporte.sintoma_id == 'sin_suministro_agua_potable' or reporte.artefacto_id == 'red_agua':
            return self._escalar_anfitrion(
                sesion,
                motivo="Afectación de suministro general compartido (agua potable). No resoluble dentro de la unidad (Regla R10)",
                causa_final="corte_suministro_general_compartido"
            )

        # 2. Obtener causas y pasos compatibles con el artefacto y síntoma (Regla R6)
        return self._proponer_siguiente_paso(sesion, evidencia_acumulada=0.55)

    def procesar_respuesta_paso(
        self,
        sesion_id: str,
        paso_id: str,
        resultado: str,
        detalle: Optional[str] = None
    ) -> Tuple[str, Optional[InstruccionEstructurada], Optional[DiagnosticoFinal], Dict[str, Any]]:
        """
        Procesa la respuesta del huésped ante una instrucción técnica:
        - 'si': Problema resuelto (Regla R3)
        - 'no': Causa descartada, acumular evidencia (Regla R11)
        - 'no_puedo' / 'no_se': Dificultad del huésped; 2 consecutivos disparan escalada (Regla R8)
        """
        sesion = self.sesiones.get(sesion_id)
        if not sesion:
            raise ValueError(f"Sesión no encontrada: {sesion_id}")

        if paso_id not in sesion.pasos_realizados:
            sesion.pasos_realizados.append(paso_id)
        sesion.pasos_intentados += 1

        # ----------------------------------------------------------------------
        # Caso A: Éxito confirmado por el huésped (Regla R3)
        # ----------------------------------------------------------------------
        if resultado == 'si':
            sesion.estado = 'resuelta_por_huesped'
            sesion.consecutivos_no_puedo = 0
            causa_resuelta = sesion.causa_actual_id or 'piloto_apagado'

            diag_final = DiagnosticoFinal(
                diagnostico_id=f"diag_{sesion_id}",
                sesion_id=sesion_id,
                inmueble_id=sesion.inmueble_id,
                artefacto_id=sesion.artefacto_id,
                servicio_id=sesion.servicio_id,
                causa_diagnosticada=causa_resuelta,
                resoluble_por_huesped=True,
                riesgo_seguridad=False,
                pasos_realizados=sesion.pasos_realizados,
                estado_cierre='resuelta_por_huesped'
            )
            sesion.diagnostico_final = diag_final

            # Mensaje amigable de cierre
            cierre_msg = "¡Excelente noticia! Me alegra que el inconveniente haya quedado solucionado. Por favor no dudes en escribirme si necesitas algo más durante tu estadía."
            instruccion = InstruccionEstructurada(
                sesion_id=sesion_id,
                tipo='cierre',
                paso_id=paso_id,
                instruccion_huesped=cierre_msg,
                riesgo_usuario='bajo',
                advertencias=[],
                justificacion='Incidencia resuelta satisfactoriamente por el huésped (Regla R3)',
                pasos_intentados=sesion.pasos_intentados,
                texto_verbalizado_llm=cierre_msg
            )
            return 'cierre_exitoso', instruccion, diag_final, {
                'regla_aplicada': 'R3_cierre_exitoso',
                'causa_resuelta': causa_resuelta,
                'pasos_totales': len(sesion.pasos_realizados)
            }

        # ----------------------------------------------------------------------
        # Caso B: No puedo / No sé (Regla R8)
        # ----------------------------------------------------------------------
        if resultado in ['no_puedo', 'no_se']:
            sesion.consecutivos_no_puedo += 1
            if sesion.consecutivos_no_puedo >= 2:
                # Regla R8: 2 rechazos o impedimentos consecutivos -> Escalar de inmediato
                return self._escalar_anfitrion(
                    sesion,
                    motivo="El huésped indicó impedimento técnico en dos pasos consecutivos (Regla R8)"
                )

        else:
            sesion.consecutivos_no_puedo = 0

        # ----------------------------------------------------------------------
        # Caso C: No funcionó (Regla R11: Descartar hipótesis y acumular evidencia)
        # ----------------------------------------------------------------------
        # Regla R9: Si al intentar rearmar la llave térmica (p6) vuelve a saltar inmediatamente
        if paso_id == 'p6' and detalle and any(w in detalle.lower() for w in ['salta', 'dispara', 'corta', 'chispazo']):
            return self._escalar_anfitrion(
                sesion,
                motivo="La protección térmica/diferencial volvió a dispararse tras el rearme. Prohibido insistir (Regla R9)",
                causa_final="fuga_electrica_o_cortocircuito"
            )

        if sesion.causa_actual_id and sesion.causa_actual_id not in sesion.causas_descartadas:
            sesion.causas_descartadas.append(sesion.causa_actual_id)

        # Regla R8: Límite de presupuesto de 4 pasos
        if sesion.pasos_intentados >= 4:
            return self._escalar_anfitrion(
                sesion,
                motivo="Se alcanzó el límite presupuestario máximo de 4 pasos de verificación asistida (Regla R8)"
            )

        # Buscar el siguiente paso con evidencia acumulada incrementada (0.85 para turno 2)
        evidencia_acumulada = 0.85 if len(sesion.causas_descartadas) == 1 else 0.95
        return self._proponer_siguiente_paso(sesion, evidencia_acumulada)

    def _proponer_siguiente_paso(
        self,
        sesion: SesionDiagnostico,
        evidencia_acumulada: float
    ) -> Tuple[str, Optional[InstruccionEstructurada], Optional[DiagnosticoFinal], Dict[str, Any]]:
        """
        Selecciona y evalúa la mejor hipótesis/paso disponible mediante M2 Mamdani.
        """
        # Consultar conocimiento estructural (C1)
        candidatos = self.db.inferir_paso_diagnostico(sesion.artefacto_id, sesion.sintoma_id)

        # Filtrar candidatos ya descartados
        candidatos_restantes = [
            c for c in candidatos
            if c.get('causa') not in sesion.causas_descartadas
        ]

        # Si no quedan hipótesis delegables al huésped
        candidatos_delegables = [
            c for c in candidatos_restantes
            if c.get('paso') is not None
        ]

        if not candidatos_delegables:
            # Identificar la causa raíz más probable no delegable (ej: falla_termocupla, gas_refrigerante_bajo, etc.)
            causa_no_delegable = candidatos_restantes[0].get('causa') if candidatos_restantes else 'falla_interna_no_delegable'
            return self._escalar_anfitrion(
                sesion,
                motivo=f"No restan pasos delegables al huésped. Causa probable: {causa_no_delegable} (Regla R2)",
                causa_final=causa_no_delegable
            )

        # Priorizar hipótesis con M2 Mamdani
        mejores_hipotesis = []
        for cand in candidatos_delegables:
            frec_val = cand.get('indice_frecuencia', 0.70)
            ries_val = cand.get('riesgo_esfuerzo', 2.0) or 2.0
            
            inputs_m2 = {
                'FrecuenciaCausa': frec_val,
                'RiesgoEsfuerzoPaso': ries_val,
                'EvidenciaAcumulada': evidencia_acumulada
            }
            centroide_m2, alfa_max, estado_cob, reglas_act = inferencia_mamdani('M2', inputs_m2)
            mejores_hipotesis.append({
                'cand': cand,
                'prioridad_difusa': centroide_m2,
                'alfa_max': alfa_max,
                'estado_cobertura': estado_cob,
                'reglas_activadas': reglas_act,
                'inputs': inputs_m2
            })

        # Ordenar por mayor prioridad difusa
        mejores_hipotesis.sort(key=lambda h: h['prioridad_difusa'], reverse=True)
        elegida = mejores_hipotesis[0]
        cand_elegido = elegida['cand']

        # Ejecutar consulta C2 en Neo4j para dejar traza en vivo de la fuzzificación de M2
        self.db.evaluar_fuzzificacion_cypher(elegida['inputs'], modulo="M2")

        sesion.causa_actual_id = cand_elegido['causa']
        sesion.paso_actual_id = cand_elegido['paso']

        # Regla R7: Advertencias técnicas
        paso_info = self.db.pasos.get(cand_elegido['paso'], {})
        advertencias = paso_info.get('advertencias', [])

        # Verbalización con Gemini (Regla I10: Fidelidad estricta al payload del grafo)
        payload_llm = {
            'instruccion': cand_elegido['instruccion'],
            'advertencias': advertencias,
            'artefacto': self.db.artefactos.get(sesion.artefacto_id, {}).get('marca', 'artefacto'),
            'riesgo': cand_elegido['riesgo']
        }
        texto_verbalizado = self.llm.verbalize_step_instruction(payload_llm)

        instruccion = InstruccionEstructurada(
            sesion_id=sesion.sesion_id,
            tipo='paso',
            paso_id=cand_elegido['paso'],
            instruccion_huesped=cand_elegido['instruccion'],
            riesgo_usuario=cand_elegido['riesgo'],
            advertencias=advertencias,
            justificacion=f"Causa {cand_elegido['causa']} evaluada con prioridad {elegida['prioridad_difusa']:.1f}",
            prioridad_difusa=elegida['prioridad_difusa'],
            pasos_intentados=sesion.pasos_intentados,
            texto_verbalizado_llm=texto_verbalizado
        )

        return 'instruccion_paso', instruccion, None, {
            'paso_id': cand_elegido['paso'],
            'causa_evaluada': cand_elegido['causa'],
            'prioridad_difusa': elegida['prioridad_difusa'],
            'alfa_max': elegida['alfa_max'],
            'reglas_activadas': elegida['reglas_activadas'],
            'inputs_difusos': elegida['inputs'],
            'texto_verbalizado': texto_verbalizado
        }

    def _escalar_anfitrion(
        self,
        sesion: SesionDiagnostico,
        motivo: str,
        causa_final: Optional[str] = None
    ) -> Tuple[str, Optional[InstruccionEstructurada], Optional[DiagnosticoFinal], Dict[str, Any]]:
        """
        Escala la incidencia hacia el submódulo M3 y genera DiagnósticoFinal.
        """
        sesion.estado = 'escalada'
        causa_diag = causa_final or sesion.causa_actual_id or 'falla_compleja'

        # Si el síntoma es cerradura electrónica trabada
        if sesion.artefacto_id == 'cer01' and 'mecanismo_trabado' in self.db.sintomas.get(sesion.sintoma_id, {}).get('causas', []):
            causa_diag = 'mecanismo_trabado'

        diag_final = DiagnosticoFinal(
            diagnostico_id=f"diag_{sesion.sesion_id}",
            sesion_id=sesion.sesion_id,
            inmueble_id=sesion.inmueble_id,
            artefacto_id=sesion.artefacto_id,
            servicio_id=sesion.servicio_id,
            causa_diagnosticada=causa_diag,
            resoluble_por_huesped=False,
            riesgo_seguridad=False,
            pasos_realizados=sesion.pasos_realizados,
            estado_cierre='escalada'
        )
        sesion.diagnostico_final = diag_final

        mensaje_huesped = (
            "Comprendo la situación. Para garantizar tu seguridad y la correcta resolución del problema, "
            "he notificado de inmediato al anfitrión para coordinar la asistencia correspondiente. Te mantendremos informado."
        )

        instruccion = InstruccionEstructurada(
            sesion_id=sesion.sesion_id,
            tipo='escalada',
            instruccion_huesped=mensaje_huesped,
            riesgo_usuario='alto',
            advertencias=["Intervención técnica especializada requerida"],
            justificacion=motivo,
            pasos_intentados=sesion.pasos_intentados,
            texto_verbalizado_llm=mensaje_huesped
        )

        return 'escalada_anfitrion', instruccion, diag_final, {
            'motivo_escalada': motivo,
            'causa_diagnosticada': causa_diag,
            'pasos_realizados': sesion.pasos_realizados
        }

# Instancia global
modulo_m2 = ModuloM2Diagnostico()
