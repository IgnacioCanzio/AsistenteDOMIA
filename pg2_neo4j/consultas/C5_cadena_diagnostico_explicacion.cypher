// ==============================================================================
// C5 - Inferencia entre módulos M1 -> M2 -> M3: traza de una incidencia
//   Une relato, reporte, sesión, hipótesis (con su prioridad difusa), diagnóstico e incidencia.
// ==============================================================================

WITH false AS incluir_cobertura
MATCH (c:CasoDifuso)-[a:ALIMENTA_VARIABLE]->(v:VariableLinguistica)
WITH incluir_cobertura, c.caso_id AS k, c.modulo AS modulo, v.variable_id AS vid, a.valor_crisp AS x
MATCH (:VariableLinguistica {variable_id: vid})-[:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH incluir_cobertura, k, modulo, e,
     CASE WHEN (e.hombro = 'izq' AND x <= e.centro) OR (e.hombro = 'der' AND x >= e.centro) THEN 1.0
          ELSE exp(-((x - e.centro)^2) / (2 * e.sigma^2)) END AS mu
MATCH (r:ReglaDifusa {modulo: modulo})-[ea:EVALUA_ANTECEDENTE]->(e)
WHERE r.activa OR incluir_cobertura
WITH k, modulo, r, ea.grupo AS grupo, max(CASE WHEN ea.negada THEN 1.0 - mu ELSE mu END) AS mu_grupo
WITH k, modulo, r, min(mu_grupo) AS alfa
MATCH (r)-[:IMPLICA_CONSECUENTE]->(s:EtiquetaDifusa)
WITH k, modulo, s, max(alfa) AS alfa_s
WITH k, collect({c: s.centro, sg: s.sigma, h: s.hombro, a: alfa_s}) AS salida
UNWIND range(0, 4000) AS i
UNWIND salida AS o
WITH k, i / 40.0 AS y, o,
     CASE WHEN (o.h = 'izq' AND i / 40.0 <= o.c) OR (o.h = 'der' AND i / 40.0 >= o.c) THEN 1.0
          ELSE exp(-((i / 40.0 - o.c)^2) / (2 * o.sg^2)) END AS m
WITH k, y, max(CASE WHEN m < o.a THEN m ELSE o.a END) AS agg
WITH k, round(sum(y * agg) / sum(agg), 1) AS puntaje
WITH collect({k: k, p: puntaje}) AS res
MATCH (inc:Incidencia {incidencia_id: $incidencia_id})<-[:GESTIONA]-(ses:SesionDiagnostico)<-[:INICIA]-(rep:ReporteEstructurado),
      (rel:Relato)<-[:ANALIZA]-(ev:EvaluacionSuficiencia)-[:PRODUCE]->(rep),
      (ses)-[:MANTIENE]->(h:Hipotesis)-[:SE_REFIERE_A]->(cr:CausaRaiz),
      (ses)-[:PRODUCE]->(df:DiagnosticoFinal)
OPTIONAL MATCH (cm1:CasoDifuso)-[:EVALUA_A]->(ev)
OPTIONAL MATCH (cm2:CasoDifuso)-[:EVALUA_A]->(h)
WITH res, rel, ev, cm1, rep, ses, df, inc, h, cr, collect(cm2.caso_id) AS casos_hip
WITH rel, ev, cm1, rep, ses, df, inc, h, cr,
     [x IN res WHERE x.k IN casos_hip | x.k + '=' + toString(x.p)] AS puntajes_hipotesis,
     [x IN res WHERE x.k = cm1.caso_id | x.p][0] AS puntaje_m1
RETURN rel.texto AS relato,
       puntaje_m1 AS m1_suficiencia,
       ev.resultado AS m1_decision,
       rep.reporte_id AS reporte,
       ses.sesion_id AS sesion,
       h.hipotesis_id AS hipotesis,
       cr.causa_id AS causa,
       h.estado AS estado_hipotesis,
       puntajes_hipotesis AS m2_prioridad_difusa,
       df.causa_diagnosticada AS diagnostico,
       inc.incidencia_id AS incidencia,
       inc.estado AS estado_incidencia
ORDER BY h.hipotesis_id;
