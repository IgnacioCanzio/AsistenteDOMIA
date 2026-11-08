# Manual de Uso del Sistema DOMIA (PG3 · Entrega Grupal)
**Asistente Experto de Conserjería & Triage Asistido para Alquileres Temporarios en Mendoza**  
**Grupo 3 · Comisión 5k9 · UTN Facultad Regional Mendoza · Ciclo Lectivo 2026**  
**Integrantes:** Ignacio Canzio (M1), Nicolás López (M2), Bruno Montero (M3)

---

## 1. Introducción y Arquitectura

DOMIA es una plataforma experta que combina **Modelos de Lenguaje de Gran Escala (LLMs)**, un **Grafo de Conocimiento en Neo4j** y **Lógica Difusa Mamdani** para gestionar incidencias técnicas en unidades de alquiler temporario de manera autónoma, segura y trazable.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 Huésped / Anfitrión                    │
                  └──────────────────────────┬─────────────────────────────┘
                                             │ Mensaje / Respuesta
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             Orquestador Maestro (PG3)                                    │
│   System Prompt Maestro · Enrutamiento contextual · Control de fidelidad · API FastAPI  │
└───────┬────────────────────────────────────┬─────────────────────────────────────┬───────┘
        │                                    │                                     │
        ▼ (Turno 1: Falla inicial)          ▼ (Turnos subsiguientes)              ▼ (Consultas Triage)
┌────────────────────────┐          ┌────────────────────────┐            ┌────────────────────────┐
│     Submódulo M1       │          │     Submódulo M2       │            │     Submódulo M3       │
│ Interpretación Semántica├─────────►│  Diagnóstico Asistido ├───────────►│ Severidad Contextual   │
│   y Diálogo Inicial    │  Reporte │ y Resolución Guiada    │ Diagnóstico│  y Triage al Anfitrión │
└────────────────────────┘          └────────────────────────┘            └────────────────────────┘
        ▲                                    ▲                                     ▲
        │                                    │                                     │
        └────────────────────────────────────┴─────────────────────────────────────┘
                                             ▲
                                  Patrón Sándwich LLM ⇄ Neo4j
                 [Prompt 1 Extracción] ──► [Grafo PG2 / Cypher C1-C9] ──► [Prompt 2 Explicación]
```

### El Patrón Sándwich (LLM ⇄ Neo4j)
En cada módulo (M1, M2 y M3), el LLM nunca razona de forma aislada:
1. **Rebanada Superior (LLM - Extracción)**: Prompt de extracción que genera estrictamente un JSON tipado y validado mediante esquemas Pydantic (`extra="forbid"`).
2. **Relleno Experto (Neo4j & Lógica Difusa)**: Ejecución de consultas Cypher parametrizadas (`C1` a `C9`), inferencia difusa Mamdani y evaluación de reglas nítidas de seguridad.
3. **Rebanada Inferior (LLM - Explicación)**: Prompt de verbalización que redacta la respuesta al usuario basándose exclusivamente en el payload devuelto por el grafo.
4. **Control de Fidelidad I10**: Un validador sintáctico y semántico audita que ningún número haya sido inventado y que todas las advertencias técnicas obligatorias estén presentes.

---

## 2. Requisitos Previos e Instalación

### 2.1 Requisitos de Software
- **Python**: Versión 3.10 o superior (verificado y compatible con Python 3.14).
- **Git** (para clonación del repositorio).
- **Neo4j** (opcional): Instancia Docker o Neo4j Desktop. Si Neo4j no está activo, el sistema conmuta automáticamente al **modo grafo autónomo de respaldo en memoria**, garantizando el 100% de la funcionalidad sin dependencias externas.

### 2.2 Pasos de Instalación
1. Clonar el repositorio y posicionarse en la raíz:
   ```bash
   git clone https://github.com/IgnacioCanzio/AsistenteDOMIA.git
   cd AsistenteDOMIA
   ```
2. Crear y activar el entorno virtual de Python:
   ```powershell
   # En Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instalar las dependencias del proyecto:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno (crear archivo `.env` en la raíz si se desea usar API de Gemini u Ollama):
   ```ini
   # Configuración de LLM
   GEMINI_API_KEY=tu_api_key_aqui
   GEMINI_MODEL=gemini-2.5-flash
   LLM_PROVIDER=replay   # Opciones: replay, gemini, ollama, fallback_i14
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b

   # Configuración de Neo4j
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=domia2026
   NEO4J_DATABASE=neo4j
   USE_MOCK_NEO4J_IF_UNAVAILABLE=true

   # Servidor FastAPI
   APP_HOST=0.0.0.0
   APP_PORT=8000
   DEBUG=true
   ```

---

## 3. Guía de Ejecución

### 3.1 Pruebas y Evaluaciones Individuales (PI4)
Cada integrante dispone de su script individual que ejecuta tanto las pruebas originales como los 8 casos del patrón sándwich:

- **Submódulo M1 (Ignacio Canzio)**:
  ```powershell
  .\venv\Scripts\python.exe pi4_individuales/pi4_m1_canzio.py
  # O ejecución exclusiva del sándwich con parámetros:
  .\venv\Scripts\python.exe pi4_individuales/pi4_m1_canzio_sandwich.py --llm replay
  .\venv\Scripts\python.exe pi4_individuales/pi4_m1_canzio_sandwich.py --caso A2 --verbose
  ```

- **Submódulo M2 (Nicolás López)**:
  ```powershell
  .\venv\Scripts\python.exe pi4_individuales/pi4_m2_lopez.py
  # O ejecución directa del sándwich:
  .\venv\Scripts\python.exe pi4_individuales/pi4_m2_lopez_sandwich.py --llm replay
  .\venv\Scripts\python.exe pi4_individuales/pi4_m2_lopez_sandwich.py --caso T2 --verbose
  ```

- **Submódulo M3 (Bruno Montero)**:
  ```powershell
  .\venv\Scripts\python.exe pi4_individuales/pi4_m3_montero.py
  # O ejecución directa del sándwich:
  .\venv\Scripts\python.exe pi4_individuales/pi4_m3_montero_sandwich.py --llm replay
  .\venv\Scripts\python.exe pi4_individuales/pi4_m3_montero_sandwich.py --caso B2 --verbose
  ```

### 3.2 Modo Interactivo por Consola
Cada script permite interactuar en lenguaje natural en tiempo real escribiendo en la terminal:
```powershell
.\venv\Scripts\python.exe pi4_individuales/pi4_m1_canzio_sandwich.py --interactivo
.\venv\Scripts\python.exe pi4_individuales/pi4_m2_lopez_sandwich.py --interactivo
.\venv\Scripts\python.exe pi4_individuales/pi4_m3_montero_sandwich.py --interactivo
```

### 3.3 Inicio del Servidor Web FastAPI
Para levantar la interfaz gráfica y los endpoints REST de DOMIA:
```powershell
.\venv\Scripts\python.exe run_server.py
```
El servidor quedará disponible en:
- **Interfaz Web**: `http://localhost:8000/`
- **Documentación Interactiva Swagger**: `http://localhost:8000/docs`
- **Documentación ReDoc**: `http://localhost:8000/redoc`

---

## 4. Uso de la Interfaz Web (Panel DOMIA)

La interfaz web de DOMIA está organizada en **tres columnas sincronizadas en tiempo real**:

### Columna 1: Chat del Huésped (Simulador QR)
- **Selector de Departamento**: Permite alternar entre los departamentos (`inm101` a `inm105`), actualizando el inventario de equipamiento según el grafo.
- **Sliders de Telemetría**: Permite variar la temperatura actual (°C) y las horas restantes de estadía para comprobar el impacto en el triage difuso.
- **Botonera de Presets de Prueba**: Accesos directos para disparar los casos canónicos del trabajo práctico:
  - *0. Capacidades (I14)*
  - *1. Agua fría (tg01)*
  - *2. Cerradura bloqueada (cer01)*
  - *3. Ambigüedad Depto 104 (Gas vs Eléctrico)*
  - *4. Ola de calor Split AC (spl01)*
  - *5. ¡Olor a gas! (Alarma crítica de seguridad)*
  - *6. Fuera de dominio (I13)*
  - *7. Artefacto inexistente (I8)*
  - *8. Alarma negada (I2)*
  - *M3: Consultas de Triage en lenguaje natural (Split 103, Cerradura 102, Límite 104)*
- **Botonera Interactiva de Pasos**: Cuando M2 indica un paso de comprobación técnica, aparecen botones interactivos (`✓ Sí, funcionó`, `✗ No funcionó`, `⚠️ No puedo / No sé`) o pills de opciones de aclaración.

### Columna 2: Panel de Triage del Anfitrión
- **Banner de Alertas de Emergencia en Tiempo Real**: Notificaciones rojas destacadas que informan de inmediato cualquier evacuación o protocolo crítico activado (fuga de gas, fuego, disyuntor).
- **Métricas Clave de Triage**: Contadores en vivo de incidencias críticas (Nivel 5), altas (Nivel 4), medias (Nivel 3) y resueltas silenciosamente por el huésped (S2 / Nivel 0).
- **Lista de Fichas de Incidencias**: Tarjetas interactivas con el estado de cada reporte, servicio afectado, causa diagnosticada y canal asignado (`alerta_inmediata`, `cola_priorizada`, `reporte_diario`, `sin_aviso`).
- **Aviso Redactado para el Anfitrión**: Notificación ejecutiva verbalizada por Gemini respetando la Regla I10.

### Columna 3: Inspector de Trazabilidad y Grafo Neo4j
- **Pestaña "Traza en Vivo"**: Desglose paso a paso de lo evaluado por M1 (suficiencia difusa), M2 (priorización de hipótesis) y M3 (centroide de severidad y piso esencial R5).
- **Pestaña "Sándwich LLM"**: Muestra el JSON estricto extraído en la etapa 1, las consultas Cypher ejecutadas con sus parámetros y el resultado del control sintáctico de fidelidad I10.
- **Pestaña "10 Casos Difusos"**: Tabla comparativa con la validación de los 10 centroides de calibración de Marco 2 respecto de la referencia de PI3.
- **Pestaña "Reglas Nítidas"**: Resumen explicativo de las reglas expertas aplicadas (`I1`, `I2`, `I8`, `I11`, `I12`, `R2`, `R3`, `R5`, `R8`, `R9`, `R10`, `S1`, `S2`, `S4`, `S5`).

---

## 5. Casos de Uso Canónicos y Demostración

| Caso | Entrada / Acción | Módulo Líder | Comportamiento Esperado |
|---|---|---|---|
| **Caso 1** | «Hola, no tengo agua caliente en la ducha» | M1 → M2 | Identifica `tg01` y `sin_agua_caliente`. Propone `p1` (llave de gas). Al responder 'no', propone `p2` (piloto). Al responder 'sí', cierra con R3 / S2 (`sin_aviso`). |
| **Caso 2** | «El teclado de la cerradura no reacciona» | M1 → M2 → M3 | Identifica `cer01`. Al fallar `p3`, escala por mecanismo trabado. M3 asigna piso mínimo de Nivel 4 (Alta) por servicio esencial (`acceso_principal`) y canal `alerta_inmediata`. |
| **Caso 3** | «No anda el agua caliente» en Depto 104 | M1 | Detecta ambigüedad (unidad con termotanque a gas y eléctrico). Emite pregunta aclaratoria sin inventar artefactos. |
| **Caso 4** | «El split tira aire caliente en vez de frío» (38°C, 48h) | M1 → M2 → M3 | Huésped limpia filtros (`p10`). Falla persiste. Siguiente causa (`p11` gas refrigerante) es no delegable (R2). Escala a M3. Mamdani evalúa centroide 76.5 -> Nivel 4 (Alta) con `alerta_inmediata`. |
| **Caso 5** | «Siento un fuerte olor a gas en la cocina» | M1 → M2 → M3 | Barrera de seguridad `I1 → R1 → S1`. Aborta diagnóstico inmediatamente. Emite plantilla inmutable `I11` al huésped, asigna Nivel 5 Emergencia y despacha Alerta de Emergencia en el panel del anfitrión. |
| **Caso 6** | «¿Me recomendás restaurantes para cenar?» | M1 | Fuera de dominio (I13). Responde cordialmente delimitando su alcance a soporte técnico y conserjería del departamento. |

---

## 6. Catálogo de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/chat/message` | Procesa un mensaje del huésped o anfitrión en lenguaje natural. |
| `POST` | `/api/chat/step-response` | Envía la respuesta a un paso técnico de diagnóstico asistido (`si`, `no`, `no_puedo`). |
| `POST` | `/api/chat/clarification` | Envía la elección ante una pregunta aclaratoria de ambigüedad. |
| `POST` | `/api/triage/query` | Consulta en lenguaje natural sobre el estado de incidencias mediante el Sándwich M3. |
| `GET` | `/api/alerts` | Lista las alertas de emergencia despachadas en tiempo real. |
| `GET` | `/api/incidents` | Retorna todas las fichas de incidencia registradas con su triage. |
| `GET` | `/api/neo4j/trace/{id}` | Retorna la trazabilidad gráfica y relaciones en Neo4j de una incidencia. |
| `GET` | `/api/neo4j/fuzzy-cases` | Retorna los 10 casos difusos calibrados de Marco 2. |
| `GET` | `/api/inmuebles` | Retorna el catálogo de unidades y artefactos registrados. |
| `GET` | `/api/health` | Estado del backend, conexión a Neo4j y modelo LLM configurado. |

---

## 7. Solución de Problemas Frecuentes

1. **¿Qué ocurre si no tengo una API Key de Gemini configurada?**
   - El sistema conmuta automáticamente al modo `replay` o `fallback_i14`. Los 24 casos sándwich de PI4 y las pruebas grupales funcionarán de manera idéntica y determinística utilizando los registros reales almacenados en `pi4_individuales/pi4_llm_registro_m*.json`.
2. **¿Qué ocurre si no está encendido el servidor Neo4j?**
   - El cliente `Neo4jClient` detecta la indisponibilidad de la conexión en el puerto 7687 y activa su **almacén de respaldo en memoria**, ejecutando las consultas Cypher de forma emulada sin fallar ningún test.
3. **¿Cómo se prueban los modelos locales Ollama?**
   - Asegurarse de tener Ollama corriendo (`ollama run llama3.2:3b`), configurar `LLM_PROVIDER=ollama` en `.env` o pasar `--llm ollama` al invocar los scripts de evaluación.
