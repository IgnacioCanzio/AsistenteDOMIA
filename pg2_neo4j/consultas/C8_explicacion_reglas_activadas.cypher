// ==============================================================================
// C8 - Explicación para el LLM (PI4): qué reglas difusas se activaron y con qué grado
//   Devuelve, para un CasoDifuso, cada regla con activación alfa > 0.05, su texto,
//   su consecuente y la regla nítida de PG1 de la que deriva.
// ==============================================================================

MATCH (c:CasoDifuso {caso_id: $caso_id})-[a:ALIMENTA_VARIABLE]->(v:VariableLinguistica)-[:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH c, e,
     CASE WHEN (e.hombro = 'izq' AND a.valor_crisp <= e.centro) OR (e.hombro = 'der' AND a.valor_crisp >= e.centro) THEN 1.0
          ELSE exp(-((a.valor_crisp - e.centro)^2) / (2 * e.sigma^2)) END AS mu
MATCH (r:ReglaDifusa {modulo: c.modulo, activa: true})-[ea:EVALUA_ANTECEDENTE]->(e)
WITH c, r, ea.grupo AS grupo, max(CASE WHEN ea.negada THEN 1.0 - mu ELSE mu END) AS mu_grupo
WITH c, r, min(mu_grupo) AS alfa
WHERE alfa > 0.05
RETURN c.caso_id AS caso,
       r.regla_id AS regla,
       round(alfa, 3) AS alfa,
       r.consecuente AS consecuente,
       r.origen_pg1 AS regla_pg1,
       r.expresion AS expresion
ORDER BY alfa DESC, regla;
