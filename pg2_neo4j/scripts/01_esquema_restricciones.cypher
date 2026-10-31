// ==============================================================================
// Script 01: Esquema, Restricciones de Unicidad e Índices
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// Restricciones de Unicidad (26 restricciones según Marco 2 - PG2)
// ------------------------------------------------------------------------------

CREATE CONSTRAINT anfitrion_id IF NOT EXISTS FOR (n:Anfitrion) REQUIRE n.anfitrion_id IS UNIQUE;
CREATE CONSTRAINT huesped_id IF NOT EXISTS FOR (n:Huesped) REQUIRE n.huesped_id IS UNIQUE;
CREATE CONSTRAINT inmueble_id IF NOT EXISTS FOR (n:Inmueble) REQUIRE n.inmueble_id IS UNIQUE;
CREATE CONSTRAINT reserva_id IF NOT EXISTS FOR (n:Reserva) REQUIRE n.reserva_id IS UNIQUE;
CREATE CONSTRAINT artefacto_id IF NOT EXISTS FOR (n:Artefacto) REQUIRE n.artefacto_id IS UNIQUE;
CREATE CONSTRAINT servicio_id IF NOT EXISTS FOR (n:Servicio) REQUIRE n.servicio_id IS UNIQUE;
CREATE CONSTRAINT sintoma_id IF NOT EXISTS FOR (n:Sintoma) REQUIRE n.sintoma_id IS UNIQUE;
CREATE CONSTRAINT causa_id IF NOT EXISTS FOR (n:CausaRaiz) REQUIRE n.causa_id IS UNIQUE;
CREATE CONSTRAINT paso_id IF NOT EXISTS FOR (n:PasoVerificacion) REQUIRE n.paso_id IS UNIQUE;
CREATE CONSTRAINT protocolo_id IF NOT EXISTS FOR (n:ProtocoloEmergencia) REQUIRE n.protocolo_id IS UNIQUE;
CREATE CONSTRAINT vocabulario_id IF NOT EXISTS FOR (n:VocabularioControlado) REQUIRE n.vocabulario_id IS UNIQUE;
CREATE CONSTRAINT expresion_id IF NOT EXISTS FOR (n:ExpresionLexica) REQUIRE n.expresion IS UNIQUE;
CREATE CONSTRAINT lexico_alarma_id IF NOT EXISTS FOR (n:LexicoAlarma) REQUIRE n.termino IS UNIQUE;
CREATE CONSTRAINT nivel_severidad_id IF NOT EXISTS FOR (n:NivelSeveridad) REQUIRE n.nivel IS UNIQUE;
CREATE CONSTRAINT relato_id IF NOT EXISTS FOR (n:Relato) REQUIRE n.relato_id IS UNIQUE;
CREATE CONSTRAINT candidato_id IF NOT EXISTS FOR (n:CandidatoExtraido) REQUIRE n.candidato_id IS UNIQUE;
CREATE CONSTRAINT evaluacion_id IF NOT EXISTS FOR (n:EvaluacionSuficiencia) REQUIRE n.evaluacion_id IS UNIQUE;
CREATE CONSTRAINT pregunta_id IF NOT EXISTS FOR (n:PreguntaAclaratoria) REQUIRE n.pregunta_id IS UNIQUE;
CREATE CONSTRAINT reporte_id IF NOT EXISTS FOR (n:ReporteEstructurado) REQUIRE n.reporte_id IS UNIQUE;
CREATE CONSTRAINT sesion_id IF NOT EXISTS FOR (n:SesionDiagnostico) REQUIRE n.sesion_id IS UNIQUE;
CREATE CONSTRAINT hipotesis_id IF NOT EXISTS FOR (n:Hipotesis) REQUIRE n.hipotesis_id IS UNIQUE;
CREATE CONSTRAINT respuesta_id IF NOT EXISTS FOR (n:RespuestaPaso) REQUIRE n.respuesta_id IS UNIQUE;
CREATE CONSTRAINT diagnostico_id IF NOT EXISTS FOR (n:DiagnosticoFinal) REQUIRE n.diagnostico_id IS UNIQUE;
CREATE CONSTRAINT incidencia_id IF NOT EXISTS FOR (n:Incidencia) REQUIRE n.incidencia_id IS UNIQUE;
CREATE CONSTRAINT contexto_id IF NOT EXISTS FOR (n:ContextoIncidencia) REQUIRE n.contexto_id IS UNIQUE;
CREATE CONSTRAINT variable_id IF NOT EXISTS FOR (n:VariableLinguistica) REQUIRE n.variable_id IS UNIQUE;
CREATE CONSTRAINT etiqueta_id IF NOT EXISTS FOR (n:EtiquetaDifusa) REQUIRE n.etiqueta_id IS UNIQUE;
CREATE CONSTRAINT regla_difusa_id IF NOT EXISTS FOR (n:ReglaDifusa) REQUIRE n.regla_id IS UNIQUE;
CREATE CONSTRAINT regla_crisp_id IF NOT EXISTS FOR (n:ReglaCrisp) REQUIRE n.regla_id IS UNIQUE;
CREATE CONSTRAINT caso_id IF NOT EXISTS FOR (n:CasoDifuso) REQUIRE n.caso_id IS UNIQUE;

// ------------------------------------------------------------------------------
// Índices para optimización de consultas
// ------------------------------------------------------------------------------

CREATE INDEX regla_difusa_modulo IF NOT EXISTS FOR (n:ReglaDifusa) ON (n.modulo);
CREATE INDEX incidencia_estado IF NOT EXISTS FOR (n:Incidencia) ON (n.estado);
