"""
pi4_individuales/pi4_m3_montero_sandwich.py - Submódulo M3 con Patrón Sándwich LLM ⇄ Neo4j
Responsable: Bruno Montero (Submódulo M3: Severidad Contextual, Triage y Notificación)
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

from src.models.schemas import ExtraccionM3, FichaIncidencia
from src.llm.prompts import (
    PROMPT_EXTRACCION_M3,
    PROMPT_EXPLICACION_M3,
    I11_PLANTILLA_EMERGENCIA_FIJA
)
from src.llm.sandwich import Sandwich, ProveedorLLM, verificar_fidelidad
from src.db.neo4j_client import db_client, CASO_DIFUSO_DE_INCIDENCIA
from src.modules.m3_severidad import modulo_m3
from src.llm.gemini_client import gemini_client


CONTEXTO_SISTEMA_M3 = {
    "unidades_registradas": [
        {"id": "inm101", "nombre": "Depto 101"},
        {"id": "inm102", "nombre": "Depto 102"},
        {"id": "inm103", "nombre": "Depto 103"},
        {"id": "inm104", "nombre": "Depto 104"},
        {"id": "inm105", "nombre": "Depto 105"}
    ],
    "servicios_validos": [
        "agua_caliente",
        "acceso_principal",
        "climatizacion",
        "electricidad",
        "agua_potable"
    ]
}


CASOS_M3 = [
    {
        "id": "B1",
        "nombre": "Incidencia difusa pura (aire acondicionado, Depto 103)",
        "inmueble": "inm103",
        "servicio": "climatizacion",
        "msg": "¿Cómo quedó clasificada la incidencia del aire acondicionado del depto 103?",
        "tipo_esperado": "ficha_incidencia"
    },
    {
        "id": "B2",
        "nombre": "Piso de servicio esencial (R5) y pedido de justificación",
        "inmueble": "inm102",
        "servicio": "acceso_principal",
        "msg": "¿Por qué la falla de la cerradura del depto 102 figura con prioridad alta si no hace calor ni queda poco tiempo?",
        "tipo_esperado": "ficha_incidencia"
    },
    {
        "id": "B3",
        "nombre": "Caso límite difuso: estado y canal de aviso (Depto 104)",
        "inmueble": "inm104",
        "servicio": "agua_caliente",
        "msg": "Quiero saber en qué estado quedó la incidencia del termotanque eléctrico del 104 y por dónde se avisa.",
        "tipo_esperado": "ficha_incidencia"
    },
    {
        "id": "B4",
        "nombre": "Cierre silencioso S2: el huésped lo resolvió",
        "inmueble": "inm101",
        "servicio": "agua_caliente",
        "msg": "¿Qué pasó con el termotanque del depto 101? Creo que el huésped lo arregló solo.",
        "tipo_esperado": "ficha_incidencia"
    },
    {
        "id": "B5",
        "nombre": "Emergencia S1: nivel 5 automático",
        "inmueble": "inm105",
        "servicio": None,
        "msg": "Necesito la ficha de la emergencia del depto 105.",
        "tipo_esperado": "ficha_incidencia"
    },
    {
        "id": "E1",
        "nombre": "Consulta fuera de dominio (receta)",
        "inmueble": None,
        "servicio": None,
        "msg": "¿Me pasás una receta de empanadas mendocinas?",
        "tipo_esperado": "fuera_de_dominio"
    },
    {
        "id": "E2",
        "nombre": "Consulta sin unidad identificable",
        "inmueble": None,
        "servicio": None,
        "msg": "¿Cómo quedó la incidencia que reportaron ayer?",
        "tipo_esperado": "datos_insuficientes"
    },
    {
        "id": "E3",
        "nombre": "Unidad inexistente (Depto 107)",
        "inmueble": None,
        "servicio": None,
        "msg": "¿Qué prioridad tiene la falla del jacuzzi del depto 107?",
        "tipo_esperado": "datos_insuficientes"
    }
]


def _fallback_deterministico_m3(mensaje: str, contexto: Dict[str, Any]) -> str:
    """Fallback determinístico para M3 si falla el LLM."""
    m_low = mensaje.lower()
    if any(w in m_low for w in ["receta", "empanada", "turismo", "restaurante", "cine", "clima"]):
        return json.dumps({
            "inmueble_id": None,
            "servicio_id": None,
            "pide_justificacion": False,
            "fuera_de_dominio": True,
            "confianza_extraccion": 1.0
        })

    pide_just = any(w in m_low for w in ["por qué", "porque", "justifica", "motivo", "razón"])

    inm = None
    for i in range(101, 106):
        if str(i) in m_low:
            inm = f"inm{i}"
            break

    serv = None
    if any(w in m_low for w in ["aire", "split", "climatizaci"]):
        serv = "climatizacion"
    elif any(w in m_low for w in ["cerradura", "acceso", "puerta"]):
        serv = "acceso_principal"
    elif any(w in m_low for w in ["agua caliente", "termotanque", "calefon"]):
        serv = "agua_caliente"
    elif any(w in m_low for w in ["luz", "electricidad", "disyuntor", "termica"]):
        serv = "electricidad"
    elif any(w in m_low for w in ["agua potable", "canilla"]):
        serv = "agua_potable"

    conf = 1.0 if inm else 0.5
    return json.dumps({
        "inmueble_id": inm,
        "servicio_id": serv,
        "pide_justificacion": pide_just,
        "fuera_de_dominio": False,
        "confianza_extraccion": conf
    })


def ejecutar_caso_m3(sandwich: Sandwich, caso: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    cid = caso["id"]
    mensaje = caso["msg"]

    print(f"\n{'=' * 80}")
    print(f"CASO {cid} · {caso['nombre']}")
    print(f"{'=' * 80}")
    print(f"┌─ 1. Consulta del usuario\n│  «{mensaje}»")

    db_client.clear_traces()

    # Etapas 1 y 2: Extracción con LLM y validación Pydantic
    obj_extraccion, info_ext = sandwich.etapa_extraccion(
        caso_id=cid,
        mensaje=mensaje,
        contexto=CONTEXTO_SISTEMA_M3,
        fallback_fn=_fallback_deterministico_m3
    )

    print(f"├─ 2. Extracción con LLM -> JSON estricto (prompt 1)")
    print(f"│  Origen: {info_ext.get('origen')} | Formato devuelto: {info_ext.get('formato')}")
    print(f"│  {info_ext.get('crudo')}")
    if info_ext.get("error"):
        print(f"│  [!] Error de validación: {info_ext.get('error')}")

    if not obj_extraccion:
        print("└─ Rechazo temprano por error de extracción.")
        return {"caso": cid, "exito": False, "error": info_ext.get("error")}

    datos_grafo = {}
    obligatorios = []
    plantilla_fija = None
    tipo = "ficha_incidencia"

    # Etapas 3 y 4: De la incidencia a la ficha estructurada (C9, C4, C6, C8)
    if obj_extraccion.fuera_de_dominio:
        tipo = "fuera_de_dominio"
        plantilla_fija = (
            "Solo puedo informar sobre la prioridad y el estado de incidencias técnicas de las unidades. "
            "Para otras consultas, comunicate con el anfitrión."
        )
        datos_grafo = {"tipo_evento": "fuera_de_dominio", "mensaje_fijo": plantilla_fija}

    elif not obj_extraccion.inmueble_id:
        tipo = "datos_insuficientes"
        plantilla_fija = (
            "¿De qué unidad es la incidencia? Las unidades registradas son: "
            "101 (Depto 101), 102 (Depto 102), 103 (Depto 103), 104 (Depto 104), 105 (Depto 105)."
        )
        datos_grafo = {"tipo_evento": "datos_insuficientes", "mensaje_fijo": plantilla_fija}

    else:
        # Consultar C9 en Neo4j
        filas = db_client.buscar_incidencias(obj_extraccion.inmueble_id, obj_extraccion.servicio_id)

        if not filas:
            tipo = "sin_incidencia"
            plantilla_fija = (
                f"No se encontraron incidencias técnicas registradas para la unidad {obj_extraccion.inmueble_id}."
            )
            datos_grafo = {
                "tipo_evento": "sin_incidencia",
                "unidad_consultada": obj_extraccion.inmueble_id,
                "servicio_consultado": obj_extraccion.servicio_id,
                "incidencias_encontradas": 0
            }
        elif len(filas) > 1:
            tipo = "datos_insuficientes"
            plantilla_fija = (
                "Hay varias incidencias en esa unidad: "
                + ", ".join(f"{f['incidencia']} ({f.get('servicio', '')})" for f in filas)
                + ". ¿Sobre cuál querés saber?"
            )
            datos_grafo = {"tipo_evento": "datos_insuficientes", "mensaje_fijo": plantilla_fija}
        else:
            inc_id = filas[0]["incidencia"]
            sev = db_client.evaluar_severidad(inc_id)  # C4
            pay = db_client.get_payload_llm(inc_id) or {}  # C6

            caso_id = CASO_DIFUSO_DE_INCIDENCIA.get(inc_id)
            reglas = db_client.explicar_reglas_activadas(caso_id) if (caso_id and sev and sev.get("via") == "difusa") else []  # C8

            tipo = "ficha_incidencia"
            datos_grafo = {
                "tipo_evento": "ficha_incidencia",
                "incidencia": inc_id,
                "unidad": pay.get("inmueble"),
                "artefacto": pay.get("artefacto"),
                "servicio": pay.get("servicio"),
                "servicio_esencial": pay.get("servicio_esencial"),
                "causa_diagnosticada": pay.get("causa"),
                "resuelta_por_huesped": pay.get("resoluble_por_huesped"),
                "riesgo_seguridad": pay.get("riesgo_seguridad"),
                "temperatura_c": pay.get("temperatura"),
                "horas_restantes": pay.get("horas_restantes"),
                "via_evaluacion": sev.get("via"),
                "puntaje_difuso": sev.get("puntaje"),
                "nivel_calculado": sev.get("nivel_calculado"),
                "piso_minimo_servicio_esencial": sev.get("piso_r5") if pay.get("servicio_esencial") else None,
                "nivel_final": sev.get("nivel_final"),
                "prioridad": sev.get("prioridad"),
                "canal": sev.get("canal"),
                "activacion_maxima": sev.get("activacion_maxima"),
                "reglas_activadas": [
                    {"regla": r["regla"], "alfa": r["alfa"], "consecuente": r["consecuente"]}
                    for r in reglas if r.get("alfa", 0) > 0.05
                ]
            }

    print("├─ 3. Validación y consultas Cypher al grafo PG2")
    print(f"│  • M3 resolvió tipo_evento = {tipo}")
    if datos_grafo.get("incidencia"):
        print(f"│  • C4: incidencia={datos_grafo['incidencia']} · vía={datos_grafo.get('via_evaluacion')} "
              f"· nivel_final={datos_grafo.get('nivel_final')} · prioridad={datos_grafo.get('prioridad')}")

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

    return {
        "caso": cid,
        "nombre": caso["nombre"],
        "tipo_obtenido": tipo,
        "tipo_esperado": caso.get("tipo_esperado"),
        "incidencia": datos_grafo.get("incidencia"),
        "extraccion": obj_extraccion.model_dump(),
        "datos_grafo": datos_grafo,
        "respuesta_final": resp_final,
        "fidelidad_ok": info_exp.get("fidelidad_ok", False),
        "problemas_fidelidad": info_exp.get("problemas", []),
        "consultas_cypher": db_client.get_traces(),
        "exito": exito
    }


def main():
    parser = argparse.ArgumentParser(description="PI4 · Submódulo M3 Sándwich (Bruno Montero)")
    parser.add_argument("--llm", choices=["replay", "gemini", "ollama", "fallback_i14"], default="replay")
    parser.add_argument("--caso", type=str, default=None, help="Ejecutar solo un caso (ej: B1, B2)")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--interactivo", action="store_true")
    args = parser.parse_args()

    reg_path = os.path.join(os.path.dirname(__file__), "pi4_llm_registro_m3.json")
    registro = None
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            registro = json.load(f)

    proveedor = ProveedorLLM(modo=args.llm, registro=registro)
    sandwich = Sandwich(
        prefijo="m3",
        prompt_extraccion=PROMPT_EXTRACCION_M3,
        prompt_explicacion=PROMPT_EXPLICACION_M3,
        modelo_pydantic=ExtraccionM3,
        llm=proveedor,
        rotulo_contexto="Contexto del sistema",
        rotulo_mensaje="Consulta del usuario"
    )

    print("=" * 80)
    print("PI4 · Submódulo M3 · Severidad, Triage y Notificación · Patrón sándwich LLM ⇄ Neo4j")
    print(f"Responsable: Bruno Montero | Modo LLM: {proveedor.descripcion()}")
    print("=" * 80)

    if args.interactivo:
        print("\nModo interactivo M3. Escribe 'salir' para terminar.")
        while True:
            try:
                msg = input("\n[Consulta de Triage] > ").strip()
                if not msg or msg.lower() in ["salir", "exit", "quit"]:
                    break
                caso_custom = {"id": "CLI", "nombre": "Interactivo", "msg": msg}
                ejecutar_caso_m3(sandwich, caso_custom, verbose=args.verbose)
            except (KeyboardInterrupt, EOFError):
                break
        return

    casos_a_ejecutar = [c for c in CASOS_M3 if not args.caso or c["id"] == args.caso]
    resultados = []
    aprobados = 0

    for c in casos_a_ejecutar:
        res = ejecutar_caso_m3(sandwich, c, verbose=args.verbose)
        resultados.append(res)
        if res.get("exito"):
            aprobados += 1

    out_file = os.path.join(os.path.dirname(__file__), "pi4_resultados_m3.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 80}")
    print(f"RESUMEN PI4 M3 SÁNDWICH: {aprobados}/{len(casos_a_ejecutar)} casos superados.")
    print(f"Resultados guardados en: {out_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
