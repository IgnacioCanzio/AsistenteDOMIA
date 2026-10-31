"""
src/modules/m3_severidad.py - Submódulo M3: Severidad, Triage Difuso y Notificación al Anfitrión
Responsable de diseño: Bruno Montero
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026

Reglas implementadas:
- S2: Cierre silencioso sin notificación para incidencias resueltas por el huésped (Nivel 0 / sin_aviso).
- S1: Riesgo de seguridad impone determinísticamente Nivel 5 Emergencia sin pasar por lógica difusa.
- S5: Sensibilidad continua ante impacto climático (fórmula contextual exacta para climatización).
- S3: Política conservadora con dato estimado ante falta de telemetría/contexto.
- M3 Mamdani: Inferencia difusa (ImpactoClimatico, TiempoRestante, SensibilidadServicio).
- T1: Mapeo de puntaje difuso continuo a 5 niveles de severidad.
- R5: Piso mandatorio de nivel 4 (Alta) para servicios esenciales (acceso_principal, agua_potable).
- T2: Asignación de canales de notificación (reporte_diario, cola_priorizada, alerta_inmediata).
- Verbalización controlada con Gemini para la redacción de la ficha y aviso al anfitrión.
"""

import math
import uuid
from typing import Dict, Any, Optional
from src.models.schemas import (
    DiagnosticoFinal,
    ContextoIncidenciaInput,
    FichaIncidencia,
    ReglaActivadaInfo
)
from src.db.neo4j_client import db_client
from src.llm.gemini_client import gemini_client
from pg2_neo4j.verificacion.ref_difuso import inferencia_mamdani

class ModuloM3Severidad:
    def __init__(self):
        self.db = db_client
        self.llm = gemini_client

    def calcular_sensibilidad_servicio(self, servicio_id: str, temperatura: float) -> float:
        """
        Regla S5: Sensibilidad contextual continua para climatización.
        sensibilidad = base + 4.5 * max(mu_Alto, mu_Extremo)
        """
        serv_info = self.db.servicios.get(servicio_id, {})
        base = serv_info.get('sensibilidad_base', 5.0)

        if serv_info.get('tipo') == 'climatizacion':
            # Parámetros exactos de Marco 2 / PG2
            # ImpactoClimatico.Alto: c=33.0, s=3.6
            # ImpactoClimatico.Extremo: c=41.0, s=3.8 (hombro derecho)
            mu_alto = math.exp(-((temperatura - 33.0) ** 2) / (2.0 * (3.6 ** 2)))
            if temperatura >= 41.0:
                mu_extremo = 1.0
            else:
                mu_extremo = math.exp(-((temperatura - 41.0) ** 2) / (2.0 * (3.8 ** 2)))

            max_mu = max(mu_alto, mu_extremo)
            return round(base + (4.5 * max_mu), 2)

        return base

    def evaluar_severidad(
        self,
        diagnostico: DiagnosticoFinal,
        contexto: Optional[ContextoIncidenciaInput] = None,
        incidencias_activas_inmueble: int = 0
    ) -> FichaIncidencia:
        """
        Ejecuta el pipeline de evaluación de severidad y triage de M3.
        Incluye soporte para S1, S2, S3, S4, S5, T1, R5 y T2.
        """
        inmueble_id = diagnostico.inmueble_id
        inmueble_info = self.db.inmuebles.get(inmueble_id, {})
        inmueble_nombre = inmueble_info.get('nombre', f"Inmueble {inmueble_id}")
        servicio_info = self.db.servicios.get(diagnostico.servicio_id, {})
        es_esencial = servicio_info.get('esencial', False)
        incidencia_id = f"inc_{diagnostico.sesion_id}"

        # ----------------------------------------------------------------------
        # Vía 1: Regla S2 - Cierre silencioso (resuelta por el huésped)
        # ----------------------------------------------------------------------
        if diagnostico.estado_cierre == 'resuelta_por_huesped' and not diagnostico.riesgo_seguridad:
            return FichaIncidencia(
                incidencia_id=incidencia_id,
                inmueble_id=inmueble_id,
                inmueble_nombre=inmueble_nombre,
                artefacto_id=diagnostico.artefacto_id,
                servicio_id=diagnostico.servicio_id,
                servicio_esencial=es_esencial,
                causa_diagnosticada=diagnostico.causa_diagnosticada,
                resoluble_por_huesped=True,
                riesgo_seguridad=False,
                temperatura=None,
                horas_restantes=None,
                dato_estimado=False,
                via_evaluacion='S2_cierre',
                puntaje_difuso=None,
                nivel_calculado=None,
                piso_r5=None,
                nivel_final=0,
                prioridad='sin_aviso',
                canal='sin_aviso',
                activacion_maxima=None,
                estado_cobertura='no_aplica',
                reglas_activadas=[],
                estado='resuelta_por_huesped',
                notificacion_redactada="Incidencia técnica resuelta satisfactoriamente por el huésped mediante pasos guiados. Registrada para reporte de mantenimiento preventivo."
            )

        # ----------------------------------------------------------------------
        # Vía 2: Regla S1 - Riesgo de Seguridad Crítico (Emergencia Nivel 5)
        # ----------------------------------------------------------------------
        if diagnostico.riesgo_seguridad or diagnostico.estado_cierre == 'abortada_seguridad':
            notif_alerta = (
                f"🚨 ALERTA CRÍTICA DE SEGURIDAD (NIVEL 5) - {inmueble_nombre}\n"
                f"Se ha detectado una señal de peligro crítico ({diagnostico.causa_diagnosticada}). "
                f"Se activó el protocolo de emergencia PE-1 indicando al huésped evacuar y ventilar de inmediato. "
                f"Se requiere intervención urgente in situ."
            )
            return FichaIncidencia(
                incidencia_id=incidencia_id,
                inmueble_id=inmueble_id,
                inmueble_nombre=inmueble_nombre,
                artefacto_id=diagnostico.artefacto_id,
                servicio_id=diagnostico.servicio_id,
                servicio_esencial=es_esencial,
                causa_diagnosticada=diagnostico.causa_diagnosticada,
                resoluble_por_huesped=False,
                riesgo_seguridad=True,
                temperatura=None,
                horas_restantes=None,
                dato_estimado=False,
                via_evaluacion='S1_emergencia',
                puntaje_difuso=None,
                nivel_calculado=5,
                piso_r5=None,
                nivel_final=5,
                prioridad='Emergencia',
                canal='alerta_inmediata',
                activacion_maxima=1.0,
                estado_cobertura='deterministica_s1',
                reglas_activadas=[ReglaActivadaInfo(regla='S1', alfa=1.0, consecuente='Emergencia', regla_pg1='S1_seguridad')],
                estado='escalada',
                notificacion_redactada=notif_alerta
            )

        # ----------------------------------------------------------------------
        # Vía 3: Regla difusa (M3 Mamdani + S5 + T1 + R5 + T2)
        # ----------------------------------------------------------------------
        # Manejo de contexto ausente / estimado (Regla S3)
        if contexto is None:
            temp = 24.0
            horas = 24.0
            estimado = True
        else:
            temp = contexto.temperatura_actual
            horas = contexto.horas_restantes
            estimado = contexto.dato_estimado

        # Regla S5: Sensibilidad contextual continua
        sensibilidad = self.calcular_sensibilidad_servicio(diagnostico.servicio_id, temp)

        inputs_m3 = {
            'ImpactoClimatico': temp,
            'TiempoRestante': horas,
            'SensibilidadServicio': sensibilidad
        }

        # Inferencia difusa Mamdani y traza C2 en Neo4j
        self.db.evaluar_fuzzificacion_cypher(inputs_m3, modulo="M3")
        centroide, alfa_max, estado_cob, reglas_act = inferencia_mamdani('M3', inputs_m3)

        # Regla T1: Mapeo de centroide a nivel de severidad (0..100 -> 1..5)
        # En caso de cobertura nula / hueco (alfa_max < 0.2), política conservadora = Nivel 3
        if alfa_max < 0.2:
            nivel_calc = 3
        elif centroide >= 80.0:
            nivel_calc = 5
        elif centroide >= 60.0:
            nivel_calc = 4
        elif centroide >= 40.0:
            nivel_calc = 3
        elif centroide >= 20.0:
            nivel_calc = 2
        else:
            nivel_calc = 1

        # Regla R5: Piso mandatorio para Servicios Esenciales
        piso = 4 if es_esencial else 1
        nivel_final = max(nivel_calc, piso)

        reglas_info = [
            ReglaActivadaInfo(
                regla=r.get('regla') or r.get('regla_id', 'R?'),
                alfa=r['alfa'],
                consecuente=r['consecuente']
            ) for r in reglas_act
        ]

        # Regla S4: Incremento de severidad por múltiples incidencias activas simultáneas en la misma unidad
        if incidencias_activas_inmueble >= 1:
            nivel_final = min(5, max(nivel_final + 1, 4))
            reglas_info.append(
                ReglaActivadaInfo(
                    regla='S4',
                    alfa=1.0,
                    consecuente='Elevacion_Concurrencia',
                    regla_pg1='S4_incidencias_simultaneas',
                    expresion=f"Incidencias previas activas en {inmueble_id}: {incidencias_activas_inmueble}"
                )
            )

        # Regla T2: Mapeo de Nivel a Prioridad y Canal de Notificación
        canales_map = {
            1: ('Baja', 'reporte_diario'),
            2: ('Baja', 'reporte_diario'),
            3: ('Media', 'cola_priorizada'),
            4: ('Alta', 'alerta_inmediata'),
            5: ('Emergencia', 'alerta_inmediata')
        }
        prioridad, canal = canales_map.get(nivel_final, ('Media', 'cola_priorizada'))

        ficha = FichaIncidencia(
            incidencia_id=incidencia_id,
            inmueble_id=inmueble_id,
            inmueble_nombre=inmueble_nombre,
            artefacto_id=diagnostico.artefacto_id,
            servicio_id=diagnostico.servicio_id,
            servicio_esencial=es_esencial,
            causa_diagnosticada=diagnostico.causa_diagnosticada,
            resoluble_por_huesped=False,
            riesgo_seguridad=False,
            temperatura=temp,
            horas_restantes=horas,
            dato_estimado=estimado,
            via_evaluacion='difusa',
            puntaje_difuso=centroide,
            nivel_calculado=nivel_calc,
            piso_r5=piso if es_esencial else None,
            nivel_final=nivel_final,
            prioridad=prioridad,
            canal=canal,
            activacion_maxima=alfa_max,
            estado_cobertura=estado_cob,
            reglas_activadas=reglas_info,
            estado='escalada'
        )

        # Redacción de notificación para anfitrión con Gemini LLM
        ficha_dict = ficha.model_dump()
        notificacion_llm = self.llm.verbalize_host_notification(ficha_dict)
        ficha.notificacion_redactada = notificacion_llm

        return ficha

# Instancia global
modulo_m3 = ModuloM3Severidad()
