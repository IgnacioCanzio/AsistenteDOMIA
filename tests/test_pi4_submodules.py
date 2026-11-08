"""
tests/test_pi4_submodules.py - Pruebas Unitarias de los Submódulos M1, M2 y M3
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import pytest
from src.modules.m1_interpretacion import modulo_m1
from src.modules.m2_diagnostico import modulo_m2
from src.modules.m3_severidad import modulo_m3
from src.models.schemas import ReporteEstructurado, DiagnosticoFinal, ContextoIncidenciaInput
from src.llm.prompts import I11_PLANTILLA_EMERGENCIA_FIJA

# ------------------------------------------------------------------------------
# Submódulo M1: Interpretación y Suficiencia
# ------------------------------------------------------------------------------

def test_m1_clear_intent():
    """M1 identifica artefacto unívoco y emite reporte suficiente."""
    tipo_ev, rep, eval_m1, _ = modulo_m1.procesar_relato(
        relato="Hola, no tengo agua caliente en la ducha",
        inmueble_id="inm101"
    )
    assert tipo_ev == 'reporte_emitido'
    assert rep is not None
    assert rep.artefacto_id == 'tg01'
    assert rep.sintoma_id == 'sin_agua_caliente'
    assert rep.senal_seguridad is False
    assert eval_m1.suficiencia_centroide >= 65.0

def test_m1_safety_interception():
    """M1 intercepta alarma de seguridad (I1) y emite pe1 de inmediato."""
    tipo_ev, rep, _, extra = modulo_m1.procesar_relato(
        relato="Hay mucho olor a gas en la cocina",
        inmueble_id="inm105"
    )
    assert tipo_ev == 'emergencia'
    assert rep.senal_seguridad is True
    assert extra['mensaje'] == I11_PLANTILLA_EMERGENCIA_FIJA

def test_m1_out_of_domain():
    """M1 detecta mensaje fuera de dominio según Regla I13."""
    tipo_ev, rep, _, extra = modulo_m1.procesar_relato(
        relato="Cuáles son los mejores museos para visitar hoy?",
        inmueble_id="inm101"
    )
    assert tipo_ev == 'fuera_de_dominio'
    assert rep is None
    assert "conserjería" in extra['mensaje']

# ------------------------------------------------------------------------------
# Submódulo M2: Diagnóstico y Troubleshooting
# ------------------------------------------------------------------------------

def test_m2_prioritization_and_discard():
    """M2 propone primer paso por prioridad difusa y reajusta tras descarte R11."""
    rep = ReporteEstructurado(
        reporte_id="rep_test_m2",
        inmueble_id="inm101",
        artefacto_id="tg01",
        sintoma_id="sin_agua_caliente"
    )
    ev1, inst1, _, _ = modulo_m2.iniciar_diagnostico(rep)
    assert ev1 == 'instruccion_paso'
    assert inst1.paso_id == 'p1'  # llave de gas

    # Huésped indica que la llave está abierta (resultado 'no')
    ev2, inst2, _, _ = modulo_m2.procesar_respuesta_paso(inst1.sesion_id, inst1.paso_id, resultado='no')
    assert ev2 == 'instruccion_paso'
    assert inst2.paso_id == 'p2'  # piloto

    # Huésped indica que encendió el piloto (resultado 'si')
    ev3, _, diag3, _ = modulo_m2.procesar_respuesta_paso(inst2.sesion_id, inst2.paso_id, resultado='si')
    assert ev3 == 'cierre_exitoso'
    assert diag3.estado_cierre == 'resuelta_por_huesped'
    assert diag3.causa_diagnosticada == 'piloto_apagado'

def test_m2_non_delegable_protection():
    """M2 no propone pasos no delegables al huésped y escala directamente (R2)."""
    rep = ReporteEstructurado(
        reporte_id="rep_test_m2_split",
        inmueble_id="inm103",
        artefacto_id="spl01",
        sintoma_id="no_enfria"
    )
    ev1, inst1, _, _ = modulo_m2.iniciar_diagnostico(rep)
    assert inst1.paso_id == 'p10' # filtro limpio

    # Huésped limpió filtros pero sigue sin enfriar (resultado 'no')
    ev2, inst2, diag2, _ = modulo_m2.procesar_respuesta_paso(inst1.sesion_id, inst1.paso_id, resultado='no')
    assert ev2 == 'escalada_anfitrion'
    assert diag2.estado_cierre == 'escalada'
    assert diag2.causa_diagnosticada == 'gas_refrigerante_bajo'
    # Verificar que nunca se entregó p11 (manómetro frigorífico) como paso al huésped
    assert inst2.paso_id != 'p11'

# ------------------------------------------------------------------------------
# Submódulo M3: Severidad y Triage
# ------------------------------------------------------------------------------

def test_m3_silent_closure_s2():
    """M3 aplica regla S2 y no notifica al anfitrión si fue resuelta por huésped."""
    diag = DiagnosticoFinal(
        diagnostico_id="diag_s2",
        sesion_id="ses_s2",
        inmueble_id="inm101",
        artefacto_id="tg01",
        servicio_id="agua_caliente",
        causa_diagnosticada="piloto_apagado",
        resoluble_por_huesped=True,
        riesgo_seguridad=False,
        estado_cierre="resuelta_por_huesped"
    )
    ficha = modulo_m3.evaluar_severidad(diag)
    assert ficha.via_evaluacion == 'S2_cierre'
    assert ficha.nivel_final == 0
    assert ficha.prioridad == 'sin_aviso'

def test_m3_essential_service_floor_r5():
    """M3 aplica piso obligatorio de Nivel 4 (Alta) para Servicios Esenciales."""
    diag = DiagnosticoFinal(
        diagnostico_id="diag_r5",
        sesion_id="ses_r5",
        inmueble_id="inm102",
        artefacto_id="cer01",
        servicio_id="acceso_principal",
        causa_diagnosticada="mecanismo_trabado",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        estado_cierre="escalada"
    )
    ctx = ContextoIncidenciaInput(temperatura_actual=22.0, horas_restantes=12.0)
    ficha = modulo_m3.evaluar_severidad(diag, ctx)
    assert ficha.servicio_esencial is True
    assert ficha.piso_r5 == 4
    assert ficha.nivel_final == 4
    assert ficha.prioridad == 'Alta'
    assert ficha.canal == 'alerta_inmediata'

def test_m3_heatwave_sensitivity_s5():
    """M3 calcula sensibilidad continua S5 y centroide esperado de ola de calor (76.5)."""
    diag = DiagnosticoFinal(
        diagnostico_id="diag_s5",
        sesion_id="ses_s5",
        inmueble_id="inm103",
        artefacto_id="spl01",
        servicio_id="climatizacion",
        causa_diagnosticada="gas_refrigerante_bajo",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        estado_cierre="escalada"
    )
    ctx = ContextoIncidenciaInput(temperatura_actual=38.0, horas_restantes=48.0)
    ficha = modulo_m3.evaluar_severidad(diag, ctx)
    assert abs(ficha.puntaje_difuso - 76.5) < 0.2
    assert ficha.nivel_final == 4
    assert ficha.prioridad == 'Alta'


# ------------------------------------------------------------------------------
# Pruebas de Reglas Diferidas a PI4 (I2, I8, I12, R9, R10, S4) y Trazas Cypher
# ------------------------------------------------------------------------------

def test_m1_regla_i2_alarma_negada():
    """Regla I2: Alarma explícitamente negada no dispara emergencia PE-1 y adjunta nota preventiva."""
    tipo_ev, rep, eval_m1, extra = modulo_m1.procesar_relato(
        relato="No hay olor a gas pero el termotanque no enciende",
        inmueble_id="inm101"
    )
    assert tipo_ev == 'reporte_emitido'
    assert rep is not None
    assert rep.senal_seguridad is False
    assert extra.get('alarma_negada_i2') is True
    assert "Regla I2" in extra.get('nota_preventiva_i2', '')


def test_m1_regla_i8_artefacto_inexistente():
    """Regla I8: Si el huésped reclama por un artefacto no instalado en la unidad, informa sin abrir diagnóstico."""
    tipo_ev, rep, _, extra = modulo_m1.procesar_relato(
        relato="El aire acondicionado split no enfría nada",
        inmueble_id="inm101"  # inm101 sólo tiene tg01 (TermotanqueGas)
    )
    assert tipo_ev == 'artefacto_inexistente'
    assert rep is None
    assert extra.get('regla_aplicada') == 'I8_artefacto_inexistente'


def test_m1_regla_i12_reserva_inactiva():
    """Regla I12: Verifica que la reserva esté activa antes de iniciar sesión diagnóstica."""
    tipo_ev, rep, _, extra = modulo_m1.procesar_relato(
        relato="Hola, no tengo agua caliente",
        inmueble_id="inm101",
        huesped_id="reserva_vencida"
    )
    assert tipo_ev == 'reserva_inactiva'
    assert rep is None
    assert extra.get('regla_aplicada') == 'I12_reserva_inactiva'


def test_m2_regla_r9_y_r10_escalamiento_directo():
    """Reglas R9 (disparo repetido de disyuntor) y R10 (corte de red compartida) escalan sin exponer al huésped."""
    # R9: Tablero eléctrico con disparo repetido
    rep_r9 = ReporteEstructurado(
        reporte_id="rep_r9",
        inmueble_id="inm104",
        artefacto_id="tab01",
        sintoma_id="disparo_repetido_disyuntor"
    )
    ev_r9, _, diag_r9, _ = modulo_m2.iniciar_diagnostico(rep_r9)
    assert ev_r9 == 'escalada_anfitrion'
    assert diag_r9.causa_diagnosticada == 'fuga_electrica_o_cortocircuito'
    assert diag_r9.servicio_id == 'electricidad'

    # R10: Sin suministro de agua potable general
    rep_r10 = ReporteEstructurado(
        reporte_id="rep_r10",
        inmueble_id="inm101",
        artefacto_id="red_agua",
        sintoma_id="sin_suministro_agua_potable"
    )
    ev_r10, _, diag_r10, _ = modulo_m2.iniciar_diagnostico(rep_r10)
    assert ev_r10 == 'escalada_anfitrion'
    assert diag_r10.causa_diagnosticada == 'corte_suministro_general_compartido'
    assert diag_r10.servicio_id == 'agua_potable'


def test_m3_regla_s4_concurrencia_incidencias_y_trazas_cypher():
    """Regla S4: Eleva el nivel de severidad cuando la unidad ya tiene otra incidencia activa simultánea."""
    from src.orchestrator.master_orchestrator import master_orchestrator
    from src.models.schemas import GuestMessageRequest

    diag = DiagnosticoFinal(
        diagnostico_id="diag_s4",
        sesion_id="ses_s4",
        inmueble_id="inm104",
        artefacto_id="te01",
        servicio_id="agua_caliente",
        causa_diagnosticada="resistencia_quemada",
        resoluble_por_huesped=False,
        riesgo_seguridad=False,
        estado_cierre="escalada"
    )
    ctx = ContextoIncidenciaInput(temperatura_actual=31.0, horas_restantes=3.5)
    # Sin concurrencia: nivel 3 (Media, 48.7)
    ficha_simple = modulo_m3.evaluar_severidad(diag, ctx, incidencias_activas_inmueble=0)
    assert ficha_simple.nivel_final == 3

    # Con concurrencia S4 (1 incidencia activa previa en el mismo departamento): sube a nivel 4 (Alta)
    ficha_s4 = modulo_m3.evaluar_severidad(diag, ctx, incidencias_activas_inmueble=1)
    assert ficha_s4.nivel_final == 4
    assert any(r.regla == 'S4' for r in ficha_s4.reglas_activadas)

    # Verificar que el Orquestador devuelve cypher_traces pobladas en cada turno
    resp = master_orchestrator.procesar_mensaje_huesped(
        GuestMessageRequest(inmueble_id="inm101", huesped_id="h1", mensaje="Hola, no sale agua caliente en la ducha")
    )
    assert len(resp.cypher_traces) >= 3


def test_m1_consulta_capacidades_y_sin_sintoma():
    """Verifica que preguntar por capacidades o sin síntoma no invente incidencias ni pregunte por gas."""
    from src.orchestrator.master_orchestrator import master_orchestrator
    from src.models.schemas import GuestMessageRequest

    # Caso 1: Pregunta de capacidades ("¿Con qué cosas me podés ayudar?")
    resp_cap = master_orchestrator.procesar_mensaje_huesped(
        GuestMessageRequest(inmueble_id="inm101", huesped_id="h1", mensaje="¿Con qué cosas me podés ayudar?")
    )
    assert resp_cap.tipo_evento == 'consulta_capacidades'
    assert resp_cap.paso_id is None
    assert "conserjería" in resp_cap.mensaje_para_huesped.lower()
    assert "termotanque" in resp_cap.mensaje_para_huesped.lower()

    # Caso 2: Mensaje genérico sin síntoma ("tengo un problema pero no sé de qué es")
    resp_indet = master_orchestrator.procesar_mensaje_huesped(
        GuestMessageRequest(inmueble_id="inm101", huesped_id="h1", mensaje="Hola, tengo un problema pero no sé de qué es")
    )
    assert resp_indet.tipo_evento == 'pregunta_aclaratoria'
    assert resp_indet.paso_id is None
    assert len(resp_indet.trazabilidad_diagnostica.get('opciones', [])) >= 2


# ------------------------------------------------------------------------------
# Pruebas de la Nueva Iteración: Patrón Sándwich LLM ⇄ Neo4j (M1, M2, M3)
# ------------------------------------------------------------------------------

def test_pi4_sandwich_m1_8_casos():
    """Ejecuta los 8 casos sándwich de M1 y valida 100% de éxito y fidelidad I10."""
    import json, os
    from src.llm.sandwich import Sandwich, ProveedorLLM
    from src.llm.prompts import PROMPT_EXTRACCION_M1, PROMPT_EXPLICACION_M1
    from src.models.schemas import ExtraccionM1
    from pi4_individuales.pi4_m1_canzio_sandwich import CASOS_M1, ejecutar_caso_m1

    reg_path = os.path.join(os.path.dirname(__file__), "..", "pi4_individuales", "pi4_llm_registro_m1.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        registro = json.load(f)

    proveedor = ProveedorLLM(modo="replay", registro=registro)
    sandwich = Sandwich(
        prefijo="m1",
        prompt_extraccion=PROMPT_EXTRACCION_M1,
        prompt_explicacion=PROMPT_EXPLICACION_M1,
        modelo_pydantic=ExtraccionM1,
        llm=proveedor,
        rotulo_contexto="Contexto del inmueble",
        rotulo_mensaje="Relato del huésped"
    )

    for c in CASOS_M1:
        res = ejecutar_caso_m1(sandwich, c)
        assert res["exito"] is True, f"Falló caso M1 {c['id']}: {res.get('problemas_fidelidad')}"


def test_pi4_sandwich_m2_8_casos():
    """Ejecuta los 8 casos sándwich de M2 y valida 100% de éxito y fidelidad I10."""
    import json, os
    from src.llm.sandwich import Sandwich, ProveedorLLM
    from src.llm.prompts import PROMPT_EXTRACCION_M2, PROMPT_EXPLICACION_M2
    from src.models.schemas import ExtraccionM2
    from pi4_individuales.pi4_m2_lopez_sandwich import CASOS_M2, ejecutar_caso_m2

    reg_path = os.path.join(os.path.dirname(__file__), "..", "pi4_individuales", "pi4_llm_registro_m2.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        registro = json.load(f)

    proveedor = ProveedorLLM(modo="replay", registro=registro)
    sandwich = Sandwich(
        prefijo="m2",
        prompt_extraccion=PROMPT_EXTRACCION_M2,
        prompt_explicacion=PROMPT_EXPLICACION_M2,
        modelo_pydantic=ExtraccionM2,
        llm=proveedor,
        rotulo_contexto="Contexto de la unidad",
        rotulo_mensaje="Mensaje del huésped"
    )

    for c in CASOS_M2:
        res = ejecutar_caso_m2(sandwich, c)
        assert res["exito"] is True, f"Falló caso M2 {c['id']}: {res.get('problemas_fidelidad')}"


def test_pi4_sandwich_m3_8_casos():
    """Ejecuta los 8 casos sándwich de M3 y valida 100% de éxito y fidelidad I10."""
    import json, os
    from src.llm.sandwich import Sandwich, ProveedorLLM
    from src.llm.prompts import PROMPT_EXTRACCION_M3, PROMPT_EXPLICACION_M3
    from src.models.schemas import ExtraccionM3
    from pi4_individuales.pi4_m3_montero_sandwich import CASOS_M3, ejecutar_caso_m3

    reg_path = os.path.join(os.path.dirname(__file__), "..", "pi4_individuales", "pi4_llm_registro_m3.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        registro = json.load(f)

    proveedor = ProveedorLLM(modo="replay", registro=registro)
    sandwich = Sandwich(
        prefijo="m3",
        prompt_extraccion=PROMPT_EXTRACCION_M3,
        prompt_explicacion=PROMPT_EXPLICACION_M3,
        modelo_pydantic=ExtraccionM3,
        llm=proveedor,
        rotulo_contexto="Contexto del sistema",
        rotulo_mensaje="Consulta del usuario"
    )

    for c in CASOS_M3:
        res = ejecutar_caso_m3(sandwich, c)
        assert res["exito"] is True, f"Falló caso M3 {c['id']}: {res.get('problemas_fidelidad')}"


def test_hallazgos_y_alertas_emergencia():
    """Valida resolución de los hallazgos: no mención de R2, alarma de gas contextual, despacho de alerta."""
    from src.orchestrator.master_orchestrator import master_orchestrator
    from src.models.schemas import GuestMessageRequest
    from src.llm.gemini_client import gemini_client

    # Hallazgo #5: Mención inocua de gas no dispara alarma
    es_seg, _, _ = gemini_client._detectar_alarma_seguridad("Tengo una hornalla a gas apagada")
    assert es_seg is False

    # Fuga real de gas sí dispara alarma
    es_seg_real, _, _ = gemini_client._detectar_alarma_seguridad("Siento un fuerte olor a gas")
    assert es_seg_real is True

    # Hallazgo #6: Inmueble inexistente
    res_inex = master_orchestrator.procesar_mensaje_huesped(
        GuestMessageRequest(inmueble_id="inm999", mensaje="No anda nada")
    )
    assert res_inex.tipo_evento == 'fuera_de_dominio'
    assert "no se encuentra registrado" in res_inex.mensaje_para_huesped

    # Hallazgo #4: Alerta de emergencia despachada
    res_em = master_orchestrator.procesar_mensaje_huesped(
        GuestMessageRequest(inmueble_id="inm105", mensaje="Hay mucho olor a gas en la cocina")
    )
    assert res_em.tipo_evento == 'emergencia'
    assert res_em.alerta_emergencia is not None
    assert res_em.alerta_emergencia.tipo_emergencia == "gas_o_seguridad_critica"
    assert len(master_orchestrator.listar_alertas_emergencia()) >= 1
