"""
src/llm/gemini_client.py - Cliente de Integración con Google Gemini API
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import os
import json
import re
from typing import Dict, Any, Optional
from src.config import settings
from src.llm.prompts import (
    I11_PLANTILLA_EMERGENCIA_FIJA,
    MASTER_ROUTER_SYSTEM_PROMPT,
    M1_EXTRACTION_SYSTEM_PROMPT,
    M1_CLARIFICATION_SYSTEM_PROMPT,
    M2_VERBALIZATION_SYSTEM_PROMPT,
    M3_HOST_NOTIFICATION_SYSTEM_PROMPT
)

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        # Detectar si la API key es vacía o es el placeholder por defecto de .env / .env.example
        if self.api_key and not any(p in self.api_key.lower() for p in ["tu_api_key", "your_api_key", "placeholder", "aqui", "pegale"]):
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                print(f"[+] GeminiClient inicializado con modelo {self.model_name}.")
            except Exception as e:
                print(f"[-] No se pudo inicializar google-genai Client: {e}. Se utilizará modo determinístico I14.")
                self._client = None
        else:
            self.api_key = ""
            print("[INFO] GEMINI_API_KEY no configurada (o en valor placeholder). Operando en modo determinístico conforme a regla I14.")

    def extract_incident_intent(self, user_text: str, contexto_inmueble: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submódulo M1: Extrae artefacto, síntoma, polaridad y señales de alarma.
        Aplica filtro de seguridad I1 / I2 antes de invocar el modelo.
        """
        # Pre-filtro determinístico de seguridad I1 / I2
        es_seguridad, termino, alarma_negada = self._detectar_alarma_seguridad(user_text)
        if es_seguridad:
            return {
                "artefacto_mencionado": "tg03" if "cocina" in user_text.lower() else "tg01",
                "sintoma_identificado": "olor_a_gas",
                "confianza_extraccion": 1.0,
                "polaridad": "afirmativa",
                "es_alarma": True,
                "alarma_negada": False,
                "termino_alarma": termino,
                "fuera_de_dominio": False,
                "mencion_artefacto_texto": "instalación de gas"
            }

        # Intentar extracción con Gemini API usando Structured Outputs (JSON mode, temperature=0.0)
        if self._client:
            try:
                from google.genai import types
                prompt = f"{M1_EXTRACTION_SYSTEM_PROMPT}\n\nContexto del inmueble: {json.dumps(contexto_inmueble or {})}\n\nRelato del huésped: \"{user_text}\""
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )
                text = response.text
                extracted = self._parse_json(text)
                if extracted:
                    # Robustez ante mención de fallas generales (no es consulta de capacidades)
                    if any(w in user_text.lower() for w in ['problema', 'falla', 'desperfecto', 'no funciona', 'no anda', 'se rompio', 'se rompió']):
                        extracted['es_consulta_capacidades'] = False

                    # Si el usuario menciona termotanque y que no enciende / no prende, asociar con sin_agua_caliente
                    if not extracted.get('sintoma_identificado') and any(w in user_text.lower() for w in ['termotanque', 'calefon', 'calefón']) and any(w in user_text.lower() for w in ['no enciende', 'no prende', 'apagado', 'no arranca']):
                        extracted['sintoma_identificado'] = 'sin_agua_caliente'

                    if alarma_negada:
                        extracted["es_alarma"] = False
                        extracted["alarma_negada"] = True
                        extracted["termino_alarma"] = termino
                        extracted["polaridad"] = "negativa"
                    elif es_seguridad:
                        extracted["es_alarma"] = True
                        extracted["alarma_negada"] = False
                        extracted["termino_alarma"] = termino
                    return extracted
            except Exception as e:
                print(f"[-] Error en llamada a Gemini API ({e}). Activando fallback determinístico I14.")
                self._client = None

        # Fallback determinístico (Regla I14)
        res = self._fallback_deterministico_m1(user_text, contexto_inmueble)
        if alarma_negada:
            res["alarma_negada"] = True
            res["termino_alarma"] = termino
            res["polaridad"] = "negativa"
        return res

    def verbalize_step(self, instruccion_data: Dict[str, Any]) -> str:
        """
        Submódulo M2: Verbaliza un paso técnico para el huésped respetando fielmente el payload (I10).
        """
        paso_id = instruccion_data.get('paso_id', '')
        instruccion = instruccion_data.get('instruccion', '')
        advertencias = instruccion_data.get('advertencias', [])

        if self._client:
            try:
                prompt = (
                    f"{M2_VERBALIZATION_SYSTEM_PROMPT}\n\n"
                    f"Paso ID: {paso_id}\n"
                    f"Instrucción base: {instruccion}\n"
                    f"Advertencias obligatorias: {advertencias}\n\n"
                    f"Redacta el mensaje para el huésped:"
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                txt = response.text.strip()
                # Regla I10: Verificar fidelidad. Si omite el texto base o advertencia, usamos texto base directo
                if instruccion.lower()[:15] in txt.lower():
                    return txt
            except Exception as e:
                print(f"[-] Error verbalizando con Gemini: {e}")
                self._client = None

        # Fallback determinístico directo
        msg = f"Por favor realice la siguiente comprobación:\n👉 {instruccion}"
        if advertencias:
            msg += "\n⚠️ Advertencias importantes:\n" + "\n".join(f"• {adv}" for adv in advertencias)
        return msg

    def verbalize_step_instruction(self, instruccion_data: Dict[str, Any]) -> str:
        """Alias para verbalize_step."""
        return self.verbalize_step(instruccion_data)

    def redact_host_notification(self, ficha_data: Dict[str, Any]) -> str:
        """
        Submódulo M3: Redacta la notificación ejecutiva para el anfitrión según la Ficha de Incidencia.
        """
        if self._client:
            try:
                prompt = (
                    f"{M3_HOST_NOTIFICATION_SYSTEM_PROMPT}\n\n"
                    f"Ficha de Incidencia estructurada:\n{json.dumps(ficha_data, indent=2, ensure_ascii=False)}\n\n"
                    f"Redacta la notificación para el anfitrión:"
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                print(f"[-] Error redactando con Gemini: {e}")
                self._client = None

        # Fallback determinístico estructurado
        inc_id = ficha_data.get('incidencia_id', 'inc-?')
        inmueble = ficha_data.get('inmueble_nombre', 'Inmueble')
        causa = ficha_data.get('causa_diagnosticada', 'No determinada')
        nivel = ficha_data.get('nivel_final', 3)
        prioridad = ficha_data.get('prioridad', 'Media')
        canal = ficha_data.get('canal', 'cola_priorizada')
        via = ficha_data.get('via_evaluacion', 'difusa')

        return (
            f"🔔 [NOTIFICACIÓN DE TRIAGE DOMIA]\n"
            f"• Incidencia: {inc_id} en {inmueble}\n"
            f"• Diagnóstico técnico: {causa.replace('_', ' ').capitalize()}\n"
            f"• Nivel de Severidad: {nivel}/5 ({prioridad}) | Vía: {via}\n"
            f"• Canal asignado: {canal}\n"
            f"• Acción requerida: Notificación al anfitrión y asignación de asistencia técnica."
        )

    def verbalize_host_notification(self, ficha_data: Dict[str, Any]) -> str:
        """Alias para redact_host_notification."""
        return self.redact_host_notification(ficha_data)

    # --------------------------------------------------------------------------
    # Reglas de Seguridad y Fallbacks Determinísticos
    # --------------------------------------------------------------------------

    def _detectar_alarma_seguridad(self, texto: str) -> tuple[bool, Optional[str], bool]:
        """
        Reglas I1 e I2: detecta términos de alarma y distingue si están explícitamente negados.
        Retorna: (es_alarma_activa, termino_detectado, es_alarma_negada)
        """
        t = texto.lower()
        alarmas = ['gas', 'humo', 'chispa', 'chispas', 'quemado']
        negada_detectada = None

        # Patrones de negación explícita (Regla I2)
        patrones_negacion = [
            r'\b(?:no\s+(?:hay|huele|sale|se\s+siente|siento|tengo|veo|percibo)?|sin|descarto|cero)\s*(?:\w+\s+){0,3}(?:gas|humo|chispa|chispas|quemado)\b',
            r'\b(?:gas|humo|chispa|chispas|quemado)\s+(?:no\s+hay|no\s+se\s+siente|descartado)\b',
            r'\bno\s+hay\s+olor\s+a\s+gas\b',
            r'\btampoco\s+(?:hay|siento|huele)\s+(?:olor\s+a\s+)?gas\b'
        ]
        es_negada = any(re.search(p, t) for p in patrones_negacion)

        for al in alarmas:
            raiz_al = 'chispa' if al.startswith('chispa') else al
            if re.search(r'\b' + al + r'\b', t):
                if es_negada:
                    negada_detectada = raiz_al
                    continue

                # Hallazgo #5: Si el término es 'gas', exigir contexto de peligro, fuga u olor
                if al == 'gas':
                    indicios_peligro = ['olor', 'huele', 'fuga', 'perdida', 'pérdida', 'escape', 'siento', 'sale', 'fuerte', 'mucho', 'intenso', 'respiro', 'peligro']
                    tiene_peligro = any(w in t for w in indicios_peligro)
                    if not tiene_peligro:
                        continue

                return True, raiz_al, False

        if negada_detectada:
            return False, negada_detectada, True
        return False, None, False

    def _fallback_deterministico_m1(self, user_text: str, contexto_inmueble: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Regla I14: Extracción semántica basada en patrones léxicos sobre Vocabulario Controlado.
        """
        t = user_text.lower()

        # Detección de fuera de dominio (Regla I13)
        if any(w in t for w in ['restaurante', 'turismo', 'bodega', 'excursion', 'vuelo', 'museo', 'clima en la ciudad', 'taxi', 'supermercado']):
            return {
                "artefacto_mencionado": None,
                "sintoma_identificado": None,
                "confianza_extraccion": 0.2,
                "polaridad": "afirmativa",
                "es_alarma": False,
                "alarma_negada": False,
                "termino_alarma": None,
                "fuera_de_dominio": True,
                "es_consulta_capacidades": False,
                "mencion_artefacto_texto": None
            }

        # Detección de consulta sobre capacidades / ayuda general / saludo (Regla I14)
        patrones_capacidades = [
            'con que cosas me puede ayudar', 'con que cosas me podes ayudar', 'con qué cosas me podés ayudar',
            'con que me podes ayudar', 'con qué me podés ayudar', 'con que puedes ayudar', 'con qué puedes ayudar',
            'en que me podes ayudar', 'en qué me podés ayudar', 'en que podes ayudar', 'en qué podés ayudar',
            'en que me puedes ayudar', 'en qué me puedes ayudar', 'en que puedes ayudar',
            'que cosas podes hacer', 'qué cosas podés hacer', 'que podes hacer', 'qué podés hacer',
            'que puedes hacer', 'qué puedes hacer', 'para que servis', 'para qué servís',
            'como funciona', 'cómo funciona', 'que funciones tenes', 'qué funciones tenés',
            'quien sos', 'quién sos', 'que sos', 'qué sos', 'como me podes ayudar', 'cómo me podés ayudar',
            'con que me ayudas', 'con qué me ayudas', 'que podes solucionar', 'qué podés solucionar'
        ]
        saludos_solos = [
            'hola', 'hola!', 'buenas', 'buen dia', 'buen día', 'buenas tardes', 'buenas noches',
            'hola domia', 'ayuda', 'ayuda por favor', 'menu', 'inicio', 'hola!'
        ]
        
        palabras_sintomas = [
            'agua', 'caliente', 'fria', 'fría', 'ducha', 'termotanque', 'calefon', 'calefón',
            'aire', 'split', 'enfria', 'enfría', 'cerradura', 'puerta', 'teclado', 'codigo', 'código',
            'disyuntor', 'termica', 'térmica', 'falla', 'rompio', 'rompió', 'problema', 'no anda', 'no funciona',
            'no abre', 'bloquead', 'olor', 'gas', 'fuego', 'humo', 'chispa'
        ]
        tiene_sintoma_aparente = any(w in t for w in palabras_sintomas)

        if not tiene_sintoma_aparente and (any(p in t for p in patrones_capacidades) or t.strip() in saludos_solos):
            return {
                "artefacto_mencionado": None,
                "sintoma_identificado": None,
                "confianza_extraccion": 0.95,
                "polaridad": "afirmativa",
                "es_alarma": False,
                "alarma_negada": False,
                "termino_alarma": None,
                "fuera_de_dominio": False,
                "es_consulta_capacidades": True,
                "mencion_artefacto_texto": None
            }

        sintoma = None
        artefacto = None
        mencion_texto = None
        confianza = 0.50

        # Detección de artefactos no existentes o específicos (Regla I8)
        for eq_inexistente in ['jacuzzi', 'lavavajillas', 'hidromasaje', 'piscina', 'calefon solar', 'sauna', 'microondas']:
            if eq_inexistente in t:
                return {
                    "artefacto_mencionado": eq_inexistente.replace(" ", "_"),
                    "sintoma_identificado": "falla_general",
                    "confianza_extraccion": 0.90,
                    "polaridad": "afirmativa",
                    "es_alarma": False,
                    "alarma_negada": False,
                    "termino_alarma": None,
                    "fuera_de_dominio": False,
                    "mencion_artefacto_texto": eq_inexistente
                }

        # Regla R9: Disparo repetido de disyuntor / térmica en Tablero Eléctrico
        if any(w in t for w in ['disyuntor', 'salta la termica', 'vuelve a saltar', 'corta la luz cada vez', 'salta el diferencial']):
            return {
                "artefacto_mencionado": "tab01",
                "sintoma_identificado": "disparo_repetido_disyuntor",
                "confianza_extraccion": 0.92,
                "polaridad": "afirmativa",
                "es_alarma": False,
                "alarma_negada": False,
                "termino_alarma": None,
                "fuera_de_dominio": False,
                "mencion_artefacto_texto": "tablero eléctrico"
            }

        # Regla R10: Causa común en servicio compartido (agua potable / corte general)
        if any(w in t for w in ['no sale agua de ninguna canilla', 'sin agua potable', 'cortaron el agua', 'todo el edificio sin agua', 'no hay agua en todo el depto']):
            return {
                "artefacto_mencionado": "red_agua",
                "sintoma_identificado": "sin_suministro_agua_potable",
                "confianza_extraccion": 0.92,
                "polaridad": "afirmativa",
                "es_alarma": False,
                "alarma_negada": False,
                "termino_alarma": None,
                "fuera_de_dominio": False,
                "mencion_artefacto_texto": "red de agua potable"
            }

        # Mapeo a Vocabulario Controlado estándar
        if any(w in t for w in ['cerradura', 'puerta', 'teclado', 'codigo', 'código', 'no abre', 'bloquead', 'clave']):
            sintoma = 'teclado_sin_respuesta'
            artefacto = 'cer01'
            mencion_texto = 'cerradura electrónica'
            confianza = 0.90

        elif any(w in t for w in ['aire', 'split', 'no enfria', 'no enfría', 'calor', 'climatizador']):
            sintoma = 'no_enfria'
            artefacto = 'spl01'
            mencion_texto = 'aire acondicionado split'
            confianza = 0.88

        elif any(w in t for w in ['agua caliente', 'ducha', 'no calienta', 'agua tibia', 'agua fria', 'termotanque', 'piloto', 'calefon']):
            sintoma = 'sin_agua_caliente'
            confianza = 0.85
            mencion_texto = 'termotanque'
            if 'baño' in t or 'electrico' in t or 'eléctrico' in t:
                artefacto = 'te01'
            elif 'cocina' in t or 'gas' in t:
                artefacto = 'tg01'
            else:
                artefacto = 'tg01'

        return {
            "artefacto_mencionado": artefacto,
            "sintoma_identificado": sintoma,
            "confianza_extraccion": confianza,
            "polaridad": "afirmativa",
            "es_alarma": False,
            "alarma_negada": False,
            "termino_alarma": None,
            "fuera_de_dominio": False,
            "mencion_artefacto_texto": mencion_texto or artefacto
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            clean = re.sub(r'^```json\s*', '', text.strip(), flags=re.MULTILINE)
            clean = re.sub(r'```$', '', clean.strip(), flags=re.MULTILINE)
            return json.loads(clean.strip())
        except Exception:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            return None

# Instancia global singleton
gemini_client = GeminiClient()
