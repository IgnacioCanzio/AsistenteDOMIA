// ==============================================================================
// C2 - Fuzzificación con exp(): grado de pertenencia de cada valor a cada etiqueta
//   mu(x) = exp(-(x-c)^2 / (2*sigma^2)); hombro 'izq': 1 si x<=c; hombro 'der': 1 si x>=c
// ==============================================================================

UNWIND $inputs AS inp
MATCH (:VariableLinguistica {variable_id: inp.v})-[t:TIENE_ETIQUETA]->(e:EtiquetaDifusa)
WITH inp, e, t,
     CASE WHEN (e.hombro = 'izq' AND inp.x <= e.centro) OR (e.hombro = 'der' AND inp.x >= e.centro) THEN 1.0
          ELSE exp(-((inp.x - e.centro)^2) / (2 * e.sigma^2)) END AS mu
RETURN inp.v AS variable, inp.x AS valor, e.nombre AS etiqueta, round(mu, 3) AS pertenencia
ORDER BY variable, t.orden;
