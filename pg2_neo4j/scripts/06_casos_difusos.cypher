// ==============================================================================
// Script 06: Casos Difusos de Calibración y Vínculos de Validación
// 10 nodos :CasoDifuso, 30 relaciones ALIMENTA_VARIABLE y 6 vínculos EVALUA_A
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Casos Difusos de M1 (3 casos)
// ------------------------------------------------------------------------------

CREATE (:CasoDifuso {caso_id:'M1-A', modulo:'M1', descripcion:'Ambigüedad parcial con distancia media', esperado_pi3:50.1});
CREATE (:CasoDifuso {caso_id:'M1-B', modulo:'M1', descripcion:'Extracción clara y unívoca', esperado_pi3:82.7});
CREATE (:CasoDifuso {caso_id:'M1-hueco', modulo:'M1', descripcion:'Combinación no cubierta (sin cobertura)', esperado_pi3:29.7});

MATCH (c:CasoDifuso {caso_id:'M1-A'}),
      (v_conf:VariableLinguistica {variable_id:'ConfianzaExtraccion'}),
      (v_coin:VariableLinguistica {variable_id:'CoincidenciaLexica'}),
      (v_dist:VariableLinguistica {variable_id:'DistanciaCandidatos'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.72}]->(v_conf),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.68}]->(v_coin),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.35}]->(v_dist);

MATCH (c:CasoDifuso {caso_id:'M1-B'}),
      (v_conf:VariableLinguistica {variable_id:'ConfianzaExtraccion'}),
      (v_coin:VariableLinguistica {variable_id:'CoincidenciaLexica'}),
      (v_dist:VariableLinguistica {variable_id:'DistanciaCandidatos'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.90}]->(v_conf),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.92}]->(v_coin),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.85}]->(v_dist);

MATCH (c:CasoDifuso {caso_id:'M1-hueco'}),
      (v_conf:VariableLinguistica {variable_id:'ConfianzaExtraccion'}),
      (v_coin:VariableLinguistica {variable_id:'CoincidenciaLexica'}),
      (v_dist:VariableLinguistica {variable_id:'DistanciaCandidatos'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.50}]->(v_conf),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.50}]->(v_coin),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.90}]->(v_dist);

// ------------------------------------------------------------------------------
// 2. Casos Difusos de M2 (4 casos)
// ------------------------------------------------------------------------------

CREATE (:CasoDifuso {caso_id:'M2-hip1-e1', modulo:'M2', descripcion:'Hipótesis 1 (piloto) estado inicial turno 1', esperado_pi3:51.1});
CREATE (:CasoDifuso {caso_id:'M2-hip1-e2', modulo:'M2', descripcion:'Hipótesis 1 (piloto) tras descarte de hip2 turno 2', esperado_pi3:75.9});
CREATE (:CasoDifuso {caso_id:'M2-hip2-e1', modulo:'M2', descripcion:'Hipótesis 2 (llave gas) estado inicial turno 1', esperado_pi3:68.4});
CREATE (:CasoDifuso {caso_id:'M2-hueco', modulo:'M2', descripcion:'Causa rara con riesgo medio (sin cobertura)', esperado_pi3:50.0});

MATCH (c:CasoDifuso {caso_id:'M2-hip1-e1'}),
      (v_frec:VariableLinguistica {variable_id:'FrecuenciaCausa'}),
      (v_ries:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso'}),
      (v_evid:VariableLinguistica {variable_id:'EvidenciaAcumulada'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.82}]->(v_frec),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:4.2}]->(v_ries),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.55}]->(v_evid);

MATCH (c:CasoDifuso {caso_id:'M2-hip1-e2'}),
      (v_frec:VariableLinguistica {variable_id:'FrecuenciaCausa'}),
      (v_ries:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso'}),
      (v_evid:VariableLinguistica {variable_id:'EvidenciaAcumulada'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.82}]->(v_frec),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:4.2}]->(v_ries),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.85}]->(v_evid);

MATCH (c:CasoDifuso {caso_id:'M2-hip2-e1'}),
      (v_frec:VariableLinguistica {variable_id:'FrecuenciaCausa'}),
      (v_ries:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso'}),
      (v_evid:VariableLinguistica {variable_id:'EvidenciaAcumulada'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.75}]->(v_frec),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:1.2}]->(v_ries),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.55}]->(v_evid);

MATCH (c:CasoDifuso {caso_id:'M2-hueco'}),
      (v_frec:VariableLinguistica {variable_id:'FrecuenciaCausa'}),
      (v_ries:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso'}),
      (v_evid:VariableLinguistica {variable_id:'EvidenciaAcumulada'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:0.10}]->(v_frec),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:5.0}]->(v_ries),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:1.00}]->(v_evid);

// ------------------------------------------------------------------------------
// 3. Casos Difusos de M3 (3 casos)
// ------------------------------------------------------------------------------

CREATE (:CasoDifuso {caso_id:'M3-caso1', modulo:'M3', descripcion:'Ola de calor con split inoperativo (Caso 4)', esperado_pi3:76.5});
CREATE (:CasoDifuso {caso_id:'M3-hueco', modulo:'M3', descripcion:'Temperatura templada y tiempo corto (sin cobertura)', esperado_pi3:66.7});
CREATE (:CasoDifuso {caso_id:'M3-limite', modulo:'M3', descripcion:'Check-out inminente a 31°C (Caso 5 / PT7)', esperado_pi3:48.7});

MATCH (c:CasoDifuso {caso_id:'M3-caso1'}),
      (v_clima:VariableLinguistica {variable_id:'ImpactoClimatico'}),
      (v_tiempo:VariableLinguistica {variable_id:'TiempoRestante'}),
      (v_sens:VariableLinguistica {variable_id:'SensibilidadServicio'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:38.0}]->(v_clima),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:48.0}]->(v_tiempo),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:8.3}]->(v_sens);

MATCH (c:CasoDifuso {caso_id:'M3-hueco'}),
      (v_clima:VariableLinguistica {variable_id:'ImpactoClimatico'}),
      (v_tiempo:VariableLinguistica {variable_id:'TiempoRestante'}),
      (v_sens:VariableLinguistica {variable_id:'SensibilidadServicio'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:12.0}]->(v_clima),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:12.0}]->(v_tiempo),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:10.0}]->(v_sens);

MATCH (c:CasoDifuso {caso_id:'M3-limite'}),
      (v_clima:VariableLinguistica {variable_id:'ImpactoClimatico'}),
      (v_tiempo:VariableLinguistica {variable_id:'TiempoRestante'}),
      (v_sens:VariableLinguistica {variable_id:'SensibilidadServicio'})
CREATE (c)-[:ALIMENTA_VARIABLE {valor_crisp:31.0}]->(v_clima),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:3.5}]->(v_tiempo),
       (c)-[:ALIMENTA_VARIABLE {valor_crisp:5.5}]->(v_sens);

// ------------------------------------------------------------------------------
// 4. Vínculos EVALUA_A (6 relaciones para trazabilidad y consultas C5)
// ------------------------------------------------------------------------------

MATCH (cm1a:CasoDifuso {caso_id:'M1-A'}), (ev3:EvaluacionSuficiencia {evaluacion_id:'ev3'})
CREATE (cm1a)-[:EVALUA_A]->(ev3);

MATCH (cm1b:CasoDifuso {caso_id:'M1-B'}), (ev1:EvaluacionSuficiencia {evaluacion_id:'ev1'})
CREATE (cm1b)-[:EVALUA_A]->(ev1);

MATCH (cm2a:CasoDifuso {caso_id:'M2-hip1-e1'}), (hip1:Hipotesis {hipotesis_id:'hip1'})
CREATE (cm2a)-[:EVALUA_A]->(hip1);

MATCH (cm2b:CasoDifuso {caso_id:'M2-hip1-e2'}), (hip1:Hipotesis {hipotesis_id:'hip1'})
CREATE (cm2b)-[:EVALUA_A]->(hip1);

MATCH (cm2c:CasoDifuso {caso_id:'M2-hip2-e1'}), (hip2:Hipotesis {hipotesis_id:'hip2'})
CREATE (cm2c)-[:EVALUA_A]->(hip2);

MATCH (cm3:CasoDifuso {caso_id:'M3-caso1'}), (inc4:Incidencia {incidencia_id:'inc4'})
CREATE (cm3)-[:EVALUA_A]->(inc4);

MATCH (cm3_lim:CasoDifuso {caso_id:'M3-limite'}), (inc5:Incidencia {incidencia_id:'inc5'})
CREATE (cm3_lim)-[:EVALUA_A]->(inc5);
