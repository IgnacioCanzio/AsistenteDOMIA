"""
src/llm/sandwich.py - Motor Reutilizable del Patrón Sándwich LLM ⇄ Neo4j
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026

Implementa las 6 etapas del patrón sándwich:
1. Extracción con LLM (Prompt 1) -> JSON estructurado
2. Validación estricta con Pydantic (extra="forbid")
2b. Compuertas determinísticas (Seguridad I1/I2, I13, I14, contexto I8/I12)
3. Consulta Cypher parametrizada al grafo PG2
4. Inferencia determinística y lógica difusa Mamdani
5. Explicación fundamentada con LLM (Prompt 2)
6. Verificación de fidelidad al grafo (Regla I10)
"""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple, List, Type
from pydantic import BaseModel, ValidationError

from src.config import settings
from src.llm.gemini_client import gemini_client


def parsear_json_estricto(texto: str) -> Tuple[Optional[dict], str]:
    """
    Parsea JSON y categoriza el formato devuelto por el LLM:
    - 'json_puro': JSON estricto sin delimitadores adicionales
    - 'json_con_vallas': JSON envuelto en bloques ```json ... ```
    - 'json_con_texto': JSON embebido con texto adicional antes/después
    - 'invalido': no contiene JSON válido
    """
    t = (texto or "").strip()
    try:
        return json.loads(t), "json_puro"
    except Exception:
        pass

    m = re.match(r"^```(?:json)?\s*(\{.*\})\s*```$", t, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1)), "json_con_vallas"
        except Exception:
            pass

    m = re.search(r"\{.*\}", t, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0)), "json_con_texto"
        except Exception:
            pass

    return None, "invalido"


def _extraer_numeros(texto: str) -> List[str]:
    """Extrae secuencias numéricas (enteros y decimales) de un texto o JSON."""
    nums = re.findall(r"\b\d+(?:[\.,]\d+)?\b", texto)
    res = []
    for n in nums:
        norm = n.replace(",", ".")
        res.append(norm)
    return res


def verificar_fidelidad(respuesta: str, datos: dict, obligatorios: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Regla I10: Control de fidelidad de la respuesta generada por el LLM:
    1. Toda cifra numérica presente en la respuesta debe existir en los datos del grafo.
       (Se admiten números de formato habitual 0..10 para pasos/niveles y redondeos enteros).
    2. Todo texto obligatorio (ej. advertencias técnicas o notas preventivas) debe aparecer.
    """
    problemas = []
    obligatorios = obligatorios or []

    # Cifras autorizadas provenientes del resultado estructurado
    permitidos = set(_extraer_numeros(json.dumps(datos, ensure_ascii=False, default=str)))
    permitidos |= {str(x) for x in range(0, 11)}  # 'nivel 4', 'paso 1', etc.

    # Agregar variantes redondeadas (ej. 50.1 -> 50, 8.3 -> 8)
    ext = set()
    for n in list(permitidos):
        try:
            ext.add(str(int(round(float(n)))))
        except ValueError:
            pass
    permitidos |= ext

    # Comprobar cifras en la respuesta del modelo
    for n in _extraer_numeros(respuesta):
        if n not in permitidos:
            problemas.append(f"cifra '{n}' no proviene del grafo")

    # Comprobar advertencias obligatorias
    base = respuesta.lower()
    for ob in obligatorios:
        if not ob:
            continue
        # Limpiar referencias técnicas entre paréntesis (ej: "(Regla I2)") ya que los prompts prohíben nombrar reglas
        ob_limpio = re.sub(r"\(regla\s+[a-z0-9_]+\)\s*:?", "", ob, flags=re.IGNORECASE)
        palabras = [w for w in re.split(r"\W+", ob_limpio.lower()) if len(w) > 3]
        if palabras:
            coincidencias = sum(1 for p in palabras if p in base)
            ratio = coincidencias / len(palabras)
            if ratio < 0.4:
                problemas.append(f"falta advertencia obligatoria: «{ob[:40]}…»")
        else:
            clave = ob_limpio.lower()[:20].strip()
            if clave and clave not in base:
                problemas.append(f"falta advertencia obligatoria: «{ob[:40]}…»")

    es_fiel = len(problemas) == 0
    return es_fiel, problemas


class ProveedorLLM:
    """Proveedor unificado para llamadas al LLM en modos Gemini, Ollama o Replay."""

    def __init__(self, modo: str = "replay", registro: Optional[Dict[str, str]] = None):
        self.modo = modo
        self.registro = registro or {}

    def descripcion(self) -> str:
        if self.modo == "gemini":
            return f"Gemini API ({settings.GEMINI_MODEL})"
        if self.modo == "ollama":
            return f"Ollama Local ({getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b')})"
        if self.modo == "replay":
            return "REPLAY: respuestas registradas de Gemini"
        return "FALLBACK determinístico (Regla I14)"

    def generar(self, clave_registro: str, prompt: str, es_json: bool = False) -> Optional[str]:
        # Modo REPLAY
        if self.modo == "replay":
            if clave_registro in self.registro:
                return self.registro[clave_registro]
            # Si no está en el registro para esa clave puntual, fallback
            return None

        # Modo GEMINI API
        if self.modo == "gemini":
            if gemini_client._client:
                try:
                    from google.genai import types
                    cfg = types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json" if es_json else "text/plain"
                    )
                    resp = gemini_client._client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=prompt,
                        config=cfg
                    )
                    return resp.text.strip()
                except Exception as e:
                    print(f"[-] Error llamando a Gemini API: {e}")
            return None

        # Modo OLLAMA LOCAL
        if self.modo == "ollama":
            url = f"{getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate"
            body = {
                "model": getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b'),
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
            if es_json:
                body["format"] = "json"
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as r:
                    res = json.loads(r.read().decode("utf-8"))
                    return res.get("response", "").strip()
            except Exception as e:
                print(f"[-] Error llamando a Ollama en {url}: {e}")
            return None

        return None


class Sandwich:
    """Implementa el flujo sándwich: Extracción -> Validación -> Explicación -> Control I10."""

    def __init__(
        self,
        prefijo: str,
        prompt_extraccion: str,
        prompt_explicacion: str,
        modelo_pydantic: Type[BaseModel],
        llm: ProveedorLLM,
        rotulo_contexto: str = "Contexto",
        rotulo_mensaje: str = "Mensaje del usuario"
    ):
        self.prefijo = prefijo
        self.prompt_extraccion = prompt_extraccion
        self.prompt_explicacion = prompt_explicacion
        self.Modelo = modelo_pydantic
        self.llm = llm
        self.rot_ctx = rotulo_contexto
        self.rot_msg = rotulo_mensaje

    def etapa_extraccion(
        self,
        caso_id: str,
        mensaje: str,
        contexto: Dict[str, Any],
        fallback_fn
    ) -> Tuple[Optional[BaseModel], Dict[str, Any]]:
        """Etapas 1 y 2: extracción mediante LLM y validación estricta Pydantic."""
        prompt = (
            f"{self.prompt_extraccion}\n\n"
            f"{self.rot_ctx}: {json.dumps(contexto, ensure_ascii=False)}\n\n"
            f"{self.rot_msg}: \"{mensaje}\""
        )
        info = {
            "prompt": prompt,
            "origen": self.llm.descripcion()
        }
        crudo = None
        try:
            clave = f"{self.prefijo}/{caso_id}/extraccion"
            crudo = self.llm.generar(clave, prompt, es_json=True)
        except Exception as e:
            info["error_llm"] = str(e)

        if crudo is None:
            # Fallback determinístico (Regla I14)
            raw_fallback = fallback_fn(mensaje, contexto)
            if isinstance(raw_fallback, str):
                datos, _ = parsear_json_estricto(raw_fallback)
                info.update(crudo=raw_fallback, formato="fallback_i14")
            else:
                datos = raw_fallback
                info.update(crudo=json.dumps(datos, ensure_ascii=False), formato="fallback_i14")
        else:
            datos, formato = parsear_json_estricto(crudo)
            info.update(crudo=crudo, formato=formato)
            if datos is None:
                info["error"] = "La respuesta del modelo no es un JSON válido."
                return None, info

        try:
            obj = self.Modelo(**datos)
            return obj, info
        except ValidationError as e:
            info["error"] = "El JSON no cumple el esquema estricto: " + "; ".join(
                f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors()
            )
            return None, info

    def etapa_explicacion(
        self,
        caso_id: str,
        datos_grafo: Dict[str, Any],
        obligatorios: Optional[List[str]] = None,
        plantilla_falla: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Etapas 5 y 6: explicación con LLM basada en datos del grafo y verificación de fidelidad I10."""
        prompt = (
            f"{self.prompt_explicacion}\n\n"
            f"Datos recuperados de Neo4j (única fuente permitida):\n"
            f"{json.dumps(datos_grafo, ensure_ascii=False, indent=2)}\n\n"
            f"Redacta la respuesta para el usuario:"
        )
        info = {
            "prompt": prompt,
            "origen": self.llm.descripcion()
        }
        crudo = None
        try:
            clave = f"{self.prefijo}/{caso_id}/explicacion"
            crudo = self.llm.generar(clave, prompt, es_json=False)
        except Exception as e:
            info["error_llm"] = str(e)

        if crudo is None:
            texto = plantilla_falla or "Hemos procesado su consulta según los registros técnicos de la propiedad."
            info.update(redactado_por="plantilla_fallback", fidelidad_ok=True, problemas=[])
            return texto, info

        fiel, problemas = verificar_fidelidad(crudo, datos_grafo, obligatorios)
        info.update(crudo=crudo, fidelidad_ok=fiel, problemas=problemas)

        if fiel:
            info["redactado_por"] = "llm"
            return crudo, info
        else:
            # Si falla la fidelidad I10, se reemplaza por plantilla determinística
            info["redactado_por"] = "plantilla_por_violacion_i10"
            texto = plantilla_falla or f"Se registró el estado técnico: {json.dumps(datos_grafo, ensure_ascii=False)}."
            return texto, info
