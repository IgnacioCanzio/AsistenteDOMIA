// ==============================================================================
// C4 - Inferencia entre módulos M2 -> M3: severidad de cada incidencia
//   S2: resuelta por el huésped -> se cierra, no se evalúa
//   S1: riesgo de seguridad -> nivel 5 Emergencia, se OMITE la inferencia difusa
//   resto: S5 (sensibilidad contextual) -> fuzzifica -> reglas F1-F6 -> centroide -> T1 -> piso R5 -> T2
//   Si alfa_max < 0.2 el centroide no es interpretable: se usa nivel 3 conservador y piso R5.
// ==============================================================================

MATCH (inc:Incidencia {estado:'resuelta_por_huesped'})-[:AFECTA_A]->(sv:Servicio)
RETURN inc.incidencia_id AS incidencia, sv.servicio_id AS servicio, 'S2_cierre' AS via,
       null AS puntaje, null AS nivel_calculado, null AS piso_r5, null AS nivel_final,
       'sin_aviso' AS prioridad, 'sin_aviso' AS canal, null AS activacion_maxima

UNION ALL

MATCH (df:DiagnosticoFinal {riesgo_seguridad:true})-[:CLASIFICA]->(inc:Incidencia)-[:AFECTA_A]->(sv:Servicio)
MATCH (n:NivelSeveridad {nivel:5})
RETURN inc.incidencia_id AS incidencia, sv.servicio_id AS servicio, 'S1_emergencia' AS via,
       null AS puntaje, null AS nivel_calculado, null AS piso_r5, 5 AS nivel_final,
       n.prioridad AS prioridad, n.canal AS canal, null AS activacion_maxima

UNION ALL

MATCH (df:DiagnosticoFinal {riesgo_seguridad:false})-[:CLASIFICA]->(inc:Incidencia {estado:'escalada'})-[:AFECTA_A]->(sv:Servicio),
      (inc)-[:TIENE_CONTEXTO]->(ctx:ContextoIncidencia)
MATCH (ea:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Alto'}), (ee:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Extremo'})
WITH inc, sv, ctx,
     exp(-((ctx.temperatura_actual - ea.centro)^2) / (2 * ea.sigma^2)) AS mu_alto,
     CASE WHEN ctx.temperatura_actual >= ee.centro THEN 1.0
          ELSE exp(-((ctx.temperatura_actual - ee.centro)^2) / (2 * ee.sigma^2)) END AS mu_extremo
WITH inc, sv, ctx,
     CASE WHEN sv.tipo = 'climatizacion'
          THEN sv.sensibilidad_base + 4.5 * (CASE WHEN mu_alto > mu_extremo THEN mu_alto ELSE mu_extremo END)
          ELSE sv.sensibilidad_base END AS s_clim
UNWIND [{v:'ImpactoClimatico', x: ctx.temperatura_actual}, {v:'TiempoRestante', x: ctx.horas_restantes}, {v:'SensibilidadServicio', x: s_clim}] AS ent
MATCH (:VariableLinguistica {variable_id: ent.v})-[:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH inc, sv, e,
     CASE WHEN (e.hombro = 'izq' AND ent.x <= e.centro) OR (e.hombro = 'der' AND ent.x >= e.centro) THEN 1.0
          ELSE exp(-((ent.x - e.centro)^2) / (2 * e.sigma^2)) END AS mu
MATCH (r:ReglaDifusa {modulo:'M3', activa:true})-[ea:EVALUA_ANTECEDENTE]->(e)
WITH inc, sv, r, ea.grupo AS grupo, max(CASE WHEN ea.negada THEN 1.0 - mu ELSE mu END) AS mu_grupo
WITH inc, sv, r, min(mu_grupo) AS alfa
MATCH (r)-[:IMPLICA_CONSECUENTE]->(s:EtiquetaDifusa)
WITH inc, sv, s, max(alfa) AS alfa_s
WITH inc, sv, collect({c: s.centro, sg: s.sigma, h: s.hombro, a: alfa_s}) AS salida, max(alfa_s) AS alfa_max
UNWIND range(0, 4000) AS i
UNWIND salida AS o
WITH inc, sv, alfa_max, i / 40.0 AS y, o,
     CASE WHEN (o.h = 'izq' AND i / 40.0 <= o.c) OR (o.h = 'der' AND i / 40.0 >= o.c) THEN 1.0
          ELSE exp(-((i / 40.0 - o.c)^2) / (2 * o.sg^2)) END AS m
WITH inc, sv, alfa_max, y, max(CASE WHEN m < o.a THEN m ELSE o.a END) AS agg
WITH inc, sv, alfa_max, sum(y * agg) / sum(agg) AS puntaje
WITH inc, sv, alfa_max, puntaje,
     CASE WHEN alfa_max < 0.2 THEN 3
          WHEN puntaje >= 80 THEN 5 WHEN puntaje >= 60 THEN 4 WHEN puntaje >= 40 THEN 3
          WHEN puntaje >= 20 THEN 2 ELSE 1 END AS nivel_calc,
     CASE WHEN sv.esencial THEN 4 ELSE 1 END AS piso
WITH inc, sv, alfa_max, puntaje, nivel_calc, piso,
     CASE WHEN nivel_calc > piso THEN nivel_calc ELSE piso END AS nivel_final
MATCH (n:NivelSeveridad {nivel: nivel_final})
RETURN inc.incidencia_id AS incidencia,
       sv.servicio_id AS servicio,
       'difusa' AS via,
       round(puntaje, 1) AS puntaje,
       nivel_calc AS nivel_calculado,
       piso AS piso_r5,
       nivel_final,
       n.prioridad AS prioridad,
       n.canal AS canal,
       round(alfa_max, 3) AS activacion_maxima;
