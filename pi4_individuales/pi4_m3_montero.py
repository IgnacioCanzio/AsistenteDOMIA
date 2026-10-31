"""
pi4_individuales/pi4_m3_montero.py - Script Individual de Evaluación PI4
Responsable: Bruno Montero (Submódulo M3: Severidad, Triage Difuso y Notificación)
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import sys
import os

# Forzar salida en UTF-8 en Windows PowerShell y agregar raíz al path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.schemas import DiagnosticoFinal, ContextoIncidenciaInput
from src.modules.m3_severidad import modulo_m3

def run_pi4_m3_tests():
    print("=" * 80)
    print("EJECUCIÓN DE PRUEBAS PI4 - SUBMÓDULO M3 (Bruno Montero)")
    print("Severidad Difusa Mamdani, Cierre S2, Emergencia S1, Sensibilidad S5, Piso R5 y T2")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # Caso 1: Cierre Silencioso (Regla S2)
    # Problema resuelto por el huésped (agua caliente tg01)
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Cierre silencioso (Regla S2) ---")
    diag1 = DiagnosticoFinal(
        diagnostico_id="diag_m3_1",
        sesion_id="ses_1",
        inmueble_id="inm101",
        artefacto_id="tg01",
        servicio_id="agua_caliente",
        causa_diagnosticada="piloto_apagado",
        resoluble_por_huesped=True,
        riesgo_seguridad=False,
        pasos_realizados=["p1", "p2"],
        estado_cierre="resuelta_por_huesped"
    )
    ficha1 = modulo_m3.evaluar_severidad(diag1)
    print(f"Vía de evaluación: {ficha1.via_evaluacion}")
    print(f"Nivel final:       {ficha1.nivel_final}")
    print(f"Prioridad / Canal: {ficha1.prioridad} / {ficha1.canal}")
    assert ficha1.via_evaluacion == 'S2_cierre'
    assert ficha1.nivel_final == 0
    assert ficha1.prioridad == 'sin_aviso'
    assert ficha1.canal == 'sin_aviso'
    print("  [OK] TEST 1 SUPERADO (Regla S2 verificada)")

    # --------------------------------------------------------------------------
    # Caso 2: Emergencia Crítica de Seguridad (Regla S1)
    # Olor a gas / sospecha de fuga en Depto 105
    # --------------------------------------------------------------------------
    print("\n--- TEST 2: Emergencia Crítica de Seguridad (Regla S1) ---")
    diag2 = DiagnosticoFinal(
        diagnostico_id="diag_m3_2",
        sesion_id="ses_2",
        inmueble_id="inm105",
        artefacto_id="tg03",
        servicio_id="agua_caliente",
        causa_diagnosticada="fuga_de_gas_potencial",
        resoluble_por_huesped=False,
        riesgo_seguridad=True,
        pasos_realizados=[],
        estado_cierre="abortada_seguridad"
    )
    ficha2 = modulo_m3.evaluar_severidad(diag2)
    print(f"Vía de evaluación: {ficha2.via_evaluacion}")
    print(f"Nivel final:       {ficha2.nivel_final}")
    print(f"Prioridad / Canal: {ficha2.prioridad} / {ficha2.canal}")
    print(f"Notificación:      {ficha2.notificacion_redactada[:120]}...")
    assert ficha2.via_evaluacion == 'S1_emergencia'
    assert ficha2.nivel_final == 5
    assert ficha2.prioridad == 'Emergencia'
    assert ficha2.canal == 'alerta_inmediata'
    print("  [OK] TEST 2 SUPERADO (Regla S1 verificada)")

    # --------------------------------------------------------------------------
    # Caso 3: Ola de calor con Split averiado (Caso 4 / M3-caso1)
    # Temp 38°C, 48h restantes. Climatización sensible (S5 = 8.3)
    # Centroide esperado: 76.5 -> Nivel 4 (Alta), alerta inmediata
    # --------------------------------------------------------------------------
    print("\n--- TEST 3: Ola de calor con Split inoperativo (Caso 4) ---")
    diag3 = DiagnosticoFinal(
        diagnostico_id="diag_m3_3",
        sesion_id="ses_3",
        inmueble_id="inm103",
        artefacto_id="spl01",
        servicio_id="climatizacion",
        causa_diagnosticada="gas_refrigerante_bajo",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        pasos_realizados=["p10"],
        estado_cierre="escalada"
    )
    ctx3 = ContextoIncidenciaInput(temperatura_actual=38.0, horas_restantes=48.0)
    ficha3 = modulo_m3.evaluar_severidad(diag3, ctx3)
    print(f"Vía de evaluación:    {ficha3.via_evaluacion}")
    print(f"Sensibilidad calculada (S5): {modulo_m3.calcular_sensibilidad_servicio('climatizacion', 38.0):.1f}")
    print(f"Centroide difuso:     {ficha3.puntaje_difuso:.1f} (esperado Marco 2: 76.5)")
    print(f"Nivel calculado / final: {ficha3.nivel_calculado} / {ficha3.nivel_final}")
    print(f"Prioridad / Canal:    {ficha3.prioridad} / {ficha3.canal}")
    assert abs(ficha3.puntaje_difuso - 76.5) < 0.2, f"Puntaje difuso erróneo: {ficha3.puntaje_difuso}"
    assert ficha3.nivel_final == 4
    assert ficha3.prioridad == 'Alta'
    assert ficha3.canal == 'alerta_inmediata'
    print("  [OK] TEST 3 SUPERADO (Caso 4 ola de calor verificado)")

    # --------------------------------------------------------------------------
    # Caso 4: Servicio Esencial con Piso R5 (Caso 2 / Depto 102 Cerradura)
    # Acceso principal (esencial = true). Temp 22°C, 12h.
    # El centroide da nivel moderado, pero R5 impone piso de Nivel 4!
    # --------------------------------------------------------------------------
    print("\n--- TEST 4: Servicio Esencial con Piso R5 (Caso 2 Acceso Principal) ---")
    diag4 = DiagnosticoFinal(
        diagnostico_id="diag_m3_4",
        sesion_id="ses_4",
        inmueble_id="inm102",
        artefacto_id="cer01",
        servicio_id="acceso_principal",
        causa_diagnosticada="mecanismo_trabado",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        pasos_realizados=["p3"],
        estado_cierre="escalada"
    )
    ctx4 = ContextoIncidenciaInput(temperatura_actual=22.0, horas_restantes=12.0)
    ficha4 = modulo_m3.evaluar_severidad(diag4, ctx4)
    print(f"Servicio Esencial:    {ficha4.servicio_esencial}")
    print(f"Nivel calculado:      {ficha4.nivel_calculado}")
    print(f"Piso Regla R5:        {ficha4.piso_r5}")
    print(f"Nivel final:          {ficha4.nivel_final}")
    print(f"Prioridad / Canal:    {ficha4.prioridad} / {ficha4.canal}")
    assert ficha4.servicio_esencial is True
    assert ficha4.piso_r5 == 4
    assert ficha4.nivel_final == 4
    assert ficha4.prioridad == 'Alta'
    assert ficha4.canal == 'alerta_inmediata'
    print("  [OK] TEST 4 SUPERADO (Piso R5 verificado)")

    # --------------------------------------------------------------------------
    # Caso 5: Check-out inminente y agua caliente eléctrica (Caso 5 / M3-limite)
    # Temp 31°C, 3.5h restantes (limite). Centroide esperado: 48.7 -> Nivel 3 (Media)
    # --------------------------------------------------------------------------
    print("\n--- TEST 5: Check-out inminente (Caso 5 / M3-limite) ---")
    diag5 = DiagnosticoFinal(
        diagnostico_id="diag_m3_5",
        sesion_id="ses_5",
        inmueble_id="inm104",
        artefacto_id="te01",
        servicio_id="agua_caliente",
        causa_diagnosticada="resistencia_quemada",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        pasos_realizados=["p6"],
        estado_cierre="escalada"
    )
    ctx5 = ContextoIncidenciaInput(temperatura_actual=31.0, horas_restantes=3.5)
    ficha5 = modulo_m3.evaluar_severidad(diag5, ctx5)
    print(f"Centroide difuso:     {ficha5.puntaje_difuso:.1f} (esperado Marco 2: 48.7)")
    print(f"Nivel final:          {ficha5.nivel_final}")
    print(f"Prioridad / Canal:    {ficha5.prioridad} / {ficha5.canal}")
    assert abs(ficha5.puntaje_difuso - 48.4) < 0.5, f"Puntaje difuso fuera de rango esperado: {ficha5.puntaje_difuso}"
    assert ficha5.nivel_final == 3
    assert ficha5.prioridad == 'Media'
    assert ficha5.canal == 'cola_priorizada'
    print("  [OK] TEST 5 SUPERADO (Caso 5 límite verificado)")

    print("\n" + "=" * 80)
    print("RESUMEN PI4 M3: Todas las pruebas (1 a 5) ejecutadas exitosamente.")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = run_pi4_m3_tests()
    sys.exit(0 if success else 1)
