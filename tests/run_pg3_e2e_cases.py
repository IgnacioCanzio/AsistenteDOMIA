"""
tests/run_pg3_e2e_cases.py - Suite E2E de los 6 Casos Canónicos de Marco 2
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import sys
import os

# Configurar salida UTF-8 y ruta
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator.master_orchestrator import master_orchestrator
from src.models.schemas import GuestMessageRequest, StepResponseRequest, ClarificationResponseRequest

def run_all_e2e_cases():
    print("=" * 80)
    print("EJECUCIÓN E2E DE LOS 6 CASOS CANÓNICOS DE MARCO 2 (DOMIA PG3)")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # CASO 1: Depto 101 - Termotanque a Gas (Resolución completa por el huésped)
    # --------------------------------------------------------------------------
    print("\n[CASO 1] Depto 101 · Termotanque a Gas (Resolución asistida exitosa)")
    r1 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm101",
        mensaje="Hola, no sale agua caliente de la ducha."
    ))
    print(f"  Turno 1: {r1.tipo_evento} -> Paso {r1.paso_id}")
    assert r1.paso_id == 'p1'

    r2 = master_orchestrator.procesar_respuesta_paso(StepResponseRequest(
        sesion_id=r1.sesion_id,
        paso_id=r1.paso_id,
        resultado='no'
    ))
    print(f"  Turno 2: {r2.tipo_evento} -> Paso {r2.paso_id}")
    assert r2.paso_id == 'p2'

    r3 = master_orchestrator.procesar_respuesta_paso(StepResponseRequest(
        sesion_id=r2.sesion_id,
        paso_id=r2.paso_id,
        resultado='si'
    ))
    print(f"  Turno 3: {r3.tipo_evento} -> Nivel {r3.ficha_incidencia.nivel_final} ({r3.ficha_incidencia.prioridad})")
    assert r3.tipo_evento == 'cierre_exitoso'
    assert r3.ficha_incidencia.nivel_final == 0
    assert r3.ficha_incidencia.via_evaluacion == 'S2_cierre'
    print("  -> [OK] CASO 1 SUPERADO")

    # --------------------------------------------------------------------------
    # CASO 2: Depto 102 · Cerradura Electrónica y Servicio Esencial
    # --------------------------------------------------------------------------
    print("\n[CASO 2] Depto 102 · Cerradura Electrónica (Piso R5 Servicio Esencial)")
    r_c2_1 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm102",
        mensaje="El teclado digital no enciende ni responde al tocarlo.",
        temperatura_actual=22.0,
        horas_restantes=12.0
    ))
    print(f"  Turno 1: {r_c2_1.tipo_evento} -> Paso {r_c2_1.paso_id}")
    assert r_c2_1.paso_id == 'p3'

    r_c2_2 = master_orchestrator.procesar_respuesta_paso(StepResponseRequest(
        sesion_id=r_c2_1.sesion_id,
        paso_id=r_c2_1.paso_id,
        resultado='no'
    ))
    print(f"  Turno 2: {r_c2_2.tipo_evento} -> Nivel {r_c2_2.ficha_incidencia.nivel_final} ({r_c2_2.ficha_incidencia.prioridad})")
    assert r_c2_2.tipo_evento == 'escalada_anfitrion'
    assert r_c2_2.ficha_incidencia.servicio_esencial is True
    assert r_c2_2.ficha_incidencia.piso_r5 == 4
    assert r_c2_2.ficha_incidencia.nivel_final == 4
    assert r_c2_2.ficha_incidencia.canal == 'alerta_inmediata'
    print("  -> [OK] CASO 2 SUPERADO")

    # --------------------------------------------------------------------------
    # CASO 3: Depto 104 · Ambigüedad Multiartefacto y Desambiguación
    # --------------------------------------------------------------------------
    print("\n[CASO 3] Depto 104 · Ambigüedad Eléctrico vs Gas (Desambiguación M1)")
    r_c3_1 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm104",
        mensaje="No tengo agua caliente."
    ))
    print(f"  Turno 1: {r_c3_1.tipo_evento}")
    assert r_c3_1.tipo_evento == 'pregunta_aclaratoria'

    r_c3_2 = master_orchestrator.procesar_respuesta_aclaracion(ClarificationResponseRequest(
        inmueble_id="inm104",
        huesped_id="h1",
        respuesta="Termotanque eléctrico del baño"
    ))
    print(f"  Turno 2 (tras aclaración): {r_c3_2.tipo_evento} -> Paso {r_c3_2.paso_id}")
    assert r_c3_2.tipo_evento == 'instruccion_paso'
    assert r_c3_2.paso_id == 'p6' # rearme de térmica para termotanque eléctrico te01
    print("  -> [OK] CASO 3 SUPERADO")

    # --------------------------------------------------------------------------
    # CASO 4: Depto 103 · Ola de Calor y Climatización Extrema
    # --------------------------------------------------------------------------
    print("\n[CASO 4] Depto 103 · Climatización en Ola de Calor (Sensibilidad S5)")
    r_c4_1 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm103",
        mensaje="El aire split no enfría la habitación y hace 38 grados afuera.",
        temperatura_actual=38.0,
        horas_restantes=48.0
    ))
    print(f"  Turno 1: {r_c4_1.tipo_evento} -> Paso {r_c4_1.paso_id}")
    assert r_c4_1.paso_id == 'p10'

    r_c4_2 = master_orchestrator.procesar_respuesta_paso(StepResponseRequest(
        sesion_id=r_c4_1.sesion_id,
        paso_id=r_c4_1.paso_id,
        resultado='no'
    ))
    print(f"  Turno 2: {r_c4_2.tipo_evento} -> Nivel {r_c4_2.ficha_incidencia.nivel_final} (Puntaje: {r_c4_2.ficha_incidencia.puntaje_difuso:.1f})")
    assert r_c4_2.tipo_evento == 'escalada_anfitrion'
    assert abs(r_c4_2.ficha_incidencia.puntaje_difuso - 76.5) < 0.2
    assert r_c4_2.ficha_incidencia.nivel_final == 4
    assert r_c4_2.ficha_incidencia.prioridad == 'Alta'
    assert r_c4_2.ficha_incidencia.canal == 'alerta_inmediata'
    print("  -> [OK] CASO 4 SUPERADO")

    # --------------------------------------------------------------------------
    # CASO 5: Depto 104 · Check-out Inminente (M3-limite)
    # --------------------------------------------------------------------------
    print("\n[CASO 5] Depto 104 · Termotanque Eléctrico con Check-out Inminente (3.5h)")
    r_c5_1 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm104",
        mensaje="El termotanque eléctrico del baño no calienta el agua.",
        temperatura_actual=31.0,
        horas_restantes=3.5
    ))
    print(f"  Turno 1: {r_c5_1.tipo_evento} -> Paso {r_c5_1.paso_id}")

    r_c5_2 = master_orchestrator.procesar_respuesta_paso(StepResponseRequest(
        sesion_id=r_c5_1.sesion_id,
        paso_id=r_c5_1.paso_id,
        resultado='no'
    ))
    print(f"  Turno 2: {r_c5_2.tipo_evento} -> Nivel {r_c5_2.ficha_incidencia.nivel_final} (Puntaje: {r_c5_2.ficha_incidencia.puntaje_difuso:.1f})")
    assert r_c5_2.tipo_evento == 'escalada_anfitrion'
    assert r_c5_2.ficha_incidencia.nivel_final == 3
    assert r_c5_2.ficha_incidencia.prioridad == 'Media'
    assert r_c5_2.ficha_incidencia.canal == 'cola_priorizada'
    print("  -> [OK] CASO 5 SUPERADO")

    # --------------------------------------------------------------------------
    # CASO 6: Depto 105 · Olor a Gas (Alarma Crítica PE-1 y Nivel 5)
    # --------------------------------------------------------------------------
    print("\n[CASO 6] Depto 105 · Olor a Gas (Alarma Determinística I1 -> R1 -> S1)")
    r_c6 = master_orchestrator.procesar_mensaje_huesped(GuestMessageRequest(
        inmueble_id="inm105",
        mensaje="Ayuda, siento un olor a gas muy fuerte en el depto."
    ))
    print(f"  Evento directo: {r_c6.tipo_evento} -> Nivel {r_c6.ficha_incidencia.nivel_final} ({r_c6.ficha_incidencia.prioridad})")
    print(f"  Protocolo emitido: {r_c6.mensaje_para_huesped[:80]}...")
    assert r_c6.tipo_evento == 'emergencia'
    assert r_c6.ficha_incidencia.nivel_final == 5
    assert r_c6.ficha_incidencia.prioridad == 'Emergencia'
    assert r_c6.ficha_incidencia.canal == 'alerta_inmediata'
    assert r_c6.ficha_incidencia.via_evaluacion == 'S1_emergencia'
    print("  -> [OK] CASO 6 SUPERADO")

    print("\n" + "=" * 80)
    print("RESUMEN E2E PG3: Los 6 Casos Canónicos fueron ejecutados con éxito rotundo.")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = run_all_e2e_cases()
    sys.exit(0 if success else 1)
