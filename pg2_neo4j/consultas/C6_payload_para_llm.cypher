// ==============================================================================
// C6 - Carga útil (payload) para el LLM de PI4: una fila por incidencia escalada
//   El LLM NO decide: solo redacta lo que el grafo ya calculó.
// ==============================================================================

MATCH (inc:Incidencia {estado:'escalada'})-[:AFECTA_A]->(i:Inmueble)
MATCH (inc)-[:AFECTA_A]->(sv:Servicio)
MATCH (df:DiagnosticoFinal)-[:CLASIFICA]->(inc)
OPTIONAL MATCH (inc)-[:VINCULA]->(a:Artefacto)
OPTIONAL MATCH (inc)-[:TIENE_CONTEXTO]->(ctx:ContextoIncidencia)
OPTIONAL MATCH (df)-[:DIAGNOSTICA]->(cr:CausaRaiz)
RETURN {
  incidencia: inc.incidencia_id,
  inmueble: i.nombre,
  artefacto: a.artefacto_id,
  servicio: sv.servicio_id,
  servicio_esencial: sv.esencial,
  causa: df.causa_diagnosticada,
  resoluble_por_huesped: df.resoluble_por_huesped,
  riesgo_seguridad: df.riesgo_seguridad,
  temperatura: ctx.temperatura_actual,
  horas_restantes: ctx.horas_restantes,
  dato_estimado: ctx.dato_estimado
} AS payload
ORDER BY inc.incidencia_id;
