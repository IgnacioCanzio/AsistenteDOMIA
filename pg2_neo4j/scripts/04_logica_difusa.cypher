// ==============================================================================
// Script 04: Motor de Lógica Difusa
// Variables Lingüísticas (12), Etiquetas Difusas (38), Reglas Difusas (22)
// y Trazabilidad REFINA (14)
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Variables Lingüísticas (12 nodos)
// ------------------------------------------------------------------------------

// M1: Interpretación
CREATE (:VariableLinguistica {variable_id:'ConfianzaExtraccion', nombre:'ConfianzaExtraccion', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'CoincidenciaLexica', nombre:'CoincidenciaLexica', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'DistanciaCandidatos', nombre:'DistanciaCandidatos', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'SuficienciaInterpretacion', nombre:'SuficienciaInterpretacion', modulo:'M1', rol:'salida', universo_min:0.0, universo_max:100.0});

// M2: Diagnóstico
CREATE (:VariableLinguistica {variable_id:'FrecuenciaCausa', nombre:'FrecuenciaCausa', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso', nombre:'RiesgoEsfuerzoPaso', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:10.0});
CREATE (:VariableLinguistica {variable_id:'EvidenciaAcumulada', nombre:'EvidenciaAcumulada', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'PrioridadHipotesisPaso', nombre:'PrioridadHipotesisPaso', modulo:'M2', rol:'salida', universo_min:0.0, universo_max:100.0});

// M3: Severidad
CREATE (:VariableLinguistica {variable_id:'ImpactoClimatico', nombre:'ImpactoClimatico', modulo:'M3', rol:'entrada', universo_min:-30.0, universo_max:55.0});
CREATE (:VariableLinguistica {variable_id:'TiempoRestante', nombre:'TiempoRestante', modulo:'M3', rol:'entrada', universo_min:0.0, universo_max:72.0});
CREATE (:VariableLinguistica {variable_id:'SensibilidadServicio', nombre:'SensibilidadServicio', modulo:'M3', rol:'entrada', universo_min:0.0, universo_max:10.0});
CREATE (:VariableLinguistica {variable_id:'CriticidadDifusa', nombre:'CriticidadDifusa', modulo:'M3', rol:'salida', universo_min:0.0, universo_max:100.0});

// ------------------------------------------------------------------------------
// 2. Etiquetas Difusas (38 nodos con funciones gaussianas y hombros)
// ------------------------------------------------------------------------------

// Etiquetas M1 (12)
UNWIND [
  {v:'ConfianzaExtraccion', id:'ConfianzaExtraccion.Baja', n:'Baja', c:0.0, s:0.18, h:'izq', o:1},
  {v:'ConfianzaExtraccion', id:'ConfianzaExtraccion.Media', n:'Media', c:0.55, s:0.16, h:'ninguno', o:2},
  {v:'ConfianzaExtraccion', id:'ConfianzaExtraccion.Alta', n:'Alta', c:1.0, s:0.15, h:'der', o:3},

  {v:'CoincidenciaLexica', id:'CoincidenciaLexica.Debil', n:'Debil', c:0.0, s:0.20, h:'izq', o:1},
  {v:'CoincidenciaLexica', id:'CoincidenciaLexica.Parcial', n:'Parcial', c:0.55, s:0.16, h:'ninguno', o:2},
  {v:'CoincidenciaLexica', id:'CoincidenciaLexica.Fuerte', n:'Fuerte', c:1.0, s:0.15, h:'der', o:3},

  {v:'DistanciaCandidatos', id:'DistanciaCandidatos.Pequena', n:'Pequena', c:0.0, s:0.15, h:'izq', o:1},
  {v:'DistanciaCandidatos', id:'DistanciaCandidatos.Moderada', n:'Moderada', c:0.4, s:0.15, h:'ninguno', o:2},
  {v:'DistanciaCandidatos', id:'DistanciaCandidatos.Grande', n:'Grande', c:1.0, s:0.22, h:'der', o:3},

  {v:'SuficienciaInterpretacion', id:'SuficienciaInterpretacion.Insuficiente', n:'Insuficiente', c:10.0, s:15.0, h:'izq', o:1},
  {v:'SuficienciaInterpretacion', id:'SuficienciaInterpretacion.Parcial', n:'Parcial', c:50.0, s:14.0, h:'ninguno', o:2},
  {v:'SuficienciaInterpretacion', id:'SuficienciaInterpretacion.Suficiente', n:'Suficiente', c:90.0, s:14.0, h:'der', o:3}
] AS e
MATCH (v:VariableLinguistica {variable_id: e.v})
CREATE (et:EtiquetaDifusa {etiqueta_id: e.id, nombre: e.n, tipo_funcion:'gaussiana', centro: e.c, sigma: e.s, hombro: e.h})
CREATE (v)-[:TIENE_ETIQUETA {orden: e.o}]->(et);

// Etiquetas M2 (12)
UNWIND [
  {v:'FrecuenciaCausa', id:'FrecuenciaCausa.Rara', n:'Rara', c:0.0, s:0.18, h:'izq', o:1},
  {v:'FrecuenciaCausa', id:'FrecuenciaCausa.PocoFrecuente', n:'PocoFrecuente', c:0.45, s:0.16, h:'ninguno', o:2},
  {v:'FrecuenciaCausa', id:'FrecuenciaCausa.Frecuente', n:'Frecuente', c:1.0, s:0.20, h:'der', o:3},

  {v:'RiesgoEsfuerzoPaso', id:'RiesgoEsfuerzoPaso.Bajo', n:'Bajo', c:0.0, s:1.8, h:'izq', o:1},
  {v:'RiesgoEsfuerzoPaso', id:'RiesgoEsfuerzoPaso.Medio', n:'Medio', c:5.0, s:1.6, h:'ninguno', o:2},
  {v:'RiesgoEsfuerzoPaso', id:'RiesgoEsfuerzoPaso.Alto', n:'Alto', c:10.0, s:1.8, h:'der', o:3},

  {v:'EvidenciaAcumulada', id:'EvidenciaAcumulada.Debil', n:'Debil', c:0.0, s:0.18, h:'izq', o:1},
  {v:'EvidenciaAcumulada', id:'EvidenciaAcumulada.Moderada', n:'Moderada', c:0.5, s:0.16, h:'ninguno', o:2},
  {v:'EvidenciaAcumulada', id:'EvidenciaAcumulada.Fuerte', n:'Fuerte', c:1.0, s:0.18, h:'der', o:3},

  {v:'PrioridadHipotesisPaso', id:'PrioridadHipotesisPaso.Baja', n:'Baja', c:10.0, s:15.0, h:'izq', o:1},
  {v:'PrioridadHipotesisPaso', id:'PrioridadHipotesisPaso.Media', n:'Media', c:50.0, s:14.0, h:'ninguno', o:2},
  {v:'PrioridadHipotesisPaso', id:'PrioridadHipotesisPaso.Alta', n:'Alta', c:90.0, s:14.0, h:'der', o:3}
] AS e
MATCH (v:VariableLinguistica {variable_id: e.v})
CREATE (et:EtiquetaDifusa {etiqueta_id: e.id, nombre: e.n, tipo_funcion:'gaussiana', centro: e.c, sigma: e.s, hombro: e.h})
CREATE (v)-[:TIENE_ETIQUETA {orden: e.o}]->(et);

// Etiquetas M3 (14)
UNWIND [
  {v:'ImpactoClimatico', id:'ImpactoClimatico.Bajo', n:'Bajo', c:16.0, s:3.5, h:'izq', o:1},
  {v:'ImpactoClimatico', id:'ImpactoClimatico.Medio', n:'Medio', c:24.0, s:3.2, h:'ninguno', o:2},
  {v:'ImpactoClimatico', id:'ImpactoClimatico.Alto', n:'Alto', c:33.0, s:3.6, h:'ninguno', o:3},
  {v:'ImpactoClimatico', id:'ImpactoClimatico.Extremo', n:'Extremo', c:41.0, s:3.8, h:'der', o:4},

  {v:'TiempoRestante', id:'TiempoRestante.Inminente', n:'Inminente', c:0.0, s:5.0, h:'izq', o:1},
  {v:'TiempoRestante', id:'TiempoRestante.Intermedio', n:'Intermedio', c:24.0, s:11.0, h:'ninguno', o:2},
  {v:'TiempoRestante', id:'TiempoRestante.Prolongado', n:'Prolongado', c:56.0, s:13.0, h:'der', o:3},

  {v:'SensibilidadServicio', id:'SensibilidadServicio.Tolerable', n:'Tolerable', c:0.0, s:1.8, h:'izq', o:1},
  {v:'SensibilidadServicio', id:'SensibilidadServicio.Molesto', n:'Molesto', c:5.0, s:1.6, h:'ninguno', o:2},
  {v:'SensibilidadServicio', id:'SensibilidadServicio.Critico', n:'Critico', c:10.0, s:1.8, h:'der', o:3},

  {v:'CriticidadDifusa', id:'CriticidadDifusa.Baja', n:'Baja', c:12.0, s:11.0, h:'izq', o:1},
  {v:'CriticidadDifusa', id:'CriticidadDifusa.Media', n:'Media', c:42.0, s:11.0, h:'ninguno', o:2},
  {v:'CriticidadDifusa', id:'CriticidadDifusa.Alta', n:'Alta', c:70.0, s:10.0, h:'ninguno', o:3},
  {v:'CriticidadDifusa', id:'CriticidadDifusa.Emergencia', n:'Emergencia', c:93.0, s:7.5, h:'der', o:4}
] AS e
MATCH (v:VariableLinguistica {variable_id: e.v})
CREATE (et:EtiquetaDifusa {etiqueta_id: e.id, nombre: e.n, tipo_funcion:'gaussiana', centro: e.c, sigma: e.s, hombro: e.h})
CREATE (v)-[:TIENE_ETIQUETA {orden: e.o}]->(et);

// ------------------------------------------------------------------------------
// 3. Reglas Difusas de M1 (7 reglas: 6 activas + IF7 de cobertura)
// ------------------------------------------------------------------------------

CREATE (:ReglaDifusa {regla_id:'IF1', modulo:'M1', activa:true, origen_pg1:'I5', consecuente:'SuficienciaInterpretacion.Suficiente',
  expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Fuerte Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Suficiente'});

CREATE (:ReglaDifusa {regla_id:'IF2', modulo:'M1', activa:true, origen_pg1:'I3', consecuente:'SuficienciaInterpretacion.Suficiente',
  expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Parcial Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Suficiente'});

CREATE (:ReglaDifusa {regla_id:'IF3', modulo:'M1', activa:true, origen_pg1:'I6', consecuente:'SuficienciaInterpretacion.Parcial',
  expresion:'SI (ConfianzaExtraccion ES Media O CoincidenciaLexica ES Parcial) Y DistanciaCandidatos ES Moderada ENTONCES SuficienciaInterpretacion ES Parcial'});

CREATE (:ReglaDifusa {regla_id:'IF4', modulo:'M1', activa:true, origen_pg1:'I4', consecuente:'SuficienciaInterpretacion.Parcial',
  expresion:'SI DistanciaCandidatos ES Pequena Y NO (ConfianzaExtraccion ES Baja) ENTONCES SuficienciaInterpretacion ES Parcial'});

CREATE (:ReglaDifusa {regla_id:'IF5', modulo:'M1', activa:true, origen_pg1:'I3', consecuente:'SuficienciaInterpretacion.Insuficiente',
  expresion:'SI ConfianzaExtraccion ES Baja O CoincidenciaLexica ES Debil ENTONCES SuficienciaInterpretacion ES Insuficiente'});

CREATE (:ReglaDifusa {regla_id:'IF6', modulo:'M1', activa:true, origen_pg1:'I4', consecuente:'SuficienciaInterpretacion.Parcial',
  expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Fuerte Y DistanciaCandidatos ES Moderada ENTONCES SuficienciaInterpretacion ES Parcial'});

CREATE (:ReglaDifusa {regla_id:'IF7', modulo:'M1', activa:false, origen_pg1:'I6', consecuente:'SuficienciaInterpretacion.Parcial',
  expresion:'(cobertura) SI ConfianzaExtraccion ES Media Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Parcial'});

// Conexión de antecedentes y consecuentes de M1
MATCH (r:ReglaDifusa {regla_id:'IF1'}),
      (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}),
      (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Fuerte'}),
      (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Suficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF2'}),
      (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}),
      (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Parcial'}),
      (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Suficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF3'}),
      (a1:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Media'}),
      (a2:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Parcial'}),
      (b:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Moderada'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1),
       (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF4'}),
      (a:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Pequena'}),
      (b:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Baja'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF5'}),
      (a1:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Baja'}),
      (a2:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Debil'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Insuficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1),
       (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF6'}),
      (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}),
      (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Fuerte'}),
      (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Moderada'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF7'}),
      (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Media'}),
      (b:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}),
      (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

// ------------------------------------------------------------------------------
// 4. Reglas Difusas de M2 (7 reglas: 6 activas + RF7 de cobertura)
// ------------------------------------------------------------------------------

CREATE (:ReglaDifusa {regla_id:'RF1', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Alta',
  expresion:'SI (FrecuenciaCausa ES Frecuente O EvidenciaAcumulada ES Fuerte) Y RiesgoEsfuerzoPaso ES Bajo ENTONCES PrioridadHipotesisPaso ES Alta'});

CREATE (:ReglaDifusa {regla_id:'RF2', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Alta',
  expresion:'SI FrecuenciaCausa ES Frecuente Y EvidenciaAcumulada ES Fuerte Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Alta'});

CREATE (:ReglaDifusa {regla_id:'RF3', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media',
  expresion:'SI FrecuenciaCausa ES PocoFrecuente Y EvidenciaAcumulada ES Moderada Y NO (RiesgoEsfuerzoPaso ES Alto) ENTONCES PrioridadHipotesisPaso ES Media'});

CREATE (:ReglaDifusa {regla_id:'RF4', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media',
  expresion:'SI FrecuenciaCausa ES Frecuente Y EvidenciaAcumulada ES Moderada Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Media'});

CREATE (:ReglaDifusa {regla_id:'RF5', modulo:'M2', activa:true, origen_pg1:'R8', consecuente:'PrioridadHipotesisPaso.Baja',
  expresion:'SI RiesgoEsfuerzoPaso ES Alto O EvidenciaAcumulada ES Debil ENTONCES PrioridadHipotesisPaso ES Baja'});

CREATE (:ReglaDifusa {regla_id:'RF6', modulo:'M2', activa:true, origen_pg1:'R12', consecuente:'PrioridadHipotesisPaso.Baja',
  expresion:'SI FrecuenciaCausa ES Rara Y NO (EvidenciaAcumulada ES Fuerte) ENTONCES PrioridadHipotesisPaso ES Baja'});

CREATE (:ReglaDifusa {regla_id:'RF7', modulo:'M2', activa:false, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media',
  expresion:'(cobertura) SI EvidenciaAcumulada ES Fuerte Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Media'});

// Conexión de antecedentes y consecuentes de M2
MATCH (r:ReglaDifusa {regla_id:'RF1'}),
      (a1:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}),
      (a2:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}),
      (b:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Bajo'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1),
       (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF2'}),
      (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}),
      (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}),
      (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF3'}),
      (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.PocoFrecuente'}),
      (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Moderada'}),
      (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Alto'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:true}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF4'}),
      (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}),
      (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Moderada'}),
      (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF5'}),
      (a1:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Alto'}),
      (a2:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Debil'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1),
       (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF6'}),
      (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Rara'}),
      (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF7'}),
      (a:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}),
      (b:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}),
      (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

// ------------------------------------------------------------------------------
// 5. Reglas Difusas de M3 (8 reglas: 7 activas + F7 de cobertura)
// ------------------------------------------------------------------------------

CREATE (:ReglaDifusa {regla_id:'F1', modulo:'M3', activa:true, origen_pg1:'F1', consecuente:'CriticidadDifusa.Emergencia',
  expresion:'SI SensibilidadServicio ES Critico Y ImpactoClimatico ES Extremo ENTONCES CriticidadDifusa ES Emergencia'});

CREATE (:ReglaDifusa {regla_id:'F2', modulo:'M3', activa:true, origen_pg1:'F2', consecuente:'CriticidadDifusa.Alta',
  expresion:'SI SensibilidadServicio ES Critico Y ImpactoClimatico ES Alto ENTONCES CriticidadDifusa ES Alta'});

CREATE (:ReglaDifusa {regla_id:'F3', modulo:'M3', activa:true, origen_pg1:'F3', consecuente:'CriticidadDifusa.Alta',
  expresion:'SI SensibilidadServicio ES Molesto Y ImpactoClimatico ES Alto Y NO (TiempoRestante ES Inminente) ENTONCES CriticidadDifusa ES Alta'});

CREATE (:ReglaDifusa {regla_id:'F4a', modulo:'M3', activa:true, origen_pg1:'F4', consecuente:'CriticidadDifusa.Baja',
  expresion:'SI SensibilidadServicio ES Tolerable ENTONCES CriticidadDifusa ES Baja'});

CREATE (:ReglaDifusa {regla_id:'F4b', modulo:'M3', activa:true, origen_pg1:'F4', consecuente:'CriticidadDifusa.Baja',
  expresion:'SI ImpactoClimatico ES Bajo Y NO (SensibilidadServicio ES Critico) ENTONCES CriticidadDifusa ES Baja'});

CREATE (:ReglaDifusa {regla_id:'F5', modulo:'M3', activa:true, origen_pg1:'F5', consecuente:'CriticidadDifusa.Media',
  expresion:'SI TiempoRestante ES Inminente Y NO (SensibilidadServicio ES Critico) ENTONCES CriticidadDifusa ES Media'});

CREATE (:ReglaDifusa {regla_id:'F6', modulo:'M3', activa:true, origen_pg1:'F6', consecuente:'CriticidadDifusa.Alta',
  expresion:'SI TiempoRestante ES Prolongado Y SensibilidadServicio ES Critico ENTONCES CriticidadDifusa ES Alta'});

CREATE (:ReglaDifusa {regla_id:'F7', modulo:'M3', activa:false, origen_pg1:'F6', consecuente:'CriticidadDifusa.Alta',
  expresion:'(cobertura) SI SensibilidadServicio ES Critico ENTONCES CriticidadDifusa ES Alta'});

// Conexión de antecedentes y consecuentes de M3
MATCH (r:ReglaDifusa {regla_id:'F1'}),
      (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Extremo'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Emergencia'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F2'}),
      (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Alto'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F3'}),
      (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Molesto'}),
      (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Alto'}),
      (c:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Inminente'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:true}]->(c),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F4a'}),
      (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Tolerable'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F4b'}),
      (a:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Bajo'}),
      (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F5'}),
      (a:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Inminente'}),
      (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F6'}),
      (a:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Prolongado'}),
      (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F7'}),
      (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}),
      (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a),
       (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

// ------------------------------------------------------------------------------
// 6. Relaciones REFINA (14 relaciones entre ReglaDifusa y ReglaCrisp)
// ------------------------------------------------------------------------------

MATCH (rf1:ReglaDifusa {regla_id:'RF1'}), (r7:ReglaCrisp {regla_id:'R7'}) CREATE (rf1)-[:REFINA]->(r7);
MATCH (rf2:ReglaDifusa {regla_id:'RF2'}), (r7:ReglaCrisp {regla_id:'R7'}) CREATE (rf2)-[:REFINA]->(r7);
MATCH (rf3:ReglaDifusa {regla_id:'RF3'}), (r7:ReglaCrisp {regla_id:'R7'}) CREATE (rf3)-[:REFINA]->(r7);
MATCH (rf4:ReglaDifusa {regla_id:'RF4'}), (r7:ReglaCrisp {regla_id:'R7'}) CREATE (rf4)-[:REFINA]->(r7);
MATCH (rf5:ReglaDifusa {regla_id:'RF5'}), (r8:ReglaCrisp {regla_id:'R8'}) CREATE (rf5)-[:REFINA]->(r8);
MATCH (rf6:ReglaDifusa {regla_id:'RF6'}), (r12:ReglaCrisp {regla_id:'R12'}) CREATE (rf6)-[:REFINA]->(r12);
MATCH (rf7:ReglaDifusa {regla_id:'RF7'}), (r7:ReglaCrisp {regla_id:'R7'}) CREATE (rf7)-[:REFINA]->(r7);

MATCH (if1:ReglaDifusa {regla_id:'IF1'}), (i5:ReglaCrisp {regla_id:'I5'}) CREATE (if1)-[:REFINA]->(i5);
MATCH (if2:ReglaDifusa {regla_id:'IF2'}), (i3:ReglaCrisp {regla_id:'I3'}) CREATE (if2)-[:REFINA]->(i3);
MATCH (if3:ReglaDifusa {regla_id:'IF3'}), (i6:ReglaCrisp {regla_id:'I6'}) CREATE (if3)-[:REFINA]->(i6);
MATCH (if4:ReglaDifusa {regla_id:'IF4'}), (i4:ReglaCrisp {regla_id:'I4'}) CREATE (if4)-[:REFINA]->(i4);
MATCH (if5:ReglaDifusa {regla_id:'IF5'}), (i3:ReglaCrisp {regla_id:'I3'}) CREATE (if5)-[:REFINA]->(i3);
MATCH (if6:ReglaDifusa {regla_id:'IF6'}), (i4:ReglaCrisp {regla_id:'I4'}) CREATE (if6)-[:REFINA]->(i4);
MATCH (if7:ReglaDifusa {regla_id:'IF7'}), (i6:ReglaCrisp {regla_id:'I6'}) CREATE (if7)-[:REFINA]->(i6);
