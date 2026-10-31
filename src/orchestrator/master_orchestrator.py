"""
src/orchestrator/master_orchestrator.py - Orquestador Maestro PG3 (Grupal)
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026

Coordina el ciclo de vida completo de la atención al huésped:
1. M1 (Ignacio Canzio): Interpretación, desambiguación y suficiencia.
2. M2 (Nicolás López): Diagnóstico, descarte y resolución técnica asistida.
3. M3 (Bruno Montero): Triage difuso, severidad contextual y ficha para el anfitrión.
"""

from typing import Dict, Any, Optional, List
from src.models.schemas import (
    GuestMessageRequest,
    StepResponseRequest,
    ClarificationResponseRequest,
    InteractionResponse,
    ReporteEstructurado,
    DiagnosticoFinal,
    ContextoIncidenciaInput,
    FichaIncidencia
)
from src.modules.m1_interpretacion import modulo_m1
from src.modules.m2_diagnostico import modulo_m2
from src.modules.m3_severidad import modulo_m3
from src.db.neo4j_client import db_client

class MasterOrchestrator:
    def __init__(self):
        self.db = db_client
        self.m1 = modulo_m1
        self.m2 = modulo_m2
        self.m3 = modulo_m3
        self.sesiones_activas: Dict[str, Dict[str, Any]] = {}
        self.incidencias_registradas: Dict[str, FichaIncidencia] = {}

    def _contar_incidencias_activas_inmueble(self, inmueble_id: str) -> int:
        """Cuenta cuántas incidencias activas/escaladas tiene actualmente el mismo inmueble (Regla S4)."""
        return sum(
            1 for f in self.incidencias_registradas.values()
            if f.inmueble_id == inmueble_id and f.estado == 'escalada'
        )

    def procesar_mensaje_huesped(self, req: GuestMessageRequest) -> InteractionResponse:
        """
        Punto de entrada principal para mensajes iniciales o continuaciones de conversación.
        """
        self.db.clear_traces()

        # Extraer contexto si fue suministrado en el request
        contexto = None
        if req.temperatura_actual is not None or req.horas_restantes is not None:
            contexto = ContextoIncidenciaInput(
                temperatura_actual=req.temperatura_actual if req.temperatura_actual is not None else 24.0,
                horas_restantes=req.horas_restantes if req.horas_restantes is not None else 24.0,
                dato_estimado=False
            )

        # ----------------------------------------------------------------------
        # PASO 1: Submódulo M1 - Interpretación semántica y suficiencia
        # ----------------------------------------------------------------------
        tipo_ev_m1, reporte, eval_m1, extra_m1 = self.m1.procesar_relato(
            relato=req.mensaje,
            inmueble_id=req.inmueble_id,
            huesped_id=req.huesped_id
        )

        # Regla I12: Reserva inactiva
        if tipo_ev_m1 == 'reserva_inactiva':
            return InteractionResponse(
                tipo_evento='reserva_inactiva',
                mensaje_para_huesped=extra_m1['mensaje'],
                trazabilidad_diagnostica={'m1': extra_m1},
                cypher_traces=self.db.get_traces()
            )

        # Regla I8: Artefacto inexistente en la unidad
        if tipo_ev_m1 == 'artefacto_inexistente':
            return InteractionResponse(
                tipo_evento='artefacto_inexistente',
                mensaje_para_huesped=extra_m1['mensaje'],
                trazabilidad_diagnostica={'m1': extra_m1},
                cypher_traces=self.db.get_traces()
            )

        # Regla I13: Mensaje fuera de dominio
        if tipo_ev_m1 == 'fuera_de_dominio':
            return InteractionResponse(
                tipo_evento='fuera_de_dominio',
                mensaje_para_huesped=extra_m1['mensaje'],
                trazabilidad_diagnostica={'m1': extra_m1},
                cypher_traces=self.db.get_traces()
            )

        # Regla I14: Consulta sobre capacidades o bienvenida
        if tipo_ev_m1 == 'consulta_capacidades':
            return InteractionResponse(
                tipo_evento='consulta_capacidades',
                mensaje_para_huesped=extra_m1['mensaje'],
                trazabilidad_diagnostica={'m1': extra_m1},
                cypher_traces=self.db.get_traces()
            )

        # Regla I4, I6: Pregunta aclaratoria por ambigüedad
        if tipo_ev_m1 == 'pregunta_aclaratoria':
            sesion_temp_id = f"clarif_{req.inmueble_id}"
            self.sesiones_activas[sesion_temp_id] = {
                'inmueble_id': req.inmueble_id,
                'huesped_id': req.huesped_id,
                'relato_original': req.mensaje,
                'ronda': 1,
                'contexto': contexto
            }
            return InteractionResponse(
                tipo_evento='pregunta_aclaratoria',
                mensaje_para_huesped=extra_m1['mensaje'],
                sesion_id=sesion_temp_id,
                trazabilidad_diagnostica={
                    'm1_evaluacion': eval_m1.model_dump() if eval_m1 else {},
                    'opciones': extra_m1.get('opciones', [])
                },
                cypher_traces=self.db.get_traces()
            )

        # Reglas I1, R1, S1: Detección crítica de seguridad (Olor a gas / chispa / humo)
        if tipo_ev_m1 == 'emergencia':
            # M2 procesa el aborto por seguridad
            _, _, diag_seg, extra_m2 = self.m2.iniciar_diagnostico(reporte)
            # M3 asigna Nivel 5 determinístico
            ficha_seg = self.m3.evaluar_severidad(diag_seg, contexto)
            self.incidencias_registradas[ficha_seg.incidencia_id] = ficha_seg

            return InteractionResponse(
                tipo_evento='emergencia',
                mensaje_para_huesped=extra_m1['mensaje'],
                advertencias=["¡EVACÚE Y VENTILE DE INMEDIATO! NO ACCIONE INTERRUPTORES ELÉCTRICOS."],
                sesion_id=diag_seg.sesion_id,
                reporte_id=reporte.reporte_id,
                incidencia_id=ficha_seg.incidencia_id,
                ficha_incidencia=ficha_seg,
                trazabilidad_diagnostica={
                    'm1_alarma': extra_m1,
                    'm2_seguridad': extra_m2,
                    'm3_ficha': ficha_seg.model_dump()
                },
                cypher_traces=self.db.get_traces()
            )

        # ----------------------------------------------------------------------
        # PASO 2: Submódulo M2 - Diagnóstico técnico y troubleshooting
        # ----------------------------------------------------------------------
        ev_m2, instruccion_m2, diag_m2, extra_m2 = self.m2.iniciar_diagnostico(reporte)

        # Guardar sesión activa
        ses_id = instruccion_m2.sesion_id if instruccion_m2 else (diag_m2.sesion_id if diag_m2 else "ses_unk")
        self.sesiones_activas[ses_id] = {
            'inmueble_id': req.inmueble_id,
            'huesped_id': req.huesped_id,
            'reporte': reporte,
            'contexto': contexto
        }

        # Si M2 propone un paso de verificación al huésped
        if ev_m2 == 'instruccion_paso' and instruccion_m2:
            advs = list(instruccion_m2.advertencias)
            if extra_m1.get('nota_preventiva_i2'):
                advs.insert(0, extra_m1['nota_preventiva_i2'])

            return InteractionResponse(
                tipo_evento='instruccion_paso',
                mensaje_para_huesped=instruccion_m2.texto_verbalizado_llm or instruccion_m2.instruccion_huesped,
                advertencias=advs,
                sesion_id=ses_id,
                paso_id=instruccion_m2.paso_id,
                reporte_id=reporte.reporte_id,
                trazabilidad_diagnostica={
                    'm1_evaluacion': eval_m1.model_dump() if eval_m1 else {},
                    'm1_extra': extra_m1,
                    'm2_priorizacion': extra_m2
                },
                cypher_traces=self.db.get_traces()
            )

        # Si M2 escaló directamente (ej: causa no delegable según R2, R9 o R10)
        if ev_m2 == 'escalada_anfitrion' and diag_m2:
            activas_previas = self._contar_incidencias_activas_inmueble(diag_m2.inmueble_id)
            ficha = self.m3.evaluar_severidad(diag_m2, contexto, incidencias_activas_inmueble=activas_previas)
            self.incidencias_registradas[ficha.incidencia_id] = ficha

            return InteractionResponse(
                tipo_evento='escalada_anfitrion',
                mensaje_para_huesped=instruccion_m2.instruccion_huesped if instruccion_m2 else "Incidencia escalada a asistencia técnica.",
                advertencias=instruccion_m2.advertencias if instruccion_m2 else [],
                sesion_id=ses_id,
                reporte_id=reporte.reporte_id,
                incidencia_id=ficha.incidencia_id,
                ficha_incidencia=ficha,
                trazabilidad_diagnostica={
                    'm1': extra_m1,
                    'm2': extra_m2,
                    'm3': ficha.model_dump()
                },
                cypher_traces=self.db.get_traces()
            )

        return InteractionResponse(
            tipo_evento='fuera_de_dominio',
            mensaje_para_huesped="No se pudo procesar la solicitud con certeza.",
            trazabilidad_diagnostica={'raw_m2': extra_m2},
            cypher_traces=self.db.get_traces()
        )

    def procesar_respuesta_paso(self, req: StepResponseRequest) -> InteractionResponse:
        """
        Procesa la respuesta del huésped a un paso técnico (sí / no / no puedo).
        """
        self.db.clear_traces()
        ses_info = self.sesiones_activas.get(req.sesion_id, {})
        contexto = ses_info.get('contexto')

        ev_m2, instruccion_m2, diag_m2, extra_m2 = self.m2.procesar_respuesta_paso(
            sesion_id=req.sesion_id,
            paso_id=req.paso_id,
            resultado=req.resultado,
            detalle=req.detalle
        )

        # Caso 1: Próximo paso técnico propuesto por M2
        if ev_m2 == 'instruccion_paso' and instruccion_m2:
            return InteractionResponse(
                tipo_evento='instruccion_paso',
                mensaje_para_huesped=instruccion_m2.texto_verbalizado_llm or instruccion_m2.instruccion_huesped,
                advertencias=instruccion_m2.advertencias,
                sesion_id=req.sesion_id,
                paso_id=instruccion_m2.paso_id,
                trazabilidad_diagnostica={'m2_paso_siguiente': extra_m2},
                cypher_traces=self.db.get_traces()
            )

        # Caso 2: Cierre exitoso resuelto por huésped (Regla R3 -> S2)
        if ev_m2 == 'cierre_exitoso' and diag_m2:
            ficha = self.m3.evaluar_severidad(diag_m2, contexto)
            self.incidencias_registradas[ficha.incidencia_id] = ficha

            return InteractionResponse(
                tipo_evento='cierre_exitoso',
                mensaje_para_huesped=instruccion_m2.instruccion_huesped if instruccion_m2 else "¡Problema resuelto exitosamente!",
                sesion_id=req.sesion_id,
                paso_id=req.paso_id,
                incidencia_id=ficha.incidencia_id,
                ficha_incidencia=ficha,
                trazabilidad_diagnostica={'m2_cierre': extra_m2, 'm3_s2': ficha.model_dump()},
                cypher_traces=self.db.get_traces()
            )

        # Caso 3: Escalada al anfitrión (Reglas R8, R2, R4, R9, R10, R11 agotada)
        if ev_m2 == 'escalada_anfitrion' and diag_m2:
            activas_previas = self._contar_incidencias_activas_inmueble(diag_m2.inmueble_id)
            ficha = self.m3.evaluar_severidad(diag_m2, contexto, incidencias_activas_inmueble=activas_previas)
            self.incidencias_registradas[ficha.incidencia_id] = ficha

            return InteractionResponse(
                tipo_evento='escalada_anfitrion',
                mensaje_para_huesped=instruccion_m2.instruccion_huesped if instruccion_m2 else "Hemos derivado tu caso al anfitrión.",
                advertencias=instruccion_m2.advertencias if instruccion_m2 else [],
                sesion_id=req.sesion_id,
                paso_id=req.paso_id,
                incidencia_id=ficha.incidencia_id,
                ficha_incidencia=ficha,
                trazabilidad_diagnostica={'m2_escalada': extra_m2, 'm3_triage': ficha.model_dump()},
                cypher_traces=self.db.get_traces()
            )

        return InteractionResponse(
            tipo_evento='fuera_de_dominio',
            mensaje_para_huesped="Estado no reconocido en el flujo de pasos.",
            cypher_traces=self.db.get_traces()
        )

    def procesar_respuesta_aclaracion(self, req: ClarificationResponseRequest) -> InteractionResponse:
        """
        Procesa la respuesta a una pregunta aclaratoria de M1 (ej. elección entre termotanque eléctrico o gas).
        """
        ses_key = f"clarif_{req.inmueble_id}"
        ses_info = self.sesiones_activas.get(ses_key, {})
        relato_original = ses_info.get('relato_original', '')
        relato_combinado = f"{relato_original}. El problema específico es con: {req.respuesta}"

        # Reenviar a flujo normal
        msg_req = GuestMessageRequest(
            inmueble_id=req.inmueble_id,
            huesped_id=req.huesped_id,
            mensaje=relato_combinado
        )
        return self.procesar_mensaje_huesped(msg_req)

    def listar_incidencias(self) -> List[Dict[str, Any]]:
        """Retorna todas las incidencias registradas en la sesión."""
        # Unir incidencias en memoria con el catálogo base de Neo4j
        res = [ficha.model_dump() for ficha in self.incidencias_registradas.values()]
        return res

    def obtener_traza_incidencia(self, incidencia_id: str) -> Dict[str, Any]:
        """Obtiene la traza completa de una incidencia para el inspector gráfico."""
        ficha = self.incidencias_registradas.get(incidencia_id)
        if ficha:
            return {
                'ficha': ficha.model_dump(),
                'sesion_m2': self.m2.sesiones.get(ficha.incidencia_id.replace('inc_', '')).__dict__ if ficha.incidencia_id.replace('inc_', '') in self.m2.sesiones else {},
                'grafo_db': self.db.get_traza(incidencia_id)
            }
        return {'error': 'Incidencia no encontrada'}

# Instancia global
master_orchestrator = MasterOrchestrator()
