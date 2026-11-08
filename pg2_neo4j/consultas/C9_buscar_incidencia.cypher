// ==============================================================================
// Consulta C9: Búsqueda y localización de incidencias por unidad y servicio (M3)
// Propuesta en Actividad PI4 - Submódulo M3 (Bruno Montero) para DOMIA
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

MATCH (inc:Incidencia)-[:AFECTA_A]->(i:Inmueble {inmueble_id: $inmueble_id})
MATCH (inc)-[:AFECTA_A]->(sv:Servicio)
WHERE $servicio_id IS NULL OR sv.servicio_id = $servicio_id
RETURN inc.incidencia_id AS incidencia,
       i.nombre AS inmueble,
       sv.servicio_id AS servicio,
       inc.estado AS estado
ORDER BY incidencia;
