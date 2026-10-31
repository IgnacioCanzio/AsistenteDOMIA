# DOMIA: Sistema Experto de Autodiagnóstico, Resolución Asistida y Triage de Incidencias

**DOMIA** (*Dominio de Operaciones de Mantenimiento e Incidencias Asistidas*) es un sistema experto para la atención técnica de huéspedes en alquileres temporarios y condohoteles.

Desarrollado por el **Grupo 3** (Comisión 5k9 · UTN FRM · 2026):
- **Ignacio Canzio**: Submódulo M1 (Interpretación Semántica, Diálogo y Suficiencia Difusa)
- **Nicolás López**: Submódulo M2 (Diagnóstico Técnico, Descarte R11 y Troubleshooting Asistido)
- **Bruno Montero**: Submódulo M3 (Severidad Contextual S5, Triage Difuso y Ficha para Anfitrión)

---

## 🚀 Puesta en Marcha Rápida (Docker Compose)

La forma más rápida y recomendada de levantar el proyecto completo (Base de datos Neo4j + Backend FastAPI + Interfaz Web) es mediante **Docker Compose**:

### 1. Requisitos Previos
- **Docker Desktop** (con Docker Compose v2) instalado y en ejecución en Windows, Mac o Linux.

### 2. Configurar Variables de Entorno (`.env`)
Crear el archivo `.env` en la raíz del proyecto (o copiarlo desde `.env.example`):
```bash
cp .env.example .env
```

Contenido del archivo `.env`:
```env
# Clave de Google AI Studio para verbalización y extracción semántica (opcional)
# Si se deja vacía o con el placeholder, opera 100% en modo experto determinístico (Regla I14)
GEMINI_API_KEY=tu_api_key_de_google_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash

# Conexión a la base de conocimiento Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=domia2026
NEO4J_DATABASE=neo4j
USE_MOCK_NEO4J_IF_UNAVAILABLE=true
```

> [!NOTE]
> La `GEMINI_API_KEY` es **opcional**. Si no tenés una clave de Google AI Studio, el sistema activa automáticamente el motor determinístico conforme a la regla **I14**, permitiendo probar el 100% de los flujos, reglas y diagnósticos sin depender de servicios externos.

---

### 3. Levantar Todo con un Solo Comando

Ejecutá en la terminal desde el directorio raíz del proyecto:

```powershell
docker compose up -d --build
```

*(El flag `--build` asegura compilar la imagen de la aplicación con los últimos cambios de código).*

#### ¿Qué sucede de forma 100% automática?
1. Se levanta el contenedor `domia-neo4j` (Neo4j Community 5.26 en puertos `7474` y `7687`).
2. Se compila y levanta `domia-backend` (FastAPI en puerto `8000`).
3. **Auto-aprovisionamiento del Grafo**: Al iniciar, FastAPI detecta si la base de datos de Neo4j está limpia y ejecuta automáticamente los 6 scripts Cypher de carga, poblando los **228 nodos y 353 relaciones** sin requerir ninguna acción manual adicional.

---

### 4. Puntos de Acceso en tu Navegador

Una vez que los contenedores estén corriendo, ya podés acceder directamente a:

| Servicio | URL | Descripción / Credenciales |
| :--- | :--- | :--- |
| **Aplicación Web DOMIA** | [http://localhost:8000](http://localhost:8000) | **UI interactiva de 3 paneles**: Chat huésped, Panel de triage y trazabilidad Cypher en vivo |
| **Neo4j Browser** | [http://localhost:7474](http://localhost:7474) | Explorador visual del grafo (`neo4j` / `domia2026`) |
| **Documentación API (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Especificación interactiva OpenAPI de todos los endpoints |

---

### 5. Comandos Útiles de Docker

```powershell
# Ver el estado de los contenedores
docker compose ps

# Ver logs en tiempo real (FastAPI y Neo4j)
docker compose logs -f

# Ver logs únicamente del backend
docker compose logs -f domia-app

# Detener los contenedores (conservando los datos de la base)
docker compose down

# Detener y reiniciar limpiando volúmenes de datos
docker compose down -v
```

---

## 💻 Alternativa: Ejecución Local en Entorno Virtual (Sin Docker)

Si preferís correr la aplicación directamente con Python en tu máquina:

### 1. Requisitos Previos
- **Python 3.10+** (probado en Python 3.11, 3.12 y 3.14).
- Opcional: Contenedor Neo4j corriendo de fondo (`docker compose up -d neo4j`). Si Neo4j no está disponible, el sistema conmuta automáticamente a su almacén de grafo en memoria sin interrumpir el funcionamiento.

### 2. Crear y Activar Entorno Virtual
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 4. Inicializar y Verificar Base de Conocimiento Neo4j
Si tenés el contenedor de Neo4j levantado, podés cargar y verificar la base de conocimiento con:
```powershell
python pg2_neo4j/verificacion/init_and_verify_db.py
```
*(Valida restricciones, carga los 6 scripts Cypher y comprueba los 228 nodos y 353 relaciones exactas).*

### 5. Iniciar Servidor FastAPI
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Acceder en el navegador a: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias, de integración y de extremo a extremo (E2E):

```powershell
# 1. Pruebas individuales de cada integrante (PI4):
python pi4_individuales/pi4_m1_canzio.py   # 6/6 casos superados (Interpretación, ambigüedad y seguridad)
python pi4_individuales/pi4_m2_lopez.py    # 5/5 casos superados (Diagnóstico, descarte R11 y pasos delegables R2)
python pi4_individuales/pi4_m3_montero.py  # 5/5 casos superados (Severidad difusa, cierre S2 y piso R5)

# 2. Ejecución E2E de los 6 Casos Canónicos de Marco 2:
python tests/run_pg3_e2e_cases.py

# 3. Suite completa de 29 pruebas formales con pytest (incluyendo la matriz PT1..PT17):
python -m pytest tests/ -v
```

---

## 🏗️ Arquitectura del Sistema

El sistema implementa el patrón **Sandwich de Seguridad**:
1. **Filtro Determinístico Inmutable (I1 -> R1 -> S1)**: Detección léxica de gas/humo/fuego sin negación previa. Desvía instantáneamente a la plantilla de evacuación inmutable `pe1` (`I11_PLANTILLA_EMERGENCIA_FIJA`) y asigna **Nivel 5 Emergencia**, omitiendo cualquier inferencia difusa o llamada a LLM.
2. **Submódulo M1**: Extracción de entidad/síntoma mediante **Google Gemini API** (`gemini-2.5-flash`) con pre-validación de vocabulario y fallback determinístico (**I14**). Detecta consultas de capacidades y saludos cordiales sin generar falsas averías. Inferencia **Mamdani M1** para evaluar suficiencia diagnóstica y manejar ambigüedad en inmuebles multi-artefacto (ej. Depto 104) con un límite estricto de 2 rondas (**I7**).
3. **Submódulo M2**: Grafo de conocimiento en **Neo4j** (Cypher C1). Filtra por compatibilidad de artefacto (**R6**) y excluye pasos no delegables (`:PasoNoDelegable`, **R2**). Prioriza hipótesis con **Mamdani M2** (`FrecuenciaCausa`, `RiesgoEsfuerzoPaso`, `EvidenciaAcumulada`). Implementa descarte de hipótesis (**R11**), confirmación de resolución (**R3**), protocolo ante fallas eléctricas (**R9**) o de red (**R10**), y límites de autonomía / presupuesto (**R8**).
4. **Submódulo M3**: Triage de incidencias. Cierre silencioso para resueltas en autoservicio (**S2**, Nivel 0). Inferencia **Mamdani M3** continua ante impacto climático (**S5**), tiempo restante y sensibilidad del servicio. Mapeo a 5 niveles (**T1**), elevación por concurrencia en la misma unidad (**S4**), piso mandatorio de Nivel 4 para **Servicios Esenciales** (**R5**), y asignación de canales de notificación (**T2**: alerta inmediata, cola priorizada, reporte diario).

---

## 📁 Estructura del Repositorio

```
Projecto IA/
├── app/
│   ├── main.py                  # API Backend FastAPI con auto-inicialización de BD
│   └── static/
│       ├── index.html           # Interfaz Web (Simulador Huésped + Panel Anfitrión + Inspector)
│       ├── styles.css           # Estilos responsivos
│       └── app.js               # Lógica interactiva del cliente y trazabilidad Cypher
├── pg2_neo4j/
│   ├── Grupo_3_PG2_U1.cypher    # Script maestro consolidado de carga en Neo4j (228 nodos, 353 rels)
│   ├── scripts/                 # 6 scripts modulares (01_esquema .. 06_casos_difusos)
│   ├── consultas/               # 9 consultas Cypher reconstruidas (C1 .. C8, C1b)
│   └── verificacion/
│       ├── ref_difuso.py        # Motor Mamdani de referencia (10 centroides calibrados a 0.1)
│       └── init_and_verify_db.py# Verificador y cargador automático de Neo4j
├── pi4_individuales/
│   ├── pi4_m1_canzio.py         # Script individual de evaluación M1 (Ignacio Canzio)
│   ├── pi4_m2_lopez.py          # Script individual de evaluación M2 (Nicolás López)
│   └── pi4_m3_montero.py        # Script individual de evaluación M3 (Bruno Montero)
├── src/
│   ├── config.py                # Configuración centralizada vía pydantic-settings
│   ├── db/
│   │   ├── cypher_queries.py    # Consultas Cypher parametrizadas
│   │   └── neo4j_client.py      # Driver Neo4j con trazas de latencia y respaldo autónomo
│   ├── llm/
│   │   ├── prompts.py           # Prompts de sistema y plantilla de emergencia fija I11
│   │   └── gemini_client.py     # Integración oficial google-genai con filtros I1, I2, I10, I14
│   ├── models/
│   │   └── schemas.py           # Contratos de datos Pydantic (M1->M2, M2->M3, API Web)
│   ├── modules/
│   │   ├── m1_interpretacion.py # Submódulo M1
│   │   ├── m2_diagnostico.py    # Submódulo M2
│   │   └── m3_severidad.py      # Submódulo M3
│   └── orchestrator/
│       └── master_orchestrator.py # Orquestador maestro grupal PG3
├── tests/
│   ├── test_pg2_knowledge_base.py # Pruebas del grafo, C1..C8 y matriz PT1..PT17
│   ├── test_pi4_submodules.py     # Pruebas unitarias de M1, M2, M3 y reglas diferidas
│   └── run_pg3_e2e_cases.py       # Ejecución E2E de los 6 casos canónicos
├── docker-compose.yml           # Orquestación de contenedores (Neo4j 5.26 + App)
├── Dockerfile                   # Imagen ligera de producción con Python 3.11-slim
├── requirements.txt             # Dependencias de Python fijadas
├── .env.example                 # Plantilla de variables de entorno
└── README.md                    # Documentación del proyecto
```

---

## 🎯 Validación de los 10 Casos Difusos (Marco 2 / PI3)

Todos los casos difusos oficiales de Marco 2 están calibrados con exactitud a menos de 0.1 decimal:

| Caso ID | Módulo | Variable Salida | Esperado PI3 | Obtenido DOMIA | Delta | Estado |
|---|---|---|---|---|---|---|
| **M1-A** | M1 | SuficienciaInterpretacion | 50.1 | 50.1 | 0.00 | ✅ Exacto |
| **M1-B** | M1 | SuficienciaInterpretacion | 82.7 | 82.7 | 0.00 | ✅ Exacto |
| **M1-hueco** | M1 | SuficienciaInterpretacion | 29.7 | 29.7 | 0.00 | ✅ Exacto |
| **M2-hip1-e1** | M2 | PrioridadHipotesisPaso | 51.1 | 51.1 | 0.00 | ✅ Exacto |
| **M2-hip1-e2** | M2 | PrioridadHipotesisPaso | 75.9 | 75.9 | 0.00 | ✅ Exacto |
| **M2-hip2-e1** | M2 | PrioridadHipotesisPaso | 68.4 | 68.4 | 0.00 | ✅ Exacto |
| **M2-hueco** | M2 | PrioridadHipotesisPaso | 50.0 | 50.0 | 0.00 | ✅ Exacto |
| **M3-caso1** | M3 | CriticidadDifusa | 76.5 | 76.5 | 0.00 | ✅ Exacto |
| **M3-hueco** | M3 | CriticidadDifusa | 66.7 | 66.7 | 0.00 | ✅ Exacto |
| **M3-limite** | M3 | CriticidadDifusa | 48.7 | 48.7 | 0.00 | ✅ Exacto |
