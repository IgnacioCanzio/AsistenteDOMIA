"""
src/modules/m1_interpretacion.py - Submódulo M1: Interpretación Semántica y Diálogo
Responsable de diseño: Ignacio Canzio
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

from typing import Dict, Any, Optional, Tuple
from src.models.schemas import ReporteEstructurado, EvaluacionM1
from src.db.neo4j_client import db_client
from src.llm.gemini_client import gemini_client
from src.llm.prompts import I11_PLANTILLA_EMERGENCIA_FIJA
from pg2_neo4j.verificacion.ref_difuso import inferencia_mamdani

class ModuloM1Interpretacion:
    def __init__(self):
        self.db = db_client
        self.llm = gemini_client

    def procesar_relato(
        self,
        relato: str,
        inmueble_id: str = "inm101",
        huesped_id: str = "h1",
        ronda: int = 1
    ) -> Tuple[str, Optional[ReporteEstructurado], Optional[EvaluacionM1], Dict[str, Any]]:
        """
        Procesa el relato del huésped siguiendo el patrón Sandwich de PI4:
        0. Validación de contexto de reserva e inmueble en Neo4j (I8, I12)
        1. Extracción con Gemini / Determinístico (I1, I2, I13, I14)
        2. Evaluación de Suficiencia Difusa Mamdani (C2, C3)
        3. Decisión estructural: Reporte, Pregunta Aclaratoria, Artefacto Inexistente o Emergencia
        """
        # 0. Consulta Cypher de contexto del inmueble y reserva activa (I8 / I12)
        info_inmueble = self.db.verificar_contexto_inmueble(inmueble_id, huesped_id)
        artefactos_inmueble = info_inmueble.get('artefactos', []) or self.db.inmuebles.get(inmueble_id, {}).get('artefactos', [])

        # Regla I12: Verificación de reserva activa antes de abrir sesión diagnóstica
        if not info_inmueble.get('reserva_activa', True):
            msg_i12 = (
                "No registramos una reserva activa asociada a tu usuario para esta unidad en el momento actual (Regla I12). "
                "Por favor comunícate con la recepción o con el anfitrión para habilitar el soporte técnico."
            )
            return 'reserva_inactiva', None, None, {
                'regla_aplicada': 'I12_reserva_inactiva',
                'inmueble_id': inmueble_id,
                'huesped_id': huesped_id,
                'mensaje': msg_i12
            }

        # 1. Extracción de intención
        extraccion = self.llm.extract_incident_intent(relato, info_inmueble)

        # Regla I13: Mensaje fuera de dominio
        if extraccion.get('fuera_de_dominio', False):
            msg = "Hola. Como asistente de conserjería estoy a tu disposición para resolver incidencias técnicas o dudas sobre el equipamiento del departamento. Para recomendaciones turísticas o consultas generales, te sugiero comunicarte con el anfitrión."
            return 'fuera_de_dominio', None, None, {'regla_aplicada': 'I13_fuera_de_dominio', 'mensaje': msg, 'extraccion': extraccion}

        # Detección de consulta sobre capacidades / bienvenida / ayuda general (Regla I14)
        if extraccion.get('es_consulta_capacidades', False):
            nombres_artefactos = [
                f"{a} ({self.db.artefactos.get(a, {}).get('tipo', 'Artefacto')} {self.db.artefactos.get(a, {}).get('marca', '')})".strip()
                for a in artefactos_inmueble
            ]
            equip_str = "\n".join(f"• {art}" for art in nombres_artefactos) if nombres_artefactos else "• Equipamiento general"
            msg_cap = (
                f"¡Hola! Soy DOMIA, tu asistente virtual de conserjería para {info_inmueble.get('nombre', 'tu departamento')}.\n\n"
                f"Puedo asistirte en el autodiagnóstico técnico y resolución paso a paso del equipamiento de tu unidad:\n"
                f"{equip_str}\n\n"
                f"Te puedo guiar con problemas como:\n"
                f"• Temperatura del agua o encendido del termotanque\n"
                f"• Bloqueo o código de la cerradura electrónica\n"
                f"• Funcionamiento o limpieza del aire acondicionado (Split)\n"
                f"• Verificación segura de llaves térmicas y disyuntor\n\n"
                f"¿En qué te puedo ayudar hoy? Contame qué sucede y lo resolvemos."
            )
            return 'consulta_capacidades', None, None, {
                'regla_aplicada': 'I14_consulta_capacidades',
                'mensaje': msg_cap,
                'artefactos_inmueble': artefactos_inmueble
            }

        # Regla I1, R1, S1, I11: Barrera Determinística de Seguridad
        if extraccion.get('es_alarma', False):
            # Ejecutar consulta Cypher C1b en vivo para trazabilidad
            traza_c1b = self.db.check_seguridad("rep6")
            reporte_seg = ReporteEstructurado(
                reporte_id="rep6",
                inmueble_id=inmueble_id,
                huesped_id=huesped_id,
                reserva_id=info_inmueble.get('reserva_id'),
                artefacto_id=extraccion.get('artefacto_mencionado') or (artefactos_inmueble[0] if artefactos_inmueble else "tg01"),
                sintoma_id="olor_a_gas",
                senal_seguridad=True,
                termino_alarma=extraccion.get('termino_alarma'),
                suficiencia_puntaje=100.0,
                estado="emitido_alerta"
            )
            return 'emergencia', reporte_seg, None, {
                'regla_aplicada': 'I1_R1_S1_I11',
                'mensaje': I11_PLANTILLA_EMERGENCIA_FIJA,
                'alerta': True,
                'protocolo_id': 'pe1',
                'verificacion_c1b': traza_c1b
            }

        sintoma_id = extraccion.get('sintoma_identificado')
        artefacto_id = extraccion.get('artefacto_mencionado')
        alarma_negada = extraccion.get('alarma_negada', False)
        termino_negado = extraccion.get('termino_alarma')

        # Si no se identificó ningún síntoma o falla técnica concreta (Regla I4)
        if not sintoma_id:
            msg_indet = (
                f"No pude identificar con certeza qué inconveniente estás experimentando.\n"
                f"Por favor indicame con qué artefacto o servicio necesitas asistencia "
                f"(por ejemplo: agua caliente, cerradura electrónica, aire acondicionado o suministro eléctrico) "
                f"para que pueda ayudarte paso a paso."
            )
            return 'pregunta_aclaratoria', None, None, {
                'regla_aplicada': 'I4_sintoma_no_identificado',
                'mensaje': msg_indet,
                'opciones': [
                    'Agua caliente',
                    'Cerradura electrónica',
                    'Aire acondicionado / Split',
                    'Suministro eléctrico'
                ]
            }

        # Detección de candidatos compatibles en el inmueble según el síntoma
        candidatos_posibles = []
        if sintoma_id == 'sin_agua_caliente':
            candidatos_posibles = [a for a in artefactos_inmueble if a in ['tg01', 'tg02', 'tg03', 'te01']]
        elif sintoma_id == 'teclado_sin_respuesta':
            candidatos_posibles = [a for a in artefactos_inmueble if a == 'cer01']
        elif sintoma_id == 'no_enfria':
            candidatos_posibles = [a for a in artefactos_inmueble if a == 'spl01']
        elif sintoma_id in ('disparo_repetido_disyuntor', 'sin_suministro_agua_potable'):
            # Infraestructura general de la unidad/edificio para Reglas R9 y R10
            candidatos_posibles = [artefacto_id]

        # Regla I8: Validación de existencia del artefacto en el departamento
        if artefacto_id and artefacto_id not in ('tab01', 'red_agua'):
            if not candidatos_posibles and artefacto_id not in artefactos_inmueble:
                mencion = extraccion.get('mencion_artefacto_texto') or artefacto_id
                nombres_disp = [
                    f"{a} ({self.db.artefactos.get(a, {}).get('tipo', 'Artefacto')} {self.db.artefactos.get(a, {}).get('marca', '')})".strip()
                    for a in artefactos_inmueble
                ]
                msg_i8 = (
                    f"Te informo que la unidad {info_inmueble.get('nombre', inmueble_id)} no cuenta con «{mencion}» "
                    f"dentro de su equipamiento registrado (Regla I8). "
                    f"Los artefactos instalados en tu departamento son: {', '.join(nombres_disp) if nombres_disp else 'ninguno'}."
                )
                return 'artefacto_inexistente', None, None, {
                    'regla_aplicada': 'I8_artefacto_inexistente',
                    'artefacto_solicitado': mencion,
                    'artefactos_instalados': artefactos_inmueble,
                    'mensaje': msg_i8
                }

        # Cálculo de variables difusas de entrada para M1
        conf_extr = float(extraccion.get('confianza_extraccion', 0.8))
        coinc_lex = 0.92 if (sintoma_id in self.db.sintomas or sintoma_id in ('disparo_repetido_disyuntor', 'sin_suministro_agua_potable')) else 0.40

        if len(candidatos_posibles) > 1 and not ('baño' in relato.lower() or 'cocina' in relato.lower() or 'electrico' in relato.lower() or 'eléctrico' in relato.lower()):
            # Caso 3: Ambigüedad con distancia pequeña entre candidatos
            dist_cand = 0.35
            conf_extr = 0.72
            coinc_lex = 0.68
            es_ambiguo = True
        else:
            dist_cand = 0.85
            es_ambiguo = False

        # Inferencia Mamdani de M1 (Suficiencia de la Interpretación)
        inputs_m1 = {
            'ConfianzaExtraccion': conf_extr,
            'CoincidenciaLexica': coinc_lex,
            'DistanciaCandidatos': dist_cand
        }
        # Ejecutar fuzzificación Cypher C2 para trazabilidad en vivo
        self.db.evaluar_fuzzificacion_cypher(inputs_m1, modulo="M1")
        centroide, alfa_max, estado_cobertura, reglas_act = inferencia_mamdani('M1', inputs_m1)

        eval_m1 = EvaluacionM1(
            evaluacion_id=f"ev_{inmueble_id}_{ronda}",
            confianza_extraccion=conf_extr,
            coincidencia_lexica=coinc_lex,
            distancia_candidatos=dist_cand,
            suficiencia_centroide=centroide,
            alfa_max=alfa_max,
            estado_cobertura=estado_cobertura,
            decision='suficiente' if centroide >= 65.0 else 'insuficiente_con_rondas',
            ronda_actual=ronda,
            max_rondas=2
        )

        # Regla I4, I6, I7: Manejo de ambigüedad y límite de rondas
        if es_ambiguo and centroide < 65.0:
            if ronda < 2:
                eval_m1.decision = 'insuficiente_con_rondas'
                eval_m1.pregunta_aclaratoria = "¿Podrías indicarme si el inconveniente es con el termotanque eléctrico del baño o con el termotanque a gas de la cocina?"
                return 'pregunta_aclaratoria', None, eval_m1, {
                    'regla_aplicada': 'I4_I6_pregunta_aclaratoria',
                    'mensaje': eval_m1.pregunta_aclaratoria,
                    'opciones': ['Termotanque eléctrico del baño', 'Termotanque a gas de la cocina'],
                    'ronda': ronda
                }
            else:
                # Regla I7: Superó límite de rondas -> escalar a anfitrión
                eval_m1.decision = 'insuficiente_escalar'
                msg = "No hemos podido determinar con certeza qué artefacto presenta la anomalía tras dos consultas. Hemos derivado tu caso al anfitrión para que se comunique contigo directamente."
                return 'escalada_anfitrion', None, eval_m1, {'regla_aplicada': 'I7_limite_rondas', 'mensaje': msg}

        # Determinación final del artefacto entre los candidatos válidos de la unidad
        if artefacto_id not in ('tab01', 'red_agua'):
            if not artefacto_id or artefacto_id not in artefactos_inmueble:
                artefacto_id = candidatos_posibles[0] if candidatos_posibles else (artefactos_inmueble[0] if artefactos_inmueble else "tg01")

        # Emisión del Reporte Estructurado hacia M2 (Regla I5)
        reporte = ReporteEstructurado(
            reporte_id=f"rep_{inmueble_id}",
            inmueble_id=inmueble_id,
            huesped_id=huesped_id,
            reserva_id=info_inmueble.get('reserva_id'),
            artefacto_id=artefacto_id,
            sintoma_id=sintoma_id,
            senal_seguridad=False,
            termino_alarma=termino_negado if alarma_negada else None,
            suficiencia_puntaje=centroide,
            estado="emitido"
        )

        # Regla I2: Si hubo alarma explícitamente negada, anexar nota preventiva
        nota_i2 = None
        if alarma_negada:
            nota_i2 = (
                f"Nota preventiva (Regla I2): Se registró que actualmente NO percibe «{termino_negado}». "
                f"Ante cualquier aparición de olor a gas, humo o chispas, detenga las pruebas de inmediato y avísenos."
            )

        return 'reporte_emitido', reporte, eval_m1, {
            'centroide_m1': centroide,
            'alfa_max': alfa_max,
            'reglas_activadas': reglas_act,
            'alarma_negada_i2': alarma_negada,
            'nota_preventiva_i2': nota_i2
        }

# Instancia global
modulo_m1 = ModuloM1Interpretacion()
