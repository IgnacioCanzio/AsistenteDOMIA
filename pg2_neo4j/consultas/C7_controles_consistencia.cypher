// ==============================================================================
// C7 - Controles de consistencia de la base: 0 violaciones esperadas
//   Los cortes 0.24 / 0.69 (frecuencia) y 2.65 / 7.35 (riesgo) son de PI3 (López).
// ==============================================================================

MATCH (c:CausaRaiz)
WITH c, CASE WHEN c.indice_frecuencia < 0.24 THEN 'rara'
             WHEN c.indice_frecuencia < 0.69 THEN 'poco_frecuente'
             ELSE 'frecuente' END AS esperado
WHERE esperado <> c.frecuencia
WITH count(*) AS n RETURN 'frecuencia categorica incoherente con indice_frecuencia' AS control, n AS violaciones

UNION ALL

MATCH (p:PasoVerificacion)
WITH p, CASE WHEN p.riesgo_esfuerzo < 2.65 THEN 'bajo'
             WHEN p.riesgo_esfuerzo < 7.35 THEN 'medio'
             ELSE 'alto' END AS esperado
WHERE esperado <> p.riesgo_usuario
WITH count(*) AS n RETURN 'riesgo categorico incoherente con riesgo_esfuerzo' AS control, n AS violaciones

UNION ALL

MATCH (p:PasoVerificacion)
WHERE (p.requiere_herramientas = true OR p.manipula_cableado = true) AND NOT p:PasoNoDelegable
WITH count(*) AS n RETURN 'paso con herramientas/cableado que no es PasoNoDelegable (R2)' AS control, n AS violaciones

UNION ALL

MATCH (c:CausaRaiz) WHERE NOT (c)-[:SE_COMPRUEBA_CON]->(:PasoVerificacion)
WITH count(*) AS n RETURN 'causa raiz sin paso de verificacion' AS control, n AS violaciones

UNION ALL

MATCH (r:ReglaDifusa) WHERE NOT (r)-[:IMPLICA_CONSECUENTE]->(:EtiquetaDifusa) OR NOT (r)-[:EVALUA_ANTECEDENTE]->(:EtiquetaDifusa)
WITH count(*) AS n RETURN 'regla difusa sin antecedente o sin consecuente' AS control, n AS violaciones

UNION ALL

MATCH (e:EtiquetaDifusa) WHERE NOT (:VariableLinguistica)-[:TIENE_ETIQUETA]->(e)
WITH count(*) AS n RETURN 'etiqueta difusa sin variable' AS control, n AS violaciones

UNION ALL

MATCH (i:Incidencia) WHERE NOT (:DiagnosticoFinal)-[:CLASIFICA]->(i)
WITH count(*) AS n RETURN 'incidencia sin DiagnosticoFinal' AS control, n AS violaciones

UNION ALL

MATCH (i:Incidencia {estado:'escalada'}) WHERE NOT (i)-[:AFECTA_A]->(:Servicio)
WITH count(*) AS n RETURN 'incidencia escalada sin servicio afectado' AS control, n AS violaciones

UNION ALL

MATCH (s:Sintoma:SenalSeguridad) WHERE NOT (s)-[:DISPARA]->(:ProtocoloEmergencia)
WITH count(*) AS n RETURN 'senal de seguridad sin protocolo de emergencia' AS control, n AS violaciones;
