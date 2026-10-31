"""
src/db/cypher_queries.py - Catálogo de Consultas Cypher para DOMIA
Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
Grupo 3 · Comisión 5k9 · UTN FRM · 2026
"""

# C1: Inferencia nítida M2 (causas compatibles y pasos delegables ordenados por riesgo y frecuencia)
C1_PROXIMO_PASO = """
MATCH (a:Artefacto {artefacto_id: $artefacto_id})-[:MANIFIESTA]->(s:Sintoma {sintoma_id: $sintoma_id})-[:ASOCIADO_A]->(c:CausaRaiz)
WHERE any(t IN labels(a) WHERE t IN c.aplica_a)
OPTIONAL MATCH (c)-[:SE_COMPRUEBA_CON]->(p:PasoVerificacion)
WHERE NOT p:PasoNoDelegable
RETURN a.artefacto_id AS artefacto,
       c.causa_id AS causa,
       c.frecuencia AS frecuencia,
       c.indice_frecuencia AS indice_frecuencia,
       c.resoluble_por_huesped AS resoluble,
       p.paso_id AS paso,
       p.instruccion_huesped AS instruccion,
       p.riesgo_usuario AS riesgo,
       p.riesgo_esfuerzo AS riesgo_esfuerzo,
       p.advertencias AS advertencias
ORDER BY CASE p.riesgo_usuario WHEN 'bajo' THEN 1 WHEN 'medio' THEN 2 ELSE 9 END,
         c.indice_frecuencia DESC;
"""

# C1b: Cadena de seguridad determinística (I1 -> R1 -> S1)
C1B_CHEQUEO_SEGURIDAD = """
MATCH (rep:ReporteEstructurado {reporte_id: $reporte_id})-[:CONTIENE]->(s:Sintoma)
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
"""

# C2: Fuzzificación genérica
C2_FUZZIFICACION = """
UNWIND $inputs AS inp
MATCH (:VariableLinguistica {variable_id: inp.v})-[t:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH inp, e, t,
     CASE WHEN (e.hombro = 'izq' AND inp.x <= e.centro) OR (e.hombro = 'der' AND inp.x >= e.centro) THEN 1.0
          ELSE exp(-((inp.x - e.centro)^2) / (2 * e.sigma^2)) END AS mu
RETURN inp.v AS variable, inp.x AS valor, e.nombre AS etiqueta, round(mu, 3) AS pertenencia
ORDER BY variable, t.orden;
"""

# C3: Inferencia Mamdani sobre :CasoDifuso
C3_MAMDANI_CASOS = """
WITH $incluir_cobertura AS incluir_cobertura
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
"""

# C4: Evaluación de severidad integrada (M2 -> M3)
C4_EVALUACION_SEVERIDAD = """
MATCH (inc:Incidencia {incidencia_id: $incidencia_id})-[:AFECTA_A]->(sv:Servicio)
WHERE inc.estado = 'resuelta_por_huesped'
RETURN inc.incidencia_id AS incidencia, sv.servicio_id AS servicio, 'S2_cierre' AS via,
       null AS puntaje, null AS nivel_calculado, null AS piso_r5, null AS nivel_final,
       'sin_aviso' AS prioridad, 'sin_aviso' AS canal, null AS activacion_maxima

UNION ALL

MATCH (df:DiagnosticoFinal {riesgo_seguridad:true})-[:CLASIFICA]->(inc:Incidencia {incidencia_id: $incidencia_id})-[:AFECTA_A]->(sv:Servicio)
MATCH (n:NivelSeveridad {nivel:5})
RETURN inc.incidencia_id AS incidencia, sv.servicio_id AS servicio, 'S1_emergencia' AS via,
       null AS puntaje, null AS nivel_calculado, null AS piso_r5, 5 AS nivel_final,
       n.prioridad AS prioridad, n.canal AS canal, null AS activacion_maxima

UNION ALL

MATCH (df:DiagnosticoFinal {riesgo_seguridad:false})-[:CLASIFICA]->(inc:Incidencia {incidencia_id: $incidencia_id, estado:'escalada'})-[:AFECTA_A]->(sv:Servicio),
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
"""

# C5: Traza completa de una incidencia
C5_TRAZA_INCIDENCIA = """
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
"""

# C6: Carga útil para el LLM
C6_PAYLOAD_LLM = """
MATCH (inc:Incidencia {incidencia_id: $incidencia_id})-[:AFECTA_A]->(i:Inmueble)
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
} AS payload;
"""

# C8: Explicación de reglas difusas activadas para un caso difuso
C8_EXPLICACION_REGLAS = """
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
"""
