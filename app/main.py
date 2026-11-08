"""
app/main.py - Servidor FastAPI para DOMIA
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.models.schemas import (
    GuestMessageRequest,
    StepResponseRequest,
    ClarificationResponseRequest,
    InteractionResponse,
    FichaIncidencia
)
from src.orchestrator.master_orchestrator import master_orchestrator
from src.db.neo4j_client import db_client
from pg2_neo4j.verificacion.ref_difuso import CASOS_CALIBRACION


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión de ciclo de vida moderno de FastAPI: inicialización y cierre de recursos."""
    if not db_client.is_connected:
        db_client.connect(max_retries=5, retry_delay=2.0)
    yield
    if db_client.is_connected and db_client._driver:
        db_client.close()


app = FastAPI(
    title="DOMIA - Sistema Experto de Conserjería para Alquileres Temporarios",
    description="Backend FastAPI para el ciclo completo M1 -> M2 -> M3 (Grupo 3 - 2026)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Endpoints de Interacción con el Huésped
# ------------------------------------------------------------------------------

@app.post("/api/chat/message", response_model=InteractionResponse)
def post_guest_message(req: GuestMessageRequest):
    """Procesa un mensaje libre del huésped (inicia diagnóstico, aclara o activa emergencia)."""
    try:
        return master_orchestrator.procesar_mensaje_huesped(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/step-response", response_model=InteractionResponse)
def post_step_response(req: StepResponseRequest):
    """Procesa la respuesta a un paso técnico de verificación asistida."""
    try:
        return master_orchestrator.procesar_respuesta_paso(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/clarification", response_model=InteractionResponse)
def post_clarification(req: ClarificationResponseRequest):
    """Procesa la respuesta del huésped a una pregunta aclaratoria de desambiguación."""
    try:
        return master_orchestrator.procesar_respuesta_aclaracion(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------------------
# Endpoints para el Panel del Anfitrión y Triage
# ------------------------------------------------------------------------------

class TriageQueryRequest(BaseModel):
    mensaje: str


@app.post("/api/triage/query")
def post_triage_query(req: TriageQueryRequest):
    """Consulta en lenguaje natural sobre incidencias y triage mediante el sándwich M3."""
    try:
        return master_orchestrator.m3.consultar_triage_lenguaje_natural(req.mensaje)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
def get_alerts():
    """Retorna las alertas de emergencia despachadas en tiempo real para el panel del anfitrión."""
    return master_orchestrator.listar_alertas_emergencia()


@app.get("/api/incidents", response_model=List[Dict[str, Any]])
def get_incidents():
    """Retorna la lista de incidencias registradas y su estado de severidad/canal."""
    return master_orchestrator.listar_incidencias()

@app.get("/api/neo4j/trace/{incidencia_id}")
def get_trace(incidencia_id: str):
    """Retorna la trazabilidad gráfica y relacional de una incidencia."""
    return master_orchestrator.obtener_traza_incidencia(incidencia_id)

@app.get("/api/neo4j/fuzzy-cases")
def get_fuzzy_cases():
    """Retorna los 10 casos difusos calibrados de Marco 2 para validación continua."""
    return CASOS_CALIBRACION

@app.get("/api/inmuebles")
def get_inmuebles():
    """Retorna los inmuebles y artefactos disponibles en el catálogo."""
    return db_client.inmuebles

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "neo4j_connected": db_client.is_connected,
        "database": db_client.database,
        "llm_model": settings.GEMINI_MODEL,
        "llm_provider": settings.LLM_PROVIDER
    }

# ------------------------------------------------------------------------------
# Servir Archivos Estáticos de la Interfaz Web
# ------------------------------------------------------------------------------

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
