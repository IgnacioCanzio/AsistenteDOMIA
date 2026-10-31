// ==============================================================================
// C1 - Inferencia nítida M2: hipótesis candidatas y próximo paso (R6, R2, R7)
//   R6: solo causas aplicables al tipo de artefacto (labels(a) IN c.aplica_a)
//   R2: nunca pedir al huésped un PasoNoDelegable
//   R7: menor riesgo primero; desempate por mayor frecuencia
//   Cambiar 'tg01' por 'te01', 'cer01' o 'spl01' para ver otros equipos.
// ==============================================================================

MATCH (a:Artefacto {artefacto_id: $artefacto_id})-[:MANIFIESTA]->(s:Sintoma {sintoma_id: $sintoma_id})-[:ASOCIADO_A]->(c:CausaRaiz)
WHERE any(t IN labels(a) WHERE t IN c.aplica_a)
OPTIONAL MATCH (c)-[:SE_COMPRUEBA_CON]->(p:PasoVerificacion)
WHERE NOT p:PasoNoDelegable
RETURN a.artefacto_id AS artefacto,
       c.causa_id AS causa,
       c.frecuencia AS frecuencia,
       p.paso_id AS paso,
       p.instruccion_huesped AS instruccion,
       p.riesgo_usuario AS riesgo
ORDER BY CASE p.riesgo_usuario WHEN 'bajo' THEN 1 WHEN 'medio' THEN 2 ELSE 9 END,
         c.indice_frecuencia DESC;
