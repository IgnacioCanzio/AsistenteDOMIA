"""
pi4_individuales/pi4_m2_lopez.py - Script Individual de Evaluación PI4
Responsable: Nicolás López (Submódulo M2: Diagnóstico y Resolución Asistida)
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import sys
import os

# Forzar salida en UTF-8 en Windows PowerShell y agregar raíz al path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.schemas import ReporteEstructurado
from src.modules.m2_diagnostico import modulo_m2

def run_pi4_m2_tests():
    print("=" * 80)
    print("EJECUCIÓN DE PRUEBAS PI4 - SUBMÓDULO M2 (Nicolás López)")
    print("Diagnóstico, Priorización Difusa M2, Descarte R11, Resolución R3 y Seguridad R2")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # Caso 1: Troubleshooting completo exitoso de Termotanque a Gas (Depto 101)
    # Turno 1 propone llave de gas (p1). Descarte (no).
    # Turno 2 propone encender piloto (p2). Confirmación (si). Resuelto!
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Ciclo completo exitoso en Termotanque a Gas (tg01) ---")
    rep1 = ReporteEstructurado(
        reporte_id="rep_test_1",
        inmueble_id="inm101",
        artefacto_id="tg01",
        sintoma_id="sin_agua_caliente",
        senal_seguridad=False
    )
    ev, inst1, diag1, extra1 = modulo_m2.iniciar_diagnostico(rep1)
    print(f"Turno 1 - Evento: {ev}")
    print(f"  Paso propuesto: {inst1.paso_id} (Prioridad difusa: {inst1.prioridad_difusa:.1f})")
    print(f"  Instrucción verbalizada: {inst1.texto_verbalizado_llm}")
    assert inst1.paso_id == 'p1', "En turno 1 debe proponerse p1 (llave de gas, mayor prioridad difusa inicial 68.4)"

    print("\nSimulando respuesta del huésped: 'no' (la llave de gas ya estaba abierta)")
    ev2, inst2, diag2, extra2 = modulo_m2.procesar_respuesta_paso(
        sesion_id=inst1.sesion_id,
        paso_id=inst1.paso_id,
        resultado='no'
    )
    print(f"Turno 2 - Evento: {ev2}")
    print(f"  Paso propuesto: {inst2.paso_id} (Prioridad difusa actualizada: {inst2.prioridad_difusa:.1f})")
    print(f"  Instrucción verbalizada: {inst2.texto_verbalizado_llm}")
    assert inst2.paso_id == 'p2', "En turno 2 tras descartar llave, la hipótesis piloto escala a prioridad 75.9 (p2)"

    print("\nSimulando respuesta del huésped: 'si' (el piloto encendió y ya sale agua caliente)")
    ev3, inst3, diag3, extra3 = modulo_m2.procesar_respuesta_paso(
        sesion_id=inst2.sesion_id,
        paso_id=inst2.paso_id,
        resultado='si'
    )
    print(f"Turno 3 - Evento: {ev3}")
    print(f"  Estado de cierre: {diag3.estado_cierre}")
    print(f"  Causa diagnosticada y resuelta: {diag3.causa_diagnosticada}")
    assert diag3.estado_cierre == 'resuelta_por_huesped', "El estado debe ser resuelta_por_huesped (Regla R3)"
    print("  [OK] TEST 1 SUPERADO")

    # --------------------------------------------------------------------------
    # Caso 2: Bloqueo de cerradura electrónica (Depto 102)
    # Proponer p3. Huésped indica "no_puedo" o no funciona -> Regla R4/R8 escalada
    # --------------------------------------------------------------------------
    print("\n--- TEST 2: Bloqueo de Cerradura Electrónica (cer01) ---")
    rep2 = ReporteEstructurado(
        reporte_id="rep_test_2",
        inmueble_id="inm102",
        artefacto_id="cer01",
        sintoma_id="teclado_sin_respuesta"
    )
    ev_c2, inst_c2, diag_c2, extra_c2 = modulo_m2.iniciar_diagnostico(rep2)
    print(f"Turno 1 - Evento: {ev_c2}")
    print(f"  Paso propuesto: {inst_c2.paso_id}")

    print("Simulando que el huésped prueba p3 y no abre (resultado 'no')")
    ev_c2_post, inst_c2_post, diag_c2_post, _ = modulo_m2.procesar_respuesta_paso(
        sesion_id=inst_c2.sesion_id,
        paso_id=inst_c2.paso_id,
        resultado='no'
    )
    print(f"Turno 2 - Evento: {ev_c2_post}")
    print(f"  Causa diagnosticada: {diag_c2_post.causa_diagnosticada}")
    print(f"  Estado: {diag_c2_post.estado_cierre}")
    assert diag_c2_post.estado_cierre == 'escalada', "Debe escalar a anfitrión por mecanismo trabado / no delegable"
    print("  [OK] TEST 2 SUPERADO")

    # --------------------------------------------------------------------------
    # Caso 3: Filtro de Split AC y protección de paso no delegable (Depto 103)
    # Proponer p10 (limpiar filtro). Huésped indica "no".
    # Siguiente causa es fuga de refrigerante (paso p11 NO DELEGABLE).
    # Regla R2: El sistema NO debe enviar p11 al huésped, debe escalar!
    # --------------------------------------------------------------------------
    print("\n--- TEST 3: Split AC y protección de Paso No Delegable R2 (spl01) ---")
    rep3 = ReporteEstructurado(
        reporte_id="rep_test_3",
        inmueble_id="inm103",
        artefacto_id="spl01",
        sintoma_id="no_enfria"
    )
    ev_c3, inst_c3, _, _ = modulo_m2.iniciar_diagnostico(rep3)
    print(f"Turno 1 - Paso propuesto: {inst_c3.paso_id} (Limpieza de filtros)")
    assert inst_c3.paso_id == 'p10'

    print("Simulando que el huésped limpió el filtro pero sigue sin enfriar (resultado 'no')")
    ev_c3_post, inst_c3_post, diag_c3_post, _ = modulo_m2.procesar_respuesta_paso(
        sesion_id=inst_c3.sesion_id,
        paso_id=inst_c3.paso_id,
        resultado='no'
    )
    print(f"Turno 2 - Evento: {ev_c3_post}")
    print(f"  Causa diagnosticada: {diag_c3_post.causa_diagnosticada}")
    print(f"  Paso no delegable p11 fue protegido: {inst_c3_post.paso_id != 'p11'}")
    assert diag_c3_post.estado_cierre == 'escalada'
    assert diag_c3_post.causa_diagnosticada == 'gas_refrigerante_bajo'
    print("  [OK] TEST 3 SUPERADO (Paso no delegable protegido según R2)")

    # --------------------------------------------------------------------------
    # Caso 4: Termotanque eléctrico con resistencia quemada (Depto 104)
    # Proponer p6 (térmica). Huésped indica "no". Causa p7 es no delegable -> Escalar.
    # --------------------------------------------------------------------------
    print("\n--- TEST 4: Termotanque Eléctrico (te01) y Paso No Delegable p7 ---")
    rep4 = ReporteEstructurado(
        reporte_id="rep_test_4",
        inmueble_id="inm104",
        artefacto_id="te01",
        sintoma_id="sin_agua_caliente"
    )
    ev_c4, inst_c4, _, _ = modulo_m2.iniciar_diagnostico(rep4)
    print(f"Turno 1 - Paso propuesto: {inst_c4.paso_id} (Rearme térmica)")
    assert inst_c4.paso_id == 'p6'

    ev_c4_post, _, diag_c4_post, _ = modulo_m2.procesar_respuesta_paso(
        sesion_id=inst_c4.sesion_id,
        paso_id=inst_c4.paso_id,
        resultado='no'
    )
    print(f"Turno 2 - Evento: {ev_c4_post}")
    print(f"  Causa diagnosticada: {diag_c4_post.causa_diagnosticada}")
    assert diag_c4_post.estado_cierre == 'escalada'
    assert diag_c4_post.causa_diagnosticada == 'resistencia_quemada'
    print("  [OK] TEST 4 SUPERADO")

    # --------------------------------------------------------------------------
    # Caso 5: Aborto inmediato por alarma de seguridad (Depto 105 - Olor a gas)
    # Reglas R1, S1: No diagnosticar, abortar de inmediato.
    # --------------------------------------------------------------------------
    print("\n--- TEST 5: Aborto Inmediato por Alarma de Seguridad (R1) ---")
    rep5 = ReporteEstructurado(
        reporte_id="rep_test_5",
        inmueble_id="inm105",
        artefacto_id="tg03",
        sintoma_id="olor_a_gas",
        senal_seguridad=True
    )
    ev_c5, inst_c5, diag_c5, _ = modulo_m2.iniciar_diagnostico(rep5)
    print(f"Resultado directo: {ev_c5}")
    print(f"  Estado de cierre: {diag_c5.estado_cierre}")
    print(f"  Riesgo seguridad: {diag_c5.riesgo_seguridad}")
    assert ev_c5 == 'emergencia'
    assert diag_c5.estado_cierre == 'abortada_seguridad'
    assert diag_c5.riesgo_seguridad is True
    print("  [OK] TEST 5 SUPERADO")

    print("\n" + "=" * 80)
    print("RESUMEN PI4 M2: Todas las pruebas (1 a 5) ejecutadas exitosamente.")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = run_pi4_m2_tests()
    sys.exit(0 if success else 1)
