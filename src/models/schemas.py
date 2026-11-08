"""
src/models/schemas.py - Modelos y Contratos de Datos Pydantic
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# ------------------------------------------------------------------------------
# Modelos de Extracción Semántica y Sándwich (M1, M2, M3)
# ------------------------------------------------------------------------------

class ExtraccionM1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artefacto_mencionado: Optional[Literal["tg01", "cer01", "spl01", "te01", "tg02", "tg03"]] = None
    sintoma_identificado: Optional[Literal["sin_agua_caliente", "teclado_sin_respuesta", "no_enfria", "olor_a_gas"]] = None
    confianza_extraccion: float = Field(ge=0.0, le=1.0)
    polaridad: Literal['afirmativa', 'negativa'] = 'afirmativa'
    es_alarma: bool = False
    termino_alarma: Optional[str] = None
    fuera_de_dominio: bool = False
    es_consulta_capacidades: bool = False
    mencion_artefacto_texto: Optional[str] = None

class ExtraccionM2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artefacto_id: Optional[Literal["tg01", "cer01", "spl01", "te01", "tg02", "tg03"]] = None
    sintoma_id: Optional[Literal["sin_agua_caliente", "teclado_sin_respuesta", "no_enfria", "olor_a_gas"]] = None
    causas_descartadas: List[Literal["llave_gas_cerrada", "piloto_apagado", "termica_bajada", "pilas_agotadas", "filtro_sucio"]] = Field(default_factory=list)
    causa_resuelta: Optional[Literal["llave_gas_cerrada", "piloto_apagado", "termica_bajada", "pilas_agotadas", "filtro_sucio"]] = None
    paso_no_puedo: bool = False
    senal_seguridad: bool = False
    fuera_de_dominio: bool = False
    confianza_extraccion: float = Field(ge=0.0, le=1.0)

class ExtraccionM3(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inmueble_id: Optional[str] = Field(default=None, pattern=r"^inm\d{3}$")
    servicio_id: Optional[Literal["agua_caliente", "acceso_principal", "climatizacion", "electricidad", "agua_potable"]] = None
    pide_justificacion: bool = False
    fuera_de_dominio: bool = False
    confianza_extraccion: float = Field(ge=0.0, le=1.0)

from datetime import datetime

class AlertaEmergencia(BaseModel):
    alerta_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    inmueble_id: str
    inmueble_nombre: str = "Departamento"
    tipo_emergencia: str = "gas_o_seguridad_critica"
    huesped_id: Optional[str] = None
    sintoma_id: str = "olor_a_gas"
    termino_alarma: Optional[str] = "gas"
    protocolo_id: str = "pe1"
    destinatarios: List[str] = Field(default_factory=lambda: [
        "Anfitrión (Roberto Gómez)",
        "Servicio de Emergencias 911 / Guardia de Gas Matriculada"
    ])
    estado_despacho: Literal['despachada', 'confirmada'] = 'despachada'

class CandidatoExtraido(BaseModel):
    candidato_id: str
    artefacto_mencionado: Optional[str] = None
    sintoma_mencionado: Optional[str] = None
    confianza: float = Field(ge=0.0, le=1.0)
    polaridad: Literal['afirmativa', 'negativa'] = 'afirmativa'
    es_alarma: bool = False
    termino_alarma: Optional[str] = None

class EvaluacionM1(BaseModel):
    evaluacion_id: str
    confianza_extraccion: float = Field(ge=0.0, le=1.0)
    coincidencia_lexica: float = Field(ge=0.0, le=1.0)
    distancia_candidatos: float = Field(ge=0.0, le=1.0)
    suficiencia_centroide: float = Field(ge=0.0, le=100.0)
    alfa_max: float
    estado_cobertura: str
    decision: Literal['suficiente', 'insuficiente_con_rondas', 'insuficiente_escalar', 'emergencia']
    pregunta_aclaratoria: Optional[str] = None
    ronda_actual: int = 1
    max_rondas: int = 2

# ------------------------------------------------------------------------------
# Contrato M1 -> M2: Reporte Estructurado
# ------------------------------------------------------------------------------

class ReporteEstructurado(BaseModel):
    reporte_id: str
    inmueble_id: str
    huesped_id: Optional[str] = None
    reserva_id: Optional[str] = None
    artefacto_id: str
    sintoma_id: str
    senal_seguridad: bool = False
    termino_alarma: Optional[str] = None
    suficiencia_puntaje: float = 0.0
    estado: Literal['emitido', 'emitido_alerta', 'bloqueado'] = 'emitido'

# ------------------------------------------------------------------------------
# Contrato M2 -> M1: Instrucción Estructurada (Próximo Paso / Protocolo)
# ------------------------------------------------------------------------------

class InstruccionEstructurada(BaseModel):
    sesion_id: str
    tipo: Literal['paso', 'emergencia', 'cierre', 'escalada']
    paso_id: Optional[str] = None
    instruccion_huesped: Optional[str] = None
    riesgo_usuario: Optional[Literal['bajo', 'medio', 'alto']] = None
    advertencias: List[str] = []
    justificacion: Optional[str] = None
    prioridad_difusa: Optional[float] = None
    pasos_intentados: int = 0
    max_pasos: int = 4
    texto_verbalizado_llm: Optional[str] = None

# ------------------------------------------------------------------------------
# Contrato M2 -> M3: Diagnóstico Final
# ------------------------------------------------------------------------------

class DiagnosticoFinal(BaseModel):
    diagnostico_id: str
    sesion_id: str
    inmueble_id: str
    artefacto_id: str
    servicio_id: str
    causa_diagnosticada: str
    resoluble_por_huesped: bool
    riesgo_seguridad: bool
    pasos_realizados: List[str] = []
    estado_cierre: Literal['resuelta_por_huesped', 'escalada', 'abortada_seguridad']

# ------------------------------------------------------------------------------
# Contrato M3 -> Anfitrión / Triage: Ficha de Incidencia
# ------------------------------------------------------------------------------

class ReglaActivadaInfo(BaseModel):
    regla: str
    alfa: float
    consecuente: str
    regla_pg1: Optional[str] = None
    expresion: Optional[str] = None

class ContextoIncidenciaInput(BaseModel):
    temperatura_actual: float = 24.0
    horas_restantes: float = 24.0
    dato_estimado: bool = False

class FichaIncidencia(BaseModel):
    incidencia_id: str
    inmueble_id: str
    inmueble_nombre: str
    artefacto_id: str
    servicio_id: str
    servicio_esencial: bool
    causa_diagnosticada: str
    resoluble_por_huesped: bool
    riesgo_seguridad: bool
    temperatura: Optional[float] = None
    horas_restantes: Optional[float] = None
    dato_estimado: bool = False
    via_evaluacion: Literal['S1_emergencia', 'S2_cierre', 'difusa']
    puntaje_difuso: Optional[float] = None
    nivel_calculado: Optional[int] = None
    piso_r5: Optional[int] = None
    nivel_final: int
    prioridad: Literal['Baja', 'Media', 'Alta', 'Emergencia', 'sin_aviso']
    canal: Literal['reporte_diario', 'cola_priorizada', 'alerta_inmediata', 'sin_aviso']
    activacion_maxima: Optional[float] = None
    estado_cobertura: Optional[str] = None
    reglas_activadas: List[ReglaActivadaInfo] = []
    estado: Literal['en_curso', 'resuelta_por_huesped', 'escalada']
    notificacion_redactada: Optional[str] = None

# ------------------------------------------------------------------------------
# Modelos para la API Web FastAPI
# ------------------------------------------------------------------------------

class GuestMessageRequest(BaseModel):
    inmueble_id: str = "inm101"
    huesped_id: str = "h1"
    mensaje: str
    temperatura_actual: Optional[float] = None
    horas_restantes: Optional[float] = None

class StepResponseRequest(BaseModel):
    sesion_id: str
    paso_id: str
    resultado: Literal['si', 'no', 'no_puedo', 'no_se']
    detalle: Optional[str] = None

class ClarificationResponseRequest(BaseModel):
    inmueble_id: str
    huesped_id: str
    respuesta: str
    ronda: int = 1

class InteractionResponse(BaseModel):
    tipo_evento: Literal[
        'pregunta_aclaratoria',
        'instruccion_paso',
        'emergencia',
        'cierre_exitoso',
        'escalada_anfitrion',
        'fuera_de_dominio',
        'artefacto_inexistente',
        'reserva_inactiva',
        'consulta_capacidades',
        'ficha_incidencia',
        'sin_incidencia',
        'datos_insuficientes'
    ]
    mensaje_para_huesped: str
    advertencias: List[str] = []
    sesion_id: Optional[str] = None
    paso_id: Optional[str] = None
    reporte_id: Optional[str] = None
    incidencia_id: Optional[str] = None
    ficha_incidencia: Optional[FichaIncidencia] = None
    alerta_emergencia: Optional[AlertaEmergencia] = None
    trazabilidad_diagnostica: Dict[str, Any] = {}
    sandwich_trace: Optional[Dict[str, Any]] = None
    cypher_traces: List[Dict[str, Any]] = []
