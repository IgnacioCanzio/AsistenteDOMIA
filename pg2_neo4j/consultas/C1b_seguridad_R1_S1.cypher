// ==============================================================================
// C1b - Cadena de seguridad nítida I1 -> R1 -> S1
//   No admite gradualidad, no usa lógica difusa.
//   Si hay señal de seguridad, aborta diagnóstico y devuelve plantilla fija.
// ==============================================================================

MATCH (rep:ReporteEstructurado)-[:CONTIENE]->(s:Sintoma)
WHERE rep.senal_seguridad = true OR s.requiere_seguridad = true
MATCH (rep)-[:INICIA]->(ses:SesionDiagnostico)-[:PRODUCE]->(df:DiagnosticoFinal)-[:CLASIFICA]->(inc:Incidencia)
OPTIONAL MATCH (s)-[:DISPARA]->(pe:ProtocoloEmergencia)
RETURN rep.reporte_id AS reporte,
       s.sintoma_id AS sintoma,
       ses.estado AS sesion,
       df.riesgo_seguridad AS riesgo_seguridad,
       inc.incidencia_id AS incidencia,
       5 AS nivel_S1,
       'Emergencia' AS prioridad,
       pe.texto_fijo AS protocolo;
