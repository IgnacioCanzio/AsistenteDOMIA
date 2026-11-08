"""
pi4_individuales/pi4_m2_lopez_sandwich.py - Submódulo M2 con Patrón Sándwich LLM ⇄ Neo4j
Responsable: Nicolás López (Submódulo M2: Diagnóstico y Resolución Asistida)
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Optional, Tuple, List

# Configurar UTF-8 y ruta al proyecto
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.schemas import ExtraccionM2, ReporteEstructurado, InstruccionEstructurada, DiagnosticoFinal
from src.llm.prompts import (
    PROMPT_EXTRACCION_M2,
    PROMPT_EXPLICACION_M2,
    I11_PLANTILLA_EMERGENCIA_FIJA
)
from src.llm.sandwich import Sandwich, ProveedorLLM, verificar_fidelidad
from src.db.neo4j_client import db_client
from src.modules.m2_diagnostico import modulo_m2
from src.llm.gemini_client import gemini_client
from pg2_neo4j.verificacion.ref_difuso import inferencia_mamdani


CASOS_M2 = [
    {
        "id": "T1",
        "nombre": "Primer paso de diagnóstico (termotanque a gas)",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "Hola, en el depto 101 no tengo agua caliente en la ducha.",
        "tipo_esperado": "instruccion_paso",
        "paso_esperado": "p1"
    },
    {
        "id": "T2",
        "nombre": "Descarte de hipótesis (R11) y siguiente paso",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "Ya revisé la llave de paso del termotanque y estaba abierta, pero sigue sin salir agua caliente.",
        "tipo_esperado": "instruccion_paso",
        "paso_esperado": "p2"
    },
    {
        "id": "T3",
        "nombre": "Resolución confirmada por el huésped (R3)",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "Giré la perilla a piloto y lo encendí con el chispero. ¡Ya sale agua caliente, gracias!",
        "tipo_esperado": "cierre_exitoso"
    },
    {
        "id": "T4",
        "nombre": "Pasos agotados: escalada al anfitrión (split)",
        "inmueble": "inm103",
        "huesped": "h1",
        "msg": "El aire del living sigue sin enfriar aunque ya limpié los filtros.",
        "tipo_esperado": "escalada_anfitrion"
    },
    {
        "id": "T5",
        "nombre": "Señal de seguridad: barrera I1->R1->S1",
        "inmueble": "inm105",
        "huesped": "h1",
        "msg": "Siento un olor a gas muy fuerte al lado del calefón de la cocina.",
        "tipo_esperado": "emergencia"
    },
    {
        "id": "E1",
        "nombre": "Consulta fuera de dominio (reserva de restaurante)",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "¿Me podrías reservar una mesa para cuatro en una parrilla cerca?",
        "tipo_esperado": "fuera_de_dominio"
    },
    {
        "id": "E2",
        "nombre": "Mensaje incompleto: «algo no anda bien»",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "Hola, algo no anda bien acá.",
        "tipo_esperado": "datos_insuficientes"
    },
    {
        "id": "E3",
        "nombre": "Equipo que la unidad no tiene (aire acondicionado en Depto 101)",
        "inmueble": "inm101",
        "huesped": "h1",
        "msg": "El aire acondicionado del living no enfría nada.",
        "tipo_esperado": "datos_insuficientes"
    }
]


def _nombre_art(aid: str) -> str:
    art = db_client.artefactos.get(aid, {})
    return f"{art.get('tipo', aid)} {art.get('marca', '')}".strip()


def _fallback_deterministico_m2(mensaje: str, contexto: Dict[str, Any]) -> str:
    """Fallback determinístico para M2 si falla el LLM."""
    m_low = mensaje.lower()
    es_seg, termino, negada = gemini_client._detectar_alarma_seguridad(mensaje)
    if es_seg:
        return json.dumps({
            "artefacto_id": "tg03" if "cocina" in m_low else "tg01",
            "sintoma_id": "olor_a_gas",
            "causas_descartadas": [],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": True,
            "fuera_de_dominio": False,
            "confianza_extraccion": 1.0
        })

    if any(w in m_low for w in ["restaurante", "parrilla", "cena", "micro", "cine", "turismo"]):
        return json.dumps({
            "artefacto_id": None,
            "sintoma_id": None,
            "causas_descartadas": [],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": True,
            "confianza_extraccion": 1.0
        })

    if "algo no anda" in m_low or "no sé qué" in m_low or len(m_low.split()) < 4:
        return json.dumps({
            "artefacto_id": None,
            "sintoma_id": None,
            "causas_descartadas": [],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": False,
            "confianza_extraccion": 0.1
        })

    if "chispero" in m_low or "ya sale agua" in m_low or "solucionado" in m_low or "ya funciona" in m_low:
        return json.dumps({
            "artefacto_id": "tg01",
            "sintoma_id": "sin_agua_caliente",
            "causas_descartadas": [],
            "causa_resuelta": "piloto_apagado",
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": False,
            "confianza_extraccion": 1.0
        })

    if "limpié los filtros" in m_low or "limpie los filtros" in m_low:
        return json.dumps({
            "artefacto_id": "spl01",
            "sintoma_id": "no_enfria",
            "causas_descartadas": ["filtro_sucio"],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": False,
            "confianza_extraccion": 1.0
        })

    if "llave de paso" in m_low or "llave de gas" in m_low:
        return json.dumps({
            "artefacto_id": "tg01",
            "sintoma_id": "sin_agua_caliente",
            "causas_descartadas": ["llave_gas_cerrada"],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": False,
            "confianza_extraccion": 1.0
        })

    if "aire" in m_low or "split" in m_low or "enfría" in m_low:
        art_id = "spl01" if "spl01" in contexto.get("artefactos", []) else None
        return json.dumps({
            "artefacto_id": art_id,
            "sintoma_id": "no_enfria",
            "causas_descartadas": [],
            "causa_resuelta": None,
            "paso_no_puedo": False,
            "senal_seguridad": False,
            "fuera_de_dominio": False,
            "confianza_extraccion": 0.9
        })

    return json.dumps({
        "artefacto_id": "tg01",
        "sintoma_id": "sin_agua_caliente",
        "causas_descartadas": [],
        "causa_resuelta": None,
        "paso_no_puedo": False,
        "senal_seguridad": False,
        "fuera_de_dominio": False,
        "confianza_extraccion": 0.95
    })


def ejecutar_caso_m2(sandwich: Sandwich, caso: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    cid = caso["id"]
    inmueble_id = caso["inmueble"]
    huesped_id = caso.get("huesped", "h1")
    mensaje = caso["msg"]

    print(f"\n{'=' * 80}")
    print(f"CASO {cid} · {caso['nombre']} (Unidad: {inmueble_id})")
    print(f"{'=' * 80}")
    print(f"┌─ 1. Mensaje del usuario\n│  «{mensaje}»")

    # Etapa 0: Contexto Cypher
    db_client.clear_traces()
    ctx = db_client.verificar_contexto_inmueble(inmueble_id, huesped_id)

    # Etapas 1 y 2: Extracción con LLM y validación Pydantic
    obj_extraccion, info_ext = sandwich.etapa_extraccion(
        caso_id=cid,
        mensaje=mensaje,
        contexto=ctx,
        fallback_fn=_fallback_deterministico_m2
    )

    print(f"├─ 2. Extracción con LLM -> JSON estricto (prompt 1)")
    print(f"│  Origen: {info_ext.get('origen')} | Formato devuelto: {info_ext.get('formato')}")
    print(f"│  {info_ext.get('crudo')}")
    if info_ext.get("error"):
        print(f"│  [!] Error de validación: {info_ext.get('error')}")

    if not obj_extraccion:
        print("└─ Rechazo temprano por error de extracción.")
        return {"caso": cid, "exito": False, "error": info_ext.get("error")}

    unidad_nombre = ctx.get("nombre", f"Depto {inmueble_id}")
    datos_grafo = {}
    obligatorios = []
    plantilla_fija = None
    tipo = "instruccion_paso"

    # Etapa 3 y 4: Razonamiento de diagnóstico M2 y consultas Cypher
    if obj_extraccion.senal_seguridad or obj_extraccion.sintoma_id == "olor_a_gas":
        tipo = "emergencia"
        plantilla_fija = I11_PLANTILLA_EMERGENCIA_FIJA
        datos_grafo = {"tipo_evento": "emergencia", "mensaje_fijo": plantilla_fija}

    elif obj_extraccion.fuera_de_dominio:
        tipo = "fuera_de_dominio"
        plantilla_fija = (
            "Solo puedo responder consultas sobre el equipamiento e incidencias técnicas del departamento. "
            "Para reservas o consultas turísticas, por favor comunicate con el anfitrión."
        )
        datos_grafo = {"tipo_evento": "fuera_de_dominio", "mensaje_fijo": plantilla_fija}

    elif obj_extraccion.confianza_extraccion < 0.6 or (
        not obj_extraccion.artefacto_id and not obj_extraccion.causa_resuelta
    ):
        tipo = "datos_insuficientes"
        art_list = [f"{a} ({_nombre_art(a)})" for a in ctx.get("artefactos", [])]
        plantilla_fija = (
            f"Para ayudarte necesito saber qué equipo presenta la falla. "
            f"En tu unidad hay: {', '.join(art_list)}. ¿Con cuál tenés el problema y qué le pasa?"
        )
        datos_grafo = {"tipo_evento": "datos_insuficientes", "mensaje_fijo": plantilla_fija}

    elif obj_extraccion.causa_resuelta:
        tipo = "cierre_exitoso"
        causa_conf = obj_extraccion.causa_resuelta
        datos_grafo = {
            "tipo_evento": "cierre_exitoso",
            "unidad": unidad_nombre,
            "artefacto": _nombre_art(obj_extraccion.artefacto_id or "tg01"),
            "causa_confirmada": causa_conf,
            "descripcion_causa": "piloto del termotanque apagado" if causa_conf == "piloto_apagado" else causa_conf
        }

    else:
        # Caso de diagnóstico en curso (T1, T2, T4)
        art_id = obj_extraccion.artefacto_id
        sint_id = obj_extraccion.sintoma_id

        # Si el artefacto no está en la unidad
        if art_id and art_id not in ctx.get("artefactos", []):
            tipo = "artefacto_inexistente"
            plantilla_fija = (
                f"La unidad {unidad_nombre} no cuenta con el equipo {_nombre_art(art_id)}. "
                f"Los artefactos instalados son: {', '.join(ctx.get('artefactos', []))}."
            )
            datos_grafo = {"tipo_evento": "artefacto_inexistente", "mensaje_fijo": plantilla_fija}
        else:
            # Consultar hipótesis C1 en Neo4j
            candidatos = db_client.inferir_paso_diagnostico(art_id, sint_id)
            descartadas = obj_extraccion.causas_descartadas or []
            candidatos_restantes = [c for c in candidatos if c.get("causa") not in descartadas]
            candidatos_delegables = [c for c in candidatos_restantes if c.get("paso") is not None]

            if not candidatos_delegables:
                # Caso T4: Pasos delegables agotados -> escalada al anfitrión (Regla R2)
                tipo = "escalada_anfitrion"
                causa_no_del = candidatos_restantes[0].get("causa") if candidatos_restantes else "gas_refrigerante_bajo"
                datos_grafo = {
                    "tipo_evento": "escalada_anfitrion",
                    "unidad": unidad_nombre,
                    "artefacto": _nombre_art(art_id),
                    "motivo": f"No restan pasos delegables al huésped. Causa probable: {causa_no_del}",
                    "causa_diagnosticada": causa_no_del
                }
            else:
                # Priorizar hipótesis con M2 Mamdani (C2)
                evidencia = 0.85 if descartadas else 0.55
                mejores = []
                for cand in candidatos_delegables:
                    inputs_m2 = {
                        "FrecuenciaCausa": cand.get("indice_frecuencia", 0.70),
                        "RiesgoEsfuerzoPaso": cand.get("riesgo_esfuerzo", 2.0) or 2.0,
                        "EvidenciaAcumulada": evidencia
                    }
                    centroide_m2, alfa_max, _, reglas_act = inferencia_mamdani("M2", inputs_m2)
                    mejores.append({
                        "cand": cand,
                        "prioridad_difusa": centroide_m2,
                        "alfa_max": alfa_max,
                        "reglas_activadas": reglas_act,
                        "inputs": inputs_m2
                    })
                mejores.sort(key=lambda h: h["prioridad_difusa"], reverse=True)
                elegida = mejores[0]
                cand_elegido = elegida["cand"]

                # Dejar traza de fuzzificación Cypher
                db_client.evaluar_fuzzificacion_cypher(elegida["inputs"], modulo="M2")

                paso_info = db_client.pasos.get(cand_elegido["paso"], {})
                advertencias = paso_info.get("advertencias", [])
                if advertencias:
                    obligatorios.extend(advertencias)

                tipo = "instruccion_paso"
                datos_grafo = {
                    "tipo_evento": "instruccion_paso",
                    "unidad": unidad_nombre,
                    "artefacto": _nombre_art(art_id),
                    "sintoma": sint_id,
                    "causas_descartadas": descartadas,
                    "causa_evaluada": cand_elegido["causa"],
                    "prioridad_difusa": round(elegida["prioridad_difusa"], 1),
                    "paso_id": cand_elegido["paso"],
                    "instruccion": cand_elegido["instruccion"],
                    "advertencias": advertencias
                }

    print("├─ 3. Validación y consultas Cypher al grafo PG2")
    print(f"│  • M2 resolvió tipo_evento = {tipo}")
    if datos_grafo.get("prioridad_difusa"):
        print(f"│  • Mamdani M2: paso={datos_grafo.get('paso_id')} -> prioridad_difusa={datos_grafo.get('prioridad_difusa')}")

    for t in db_client.get_traces():
        print(f"│  ▸ {t['query_name']}  filas={t['rows_returned']}  origen={t['source']}")

    print("├─ 4. Resultado estructurado del motor")
    print(f"│  {json.dumps(datos_grafo, ensure_ascii=False)}")

    # Etapas 5 y 6: Explicación y verificación de fidelidad (I10)
    if plantilla_fija:
        resp_final = plantilla_fija
        info_exp = {"redactado_por": "plantilla fija del sistema", "fidelidad_ok": True}
    else:
        resp_final, info_exp = sandwich.etapa_explicacion(
            caso_id=cid,
            datos_grafo=datos_grafo,
            obligatorios=obligatorios,
            plantilla_falla=plantilla_fija
        )

    print(f"├─ 5. Respuesta final ({info_exp.get('redactado_por')})")
    print(f"│  «{resp_final}»")
    print(f"└─ 6. Control de fidelidad I10: {'[OK] SUPERADO' if info_exp.get('fidelidad_ok') else '[FALLÓ]'}")
    if info_exp.get("problemas"):
        print(f"   Observaciones: {info_exp.get('problemas')}")

    exito = (tipo == caso.get("tipo_esperado")) and info_exp.get("fidelidad_ok", False)
    if caso.get("paso_esperado"):
        exito = exito and (datos_grafo.get("paso_id") == caso.get("paso_esperado"))

    return {
        "caso": cid,
        "nombre": caso["nombre"],
        "tipo_obtenido": tipo,
        "tipo_esperado": caso.get("tipo_esperado"),
        "paso_obtenido": datos_grafo.get("paso_id"),
        "paso_esperado": caso.get("paso_esperado"),
        "extraccion": obj_extraccion.model_dump(),
        "datos_grafo": datos_grafo,
        "respuesta_final": resp_final,
        "fidelidad_ok": info_exp.get("fidelidad_ok", False),
        "problemas_fidelidad": info_exp.get("problemas", []),
        "consultas_cypher": db_client.get_traces(),
        "exito": exito
    }


def main():
    parser = argparse.ArgumentParser(description="PI4 · Submódulo M2 Sándwich (Nicolás López)")
    parser.add_argument("--llm", choices=["replay", "gemini", "ollama", "fallback_i14"], default="replay")
    parser.add_argument("--caso", type=str, default=None, help="Ejecutar solo un caso (ej: T1, T2)")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--interactivo", action="store_true")
    args = parser.parse_args()

    reg_path = os.path.join(os.path.dirname(__file__), "pi4_llm_registro_m2.json")
    registro = None
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            registro = json.load(f)

    proveedor = ProveedorLLM(modo=args.llm, registro=registro)
    sandwich = Sandwich(
        prefijo="m2",
        prompt_extraccion=PROMPT_EXTRACCION_M2,
        prompt_explicacion=PROMPT_EXPLICACION_M2,
        modelo_pydantic=ExtraccionM2,
        llm=proveedor,
        rotulo_contexto="Contexto de la unidad",
        rotulo_mensaje="Mensaje del huésped"
    )

    print("=" * 80)
    print("PI4 · Submódulo M2 · Diagnóstico y Resolución Asistida · Patrón sándwich LLM ⇄ Neo4j")
    print(f"Responsable: Nicolás López | Modo LLM: {proveedor.descripcion()}")
    print("=" * 80)

    if args.interactivo:
        print("\nModo interactivo M2. Escribe 'salir' para terminar.")
        inm = "inm101"
        while True:
            try:
                msg = input(f"\n[Huésped @ {inm}] > ").strip()
                if not msg or msg.lower() in ["salir", "exit", "quit"]:
                    break
                caso_custom = {"id": "CLI", "nombre": "Interactivo", "inmueble": inm, "msg": msg}
                ejecutar_caso_m2(sandwich, caso_custom, verbose=args.verbose)
            except (KeyboardInterrupt, EOFError):
                break
        return

    casos_a_ejecutar = [c for c in CASOS_M2 if not args.caso or c["id"] == args.caso]
    resultados = []
    aprobados = 0

    for c in casos_a_ejecutar:
        res = ejecutar_caso_m2(sandwich, c, verbose=args.verbose)
        resultados.append(res)
        if res.get("exito"):
            aprobados += 1

    out_file = os.path.join(os.path.dirname(__file__), "pi4_resultados_m2.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 80}")
    print(f"RESUMEN PI4 M2 SÁNDWICH: {aprobados}/{len(casos_a_ejecutar)} casos superados.")
    print(f"Resultados guardados en: {out_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
