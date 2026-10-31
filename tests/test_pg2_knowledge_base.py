"""
tests/test_pg2_knowledge_base.py - Pruebas de Integridad del Grafo PG2 y Motor Difuso
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import os
import pytest
from pg2_neo4j.verificacion.ref_difuso import CASOS_CALIBRACION, inferencia_mamdani
from src.db.neo4j_client import db_client

def test_cypher_files_exist():
    """Verifica que los 6 scripts de carga Cypher y las 8 consultas C1..C8 existan."""
    scripts_dir = os.path.join(os.path.dirname(__file__), "..", "pg2_neo4j", "scripts")
    consultas_dir = os.path.join(os.path.dirname(__file__), "..", "pg2_neo4j", "consultas")

    expected_scripts = [
        "01_esquema_restricciones.cypher",
        "02_catalogo_conocimiento.cypher",
        "03_reglas_nitidas.cypher",
        "04_logica_difusa.cypher",
        "05_instancias_casos.cypher",
        "06_casos_difusos.cypher"
    ]
    for script in expected_scripts:
        path = os.path.join(scripts_dir, script)
        assert os.path.exists(path), f"Falta el script Cypher: {script}"
        assert os.path.getsize(path) > 500, f"Script Cypher vacío o corrupto: {script}"

    expected_queries = [
        "C1_inferencia_nitida.cypher",
        "C1b_seguridad_R1_S1.cypher",
        "C2_fuzzificacion.cypher",
        "C3_inferencia_difusa_m1_m2_m3.cypher",
        "C4_inferencia_severidad_integrada.cypher",
        "C5_cadena_diagnostico_explicacion.cypher",
        "C6_payload_para_llm.cypher",
        "C7_controles_consistencia.cypher",
        "C8_explicacion_reglas_activadas.cypher"
    ]
    for q in expected_queries:
        path = os.path.join(consultas_dir, q)
        assert os.path.exists(path), f"Falta la consulta Cypher: {q}"

def test_all_10_fuzzy_cases_match_pi3():
    """Valida que los 10 casos difusos calibrados coincidan con Marco 2 y PI3 a 0.1 decimal."""
    for caso in CASOS_CALIBRACION:
        c_id = caso['caso_id']
        mod = caso['modulo']
        inputs = caso['inputs']
        esperado = caso['esperado_pi3']

        centroide, alfa_max, _, _ = inferencia_mamdani(mod, inputs)
        diff = abs(centroide - esperado)
        assert diff <= 0.15, (
            f"Fallo en calibración difusa caso {c_id} ({mod}): "
            f"obtenido={centroide:.2f}, esperado={esperado:.2f}, diff={diff:.3f}"
        )

def test_knowledge_base_catalogs():
    """Valida el catálogo de causas, artefactos y pasos de verificación."""
    assert len(db_client.inmuebles) == 5
    assert len(db_client.artefactos) == 6
    assert len(db_client.sintomas) == 4
    assert len(db_client.causas) == 9
    assert len(db_client.pasos) == 9

    # Verificar que existen 4 pasos no delegables según R2
    no_delegables = [p_id for p_id, p in db_client.pasos.items() if p.get('no_delegable')]
    assert len(no_delegables) == 4
    assert 'p5' in no_delegables  # termocupla
    assert 'p7' in no_delegables  # resistencia termotanque eléctrico
    assert 'p9' in no_delegables  # cerrajería cilindro mecánico
    assert 'p11' in no_delegables # manómetro refrigerante R410A


# ------------------------------------------------------------------------------
# Matriz de Validación Formal de Marco 2 (Sección d.11): Casos PT1 a PT17
# ------------------------------------------------------------------------------

def test_pt1_a_pt4_inferencia_nitida_c1():
    """PT1..PT4: Verifica C1 (filtrado R6 por tipo de artefacto, exclusión R2 de no delegables y ordenamiento R7)."""
    # PT1: tg01 + sin_agua_caliente -> sólo causas de TermotanqueGas, pasos delegables primero (p1 bajo, p2 medio, falla_termocupla sin paso)
    rows_tg = db_client.get_proximo_paso("tg01", "sin_agua_caliente")
    causas_tg = [r["causa"] for r in rows_tg]
    assert causas_tg == ["llave_gas_cerrada", "piloto_apagado", "falla_termocupla"]
    assert rows_tg[0]["paso"] == "p1" and rows_tg[0]["riesgo"] == "bajo"
    assert rows_tg[1]["paso"] == "p2" and rows_tg[1]["riesgo"] == "medio"
    assert rows_tg[2]["paso"] is None  # p5 excluido por R2 (:PasoNoDelegable)

    # PT2: te01 + sin_agua_caliente -> sólo causas de TermotanqueElectrico (termica_bajada con p6, resistencia_quemada sin paso)
    rows_te = db_client.get_proximo_paso("te01", "sin_agua_caliente")
    causas_te = [r["causa"] for r in rows_te]
    assert causas_te == ["termica_bajada", "resistencia_quemada"]
    assert rows_te[0]["paso"] == "p6"
    assert rows_te[1]["paso"] is None  # p7 excluido por R2

    # PT3: cer01 + teclado_sin_respuesta -> pilas_agotadas (p3) y mecanismo_trabado (sin paso p9)
    rows_cer = db_client.get_proximo_paso("cer01", "teclado_sin_respuesta")
    assert [r["causa"] for r in rows_cer] == ["pilas_agotadas", "mecanismo_trabado"]
    assert rows_cer[0]["paso"] == "p3"
    assert rows_cer[1]["paso"] is None

    # PT4: spl01 + no_enfria -> filtro_sucio (p10) y gas_refrigerante_bajo (sin paso p11)
    rows_spl = db_client.get_proximo_paso("spl01", "no_enfria")
    assert [r["causa"] for r in rows_spl] == ["filtro_sucio", "gas_refrigerante_bajo"]
    assert rows_spl[0]["paso"] == "p10"
    assert rows_spl[1]["paso"] is None


def test_pt5_a_pt10_seguridad_y_severidad_integrada_c1b_c4():
    """PT5..PT10: Verifica barrera de seguridad C1b y las 5 vías de severidad en C4."""
    # PT5: Prueba negativa de C1b sobre reporte benigno (rep1 no dispara protocolo de emergencia)
    assert db_client.check_seguridad("rep1") is None

    # PT6: Prueba positiva de C1b sobre reporte con olor a gas (rep6 -> Nivel 5 Emergencia + pe1)
    seg = db_client.check_seguridad("rep6")
    assert seg is not None
    assert seg["nivel_S1"] == 5
    assert seg["prioridad"] == "Emergencia"

    # PT7: C4 sobre inc1 (resuelta_por_huesped -> S2_cierre, sin_aviso)
    c4_inc1 = db_client.evaluar_severidad("inc1")
    assert c4_inc1["via"] == "S2_cierre"
    assert c4_inc1["prioridad"] == "sin_aviso"
    assert c4_inc1["canal"] == "sin_aviso"

    # PT8: C4 sobre inc6 (riesgo_seguridad -> S1_emergencia, Nivel 5, alerta_inmediata)
    c4_inc6 = db_client.evaluar_severidad("inc6")
    assert c4_inc6["via"] == "S1_emergencia"
    assert c4_inc6["nivel_final"] == 5
    assert c4_inc6["canal"] == "alerta_inmediata"

    # PT9: C4 sobre inc2 (servicio esencial acceso_principal -> activacion_maxima=0.038 < 0.2, nivel_calc=3, piso_r5=4 -> nivel_final=4)
    c4_inc2 = db_client.evaluar_severidad("inc2")
    assert c4_inc2["via"] == "difusa"
    assert abs(c4_inc2["puntaje"] - 40.5) <= 0.15
    assert c4_inc2["activacion_maxima"] < 0.2
    assert c4_inc2["nivel_calculado"] == 3
    assert c4_inc2["piso_r5"] == 4
    assert c4_inc2["nivel_final"] == 4

    # PT10: C4 sobre inc4 (ola de calor 38°C, 48h -> puntaje=76.5, nivel_final=4 Alta) e inc5 (31°C, 3.5h -> puntaje=48.7, nivel_final=3 Media)
    c4_inc4 = db_client.evaluar_severidad("inc4")
    assert abs(c4_inc4["puntaje"] - 76.5) <= 0.15
    assert c4_inc4["nivel_final"] == 4
    c4_inc5 = db_client.evaluar_severidad("inc5")
    assert abs(c4_inc5["puntaje"] - 48.7) <= 0.15
    assert c4_inc5["nivel_final"] == 3


@pytest.mark.parametrize("caso_id,modulo,inputs,esperado_pi3,min_alfa", [
    ("M1-A", "M1", {"ConfianzaExtraccion": 0.72, "CoincidenciaLexica": 0.68, "DistanciaCandidatos": 0.35}, 50.1, 0.20),
    ("M1-B", "M1", {"ConfianzaExtraccion": 0.90, "CoincidenciaLexica": 0.92, "DistanciaCandidatos": 0.85}, 82.7, 0.20),
    ("M1-hueco", "M1", {"ConfianzaExtraccion": 0.50, "CoincidenciaLexica": 0.50, "DistanciaCandidatos": 0.90}, 29.7, 0.00),
    ("M2-hip1-e1", "M2", {"FrecuenciaCausa": 0.82, "RiesgoEsfuerzoPaso": 4.2, "EvidenciaAcumulada": 0.55}, 51.1, 0.20),
    ("M2-hip1-e2", "M2", {"FrecuenciaCausa": 0.82, "RiesgoEsfuerzoPaso": 4.2, "EvidenciaAcumulada": 0.85}, 75.9, 0.20),
    ("M2-hip2-e1", "M2", {"FrecuenciaCausa": 0.75, "RiesgoEsfuerzoPaso": 1.2, "EvidenciaAcumulada": 0.55}, 68.4, 0.20),
    ("M2-hueco", "M2", {"FrecuenciaCausa": 0.10, "RiesgoEsfuerzoPaso": 5.0, "EvidenciaAcumulada": 1.00}, 50.0, 0.00),
    ("M3-caso1", "M3", {"ImpactoClimatico": 38.0, "TiempoRestante": 48.0, "SensibilidadServicio": 8.3}, 76.5, 0.20),
    ("M3-hueco", "M3", {"ImpactoClimatico": 12.0, "TiempoRestante": 12.0, "SensibilidadServicio": 10.0}, 66.7, 0.00),
    ("M3-limite", "M3", {"ImpactoClimatico": 31.0, "TiempoRestante": 3.5, "SensibilidadServicio": 5.5}, 48.7, 0.20),
])
def test_pt11_a_pt17_casos_borde_y_explicabilidad_c3_c6_c8(caso_id, modulo, inputs, esperado_pi3, min_alfa):
    """PT11..PT17: Verifica casos difusos nominales, huecos de cobertura y consultas C6/C8."""
    centroide, alfa_max, estado, reglas = inferencia_mamdani(modulo, inputs)
    assert abs(centroide - esperado_pi3) <= 0.15
    assert alfa_max >= min_alfa
    if "hueco" not in caso_id:
        c8_rows = db_client.explicar_reglas_activadas(caso_id)
        assert len(c8_rows) >= 1

    # Validar C6 (Payload estructurado para LLM) sobre inc4
    payload_inc4 = db_client.get_payload_llm("inc4")
    assert payload_inc4 is not None
    assert payload_inc4["incidencia"] == "inc4"
    assert payload_inc4["causa"] == "gas_refrigerante_bajo"
