// ==============================================================================
// C3 - Inferencia difusa completa (Mamdani) sobre los CasoDifuso, en Cypher puro
//   1) Fuzzifica
//   2) Activa reglas: AND = MIN de grupos, OR = MAX dentro del grupo, NOT = 1 - mu
//   3) Recorta consecuentes y agrega por MAX
//   4) Centroide sobre 4001 puntos (paso 0.025)
//   incluir_cobertura = false -> base de PI3 (reglas activa:true); true -> suma RF7/IF7/F7
// ==============================================================================

WITH false AS incluir_cobertura
MATCH (c:CasoDifuso)-[a:ALIMENTA_VARIABLE]->(v:VariableLinguistica)
WITH incluir_cobertura, c.caso_id AS k, c.modulo AS modulo, c.esperado_pi3 AS esperado, v.variable_id AS vid, a.valor_crisp AS x
MATCH (:VariableLinguistica {variable_id: vid})-[:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH incluir_cobertura, k, modulo, esperado, e,
     CASE WHEN (e.hombro = 'izq' AND x <= e.centro) OR (e.hombro = 'der' AND x >= e.centro) THEN 1.0
          ELSE exp(-((x - e.centro)^2) / (2 * e.sigma^2)) END AS mu
MATCH (r:ReglaDifusa {modulo: modulo})-[ea:EVALUA_ANTECEDENTE]->(e)
WHERE r.activa OR incluir_cobertura
WITH k, modulo, esperado, r, ea.grupo AS grupo, max(CASE WHEN ea.negada THEN 1.0 - mu ELSE mu END) AS mu_grupo
WITH k, modulo, esperado, r, min(mu_grupo) AS alfa
MATCH (r)-[:IMPLICA_CONSECUENTE]->(s:EtiquetaDifusa)
WITH k, modulo, esperado, s, max(alfa) AS alfa_s
WITH k, modulo, esperado, collect({c: s.centro, sg: s.sigma, h: s.hombro, a: alfa_s}) AS salida, max(alfa_s) AS alfa_max
UNWIND range(0, 4000) AS i
UNWIND salida AS o
WITH k, modulo, esperado, alfa_max, i / 40.0 AS y, o,
     CASE WHEN (o.h = 'izq' AND i / 40.0 <= o.c) OR (o.h = 'der' AND i / 40.0 >= o.c) THEN 1.0
          ELSE exp(-((i / 40.0 - o.c)^2) / (2 * o.sg^2)) END AS m
WITH k, modulo, esperado, alfa_max, y, max(CASE WHEN m < o.a THEN m ELSE o.a END) AS agg
RETURN k AS caso,
       modulo,
       esperado AS esperado_pi3,
       round(sum(y * agg) / sum(agg), 1) AS centroide,
       round(alfa_max, 3) AS activacion_maxima,
       CASE WHEN alfa_max < 0.2 THEN 'sin_cobertura (usar respaldo nitido)' ELSE 'interpretable' END AS estado
ORDER BY modulo, caso;
