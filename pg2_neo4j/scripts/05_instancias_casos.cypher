// ==============================================================================
// Script 05: Instancias y Casos de Uso Integrados
// Anfitrión, Inmuebles, Artefactos, Huéspedes, Reservas y los 6 Casos de Uso
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Anfitrión e Inmuebles (1 Anfitrión, 5 Inmuebles)
// ------------------------------------------------------------------------------

CREATE (anf1:Anfitrion {anfitrion_id:'anf1', nombre:'Roberto Gómez', telefono:'+54 9 261 456-7890', email:'roberto@domia-alquileres.com'});

CREATE (inm101:Inmueble {inmueble_id:'inm101', nombre:'Depto 101', direccion:'Av. San Martín 1234, Piso 1, Mendoza', capacidad:3});
CREATE (inm102:Inmueble {inmueble_id:'inm102', nombre:'Depto 102', direccion:'Av. San Martín 1234, Piso 1, Mendoza', capacidad:2});
CREATE (inm103:Inmueble {inmueble_id:'inm103', nombre:'Depto 103', direccion:'Av. San Martín 1234, Piso 2, Mendoza', capacidad:4});
CREATE (inm104:Inmueble {inmueble_id:'inm104', nombre:'Depto 104', direccion:'Av. San Martín 1234, Piso 2, Mendoza', capacidad:5});
CREATE (inm105:Inmueble {inmueble_id:'inm105', nombre:'Depto 105', direccion:'Av. San Martín 1234, Piso 3, Mendoza', capacidad:2});

MATCH (anf:Anfitrion {anfitrion_id:'anf1'}),
      (i1:Inmueble {inmueble_id:'inm101'}),
      (i2:Inmueble {inmueble_id:'inm102'}),
      (i3:Inmueble {inmueble_id:'inm103'}),
      (i4:Inmueble {inmueble_id:'inm104'}),
      (i5:Inmueble {inmueble_id:'inm105'})
CREATE (anf)-[:ADMINISTRA]->(i1),
       (anf)-[:ADMINISTRA]->(i2),
       (anf)-[:ADMINISTRA]->(i3),
       (anf)-[:ADMINISTRA]->(i4),
       (anf)-[:ADMINISTRA]->(i5);

// ------------------------------------------------------------------------------
// 2. Artefactos instalados (6 nodos con subetiquetas)
// ------------------------------------------------------------------------------

CREATE (tg01:Artefacto:TermotanqueGas {artefacto_id:'tg01', tipo:'TermotanqueGas', marca:'Eskabe', modelo:'Aquapiú 80L', ubicacion:'Lavadero', tiene_piloto:true});
CREATE (cer01:Artefacto:CerraduraElectronica {artefacto_id:'cer01', tipo:'CerraduraElectronica', marca:'Samsung', modelo:'SHP-DH538', ubicacion:'Puerta Principal'});
CREATE (spl01:Artefacto:SplitAC {artefacto_id:'spl01', tipo:'SplitAC', marca:'BGH', modelo:'Silent Air 3000', ubicacion:'Estar Comedor'});
CREATE (te01:Artefacto:TermotanqueElectrico {artefacto_id:'te01', tipo:'TermotanqueElectrico', marca:'Philco', modelo:'TE-50L', ubicacion:'Baño Principal'});
CREATE (tg02:Artefacto:TermotanqueGas {artefacto_id:'tg02', tipo:'TermotanqueGas', marca:'Rheem', modelo:'TG-120', ubicacion:'Cocina', tiene_piloto:true});
CREATE (tg03:Artefacto:TermotanqueGas {artefacto_id:'tg03', tipo:'TermotanqueGas', marca:'Orbis', modelo:'Eurotrend', ubicacion:'Cocina', tiene_piloto:true});

// Inmuebles CONTIENE Artefactos
MATCH (i1:Inmueble {inmueble_id:'inm101'}), (tg01:Artefacto {artefacto_id:'tg01'}) CREATE (i1)-[:CONTIENE]->(tg01);
MATCH (i2:Inmueble {inmueble_id:'inm102'}), (cer01:Artefacto {artefacto_id:'cer01'}) CREATE (i2)-[:CONTIENE]->(cer01);
MATCH (i3:Inmueble {inmueble_id:'inm103'}), (spl01:Artefacto {artefacto_id:'spl01'}) CREATE (i3)-[:CONTIENE]->(spl01);
MATCH (i4:Inmueble {inmueble_id:'inm104'}), (te01:Artefacto {artefacto_id:'te01'}), (tg02:Artefacto {artefacto_id:'tg02'})
CREATE (i4)-[:CONTIENE]->(te01), (i4)-[:CONTIENE]->(tg02);
MATCH (i5:Inmueble {inmueble_id:'inm105'}), (tg03:Artefacto {artefacto_id:'tg03'}) CREATE (i5)-[:CONTIENE]->(tg03);

// Artefactos DEPENDE_DE Servicios
MATCH (tg01:Artefacto {artefacto_id:'tg01'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg01)-[:DEPENDE_DE]->(s_ac);
MATCH (cer01:Artefacto {artefacto_id:'cer01'}), (s_acc:Servicio {servicio_id:'acceso_principal'}) CREATE (cer01)-[:DEPENDE_DE]->(s_acc);
MATCH (spl01:Artefacto {artefacto_id:'spl01'}), (s_cl:Servicio {servicio_id:'climatizacion'}) CREATE (spl01)-[:DEPENDE_DE]->(s_cl);
MATCH (te01:Artefacto {artefacto_id:'te01'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (te01)-[:DEPENDE_DE]->(s_ac);
MATCH (tg02:Artefacto {artefacto_id:'tg02'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg02)-[:DEPENDE_DE]->(s_ac);
MATCH (tg03:Artefacto {artefacto_id:'tg03'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg03)-[:DEPENDE_DE]->(s_ac);

// Artefactos MANIFIESTA Síntomas típicos
MATCH (tg01:Artefacto {artefacto_id:'tg01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (tg01)-[:MANIFIESTA]->(sin_ac);
MATCH (cer01:Artefacto {artefacto_id:'cer01'}), (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta'}) CREATE (cer01)-[:MANIFIESTA]->(sin_tec);
MATCH (spl01:Artefacto {artefacto_id:'spl01'}), (sin_enf:Sintoma {sintoma_id:'no_enfria'}) CREATE (spl01)-[:MANIFIESTA]->(sin_enf);
MATCH (te01:Artefacto {artefacto_id:'te01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (te01)-[:MANIFIESTA]->(sin_ac);
MATCH (tg02:Artefacto {artefacto_id:'tg02'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (tg02)-[:MANIFIESTA]->(sin_ac);
MATCH (tg03:Artefacto {artefacto_id:'tg03'}), (sin_gas:Sintoma {sintoma_id:'olor_a_gas'}) CREATE (tg03)-[:MANIFIESTA]->(sin_gas);

// ------------------------------------------------------------------------------
// 3. Huéspedes y Reservas (5 Huéspedes, 5 Reservas)
// ------------------------------------------------------------------------------

CREATE (h1:Huesped {huesped_id:'h1', nombre:'Juan Pérez', telefono:'+54 9 11 1111-1111', idioma:'es'});
CREATE (h2:Huesped {huesped_id:'h2', nombre:'Ana Gómez', telefono:'+54 9 11 2222-2222', idioma:'es'});
CREATE (h3:Huesped {huesped_id:'h3', nombre:'Carlos Ruiz', telefono:'+54 9 11 3333-3333', idioma:'es'});
CREATE (h4:Huesped {huesped_id:'h4', nombre:'María López', telefono:'+54 9 11 4444-4444', idioma:'es'});
CREATE (h5:Huesped {huesped_id:'h5', nombre:'Laura Torres', telefono:'+54 9 11 5555-5555', idioma:'es'});

CREATE (res1:Reserva {reserva_id:'res1', fecha_inicio:'2026-10-28', fecha_fin:'2026-11-02', activa:true});
CREATE (res2:Reserva {reserva_id:'res2', fecha_inicio:'2026-10-29', fecha_fin:'2026-10-31', activa:true});
CREATE (res3:Reserva {reserva_id:'res3', fecha_inicio:'2026-10-25', fecha_fin:'2026-11-01', activa:true});
CREATE (res4:Reserva {reserva_id:'res4', fecha_inicio:'2026-10-30', fecha_fin:'2026-11-03', activa:true});
CREATE (res5:Reserva {reserva_id:'res5', fecha_inicio:'2026-10-31', fecha_fin:'2026-11-05', activa:true});

MATCH (h1:Huesped {huesped_id:'h1'}), (h2:Huesped {huesped_id:'h2'}), (h3:Huesped {huesped_id:'h3'}), (h4:Huesped {huesped_id:'h4'}), (h5:Huesped {huesped_id:'h5'}),
      (res1:Reserva {reserva_id:'res1'}), (res2:Reserva {reserva_id:'res2'}), (res3:Reserva {reserva_id:'res3'}), (res4:Reserva {reserva_id:'res4'}), (res5:Reserva {reserva_id:'res5'}),
      (i1:Inmueble {inmueble_id:'inm101'}), (i2:Inmueble {inmueble_id:'inm102'}), (i3:Inmueble {inmueble_id:'inm103'}), (i4:Inmueble {inmueble_id:'inm104'}), (i5:Inmueble {inmueble_id:'inm105'})
CREATE (h1)-[:OCUPA]->(res1), (res1)-[:CORRESPONDE_A]->(i1), (h1)-[:SE_ALOJA_EN]->(i1),
       (h2)-[:OCUPA]->(res2), (res2)-[:CORRESPONDE_A]->(i2), (h2)-[:SE_ALOJA_EN]->(i2),
       (h3)-[:OCUPA]->(res3), (res3)-[:CORRESPONDE_A]->(i3), (h3)-[:SE_ALOJA_EN]->(i3),
       (h4)-[:OCUPA]->(res4), (res4)-[:CORRESPONDE_A]->(i4), (h4)-[:SE_ALOJA_EN]->(i4),
       (h5)-[:OCUPA]->(res5), (res5)-[:CORRESPONDE_A]->(i5), (h5)-[:SE_ALOJA_EN]->(i5);

// ------------------------------------------------------------------------------
// 4. Caso 1: Positivo Resuelto por Huésped (M1 -> M2 -> S2)
// ------------------------------------------------------------------------------

CREATE (rel1:Relato {relato_id:'rel1', texto:'no sale agua caliente en la ducha'});
CREATE (cd1:CandidatoExtraido {candidato_id:'cd1', artefacto_mencionado:'tg01', sintoma_mencionado:'sin_agua_caliente', confianza:0.90, polaridad:'afirmativa', estado:'normalizado'});
CREATE (ev1:EvaluacionSuficiencia {evaluacion_id:'ev1', resultado:'suficiente', ronda:1});
CREATE (rep1:ReporteEstructurado {reporte_id:'rep1', senal_seguridad:false, estado:'emitido'});
CREATE (ses1:SesionDiagnostico {sesion_id:'ses1', estado:'resuelta_por_huesped', max_pasos:5, pasos_intentados:2});

CREATE (hip1:Hipotesis {hipotesis_id:'hip1', estado:'confirmada', evidencia_acumulada:0.85});
CREATE (hip2:Hipotesis {hipotesis_id:'hip2', estado:'descartada', evidencia_acumulada:0.0});
CREATE (hip3:Hipotesis {hipotesis_id:'hip3', estado:'vigente', evidencia_acumulada:0.10});

CREATE (r1:RespuestaPaso {respuesta_id:'r1', resultado:'si', detalle:'La llave de gas está abierta'});
CREATE (r2:RespuestaPaso {respuesta_id:'r2', resultado:'si', detalle:'El piloto encendió y quedó prendido'});

CREATE (df1:DiagnosticoFinal {diagnostico_id:'df1', causa_diagnosticada:'piloto_apagado', resoluble_por_huesped:true, riesgo_seguridad:false});
CREATE (inc1:Incidencia {incidencia_id:'inc1', estado:'resuelta_por_huesped'});

MATCH (h1:Huesped {huesped_id:'h1'}), (res1:Reserva {reserva_id:'res1'}), (rel1:Relato {relato_id:'rel1'}),
      (cd1:CandidatoExtraido {candidato_id:'cd1'}), (ev1:EvaluacionSuficiencia {evaluacion_id:'ev1'}),
      (rep1:ReporteEstructurado {reporte_id:'rep1'}), (ses1:SesionDiagnostico {sesion_id:'ses1'}),
      (hip1:Hipotesis {hipotesis_id:'hip1'}), (hip2:Hipotesis {hipotesis_id:'hip2'}), (hip3:Hipotesis {hipotesis_id:'hip3'}),
      (c_pil:CausaRaiz {causa_id:'piloto_apagado'}), (c_llave:CausaRaiz {causa_id:'llave_gas_cerrada'}), (c_tc:CausaRaiz {causa_id:'falla_termocupla'}),
      (p1:PasoVerificacion {paso_id:'p1'}), (p2:PasoVerificacion {paso_id:'p2'}),
      (r1:RespuestaPaso {respuesta_id:'r1'}), (r2:RespuestaPaso {respuesta_id:'r2'}),
      (df1:DiagnosticoFinal {diagnostico_id:'df1'}), (inc1:Incidencia {incidencia_id:'inc1'}),
      (tg01:Artefacto {artefacto_id:'tg01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}),
      (s_ac:Servicio {servicio_id:'agua_caliente'}), (i1:Inmueble {inmueble_id:'inm101'})
CREATE (h1)-[:ESCRIBE]->(rel1),
       (rel1)-[:SE_ASOCIA_A]->(res1),
       (cd1)-[:SE_EXTRAE_DE]->(rel1),
       (cd1)-[:APUNTA_A]->(tg01),
       (cd1)-[:APUNTA_A]->(sin_ac),
       (ev1)-[:ANALIZA]->(rel1),
       (ev1)-[:EVALUA]->(cd1),
       (ev1)-[:PRODUCE]->(rep1),
       (rep1)-[:IDENTIFICA]->(tg01),
       (rep1)-[:CONTIENE]->(sin_ac),
       (rep1)-[:INICIA]->(ses1),
       (ses1)-[:GESTIONA]->(inc1),
       (ses1)-[:MANTIENE]->(hip1),
       (ses1)-[:MANTIENE]->(hip2),
       (ses1)-[:MANTIENE]->(hip3),
       (hip1)-[:SE_REFIERE_A]->(c_pil),
       (hip2)-[:SE_REFIERE_A]->(c_llave),
       (hip3)-[:SE_REFIERE_A]->(c_tc),
       (h1)-[:EMITE]->(r1),
       (h1)-[:EMITE]->(r2),
       (r1)-[:RESPONDE_A]->(p1),
       (r2)-[:RESPONDE_A]->(p2),
       (r1)-[:ACTUALIZA {regla:'R11'}]->(hip2),
       (r1)-[:ACTUALIZA {regla:'R11'}]->(hip1),
       (r2)-[:ACTUALIZA {regla:'R3'}]->(hip1),
       (ses1)-[:PRODUCE]->(df1),
       (df1)-[:DIAGNOSTICA]->(c_pil),
       (df1)-[:CLASIFICA]->(inc1),
       (inc1)-[:VINCULA]->(tg01),
       (inc1)-[:AFECTA_A]->(i1),
       (inc1)-[:AFECTA_A]->(s_ac);

// ------------------------------------------------------------------------------
// 5. Caso 2: Negativo Escalado (M2 -> M3: R4, R5)
// ------------------------------------------------------------------------------

CREATE (rel2:Relato {relato_id:'rel2', texto:'el teclado de la puerta no responde'});
CREATE (rep2:ReporteEstructurado {reporte_id:'rep2', senal_seguridad:false, estado:'emitido'});
CREATE (ses2:SesionDiagnostico {sesion_id:'ses2', estado:'escalada', max_pasos:3, pasos_intentados:1});

CREATE (hip4:Hipotesis {hipotesis_id:'hip4', estado:'descartada', evidencia_acumulada:0.0});
CREATE (hip5:Hipotesis {hipotesis_id:'hip5', estado:'vigente', evidencia_acumulada:0.50});

CREATE (r3:RespuestaPaso {respuesta_id:'r3', resultado:'no', detalle:'El código maestro no abre la cerradura'});

CREATE (df2:DiagnosticoFinal {diagnostico_id:'df2', causa_diagnosticada:'bloqueo sin causa determinada', resoluble_por_huesped:false, riesgo_seguridad:false});
CREATE (ctx2:ContextoIncidencia {contexto_id:'ctx2', temperatura_actual:22.0, horas_restantes:12.0, dato_estimado:false});
CREATE (inc2:Incidencia {incidencia_id:'inc2', estado:'escalada'});

MATCH (h2:Huesped {huesped_id:'h2'}), (res2:Reserva {reserva_id:'res2'}), (rel2:Relato {relato_id:'rel2'}),
      (rep2:ReporteEstructurado {reporte_id:'rep2'}), (ses2:SesionDiagnostico {sesion_id:'ses2'}),
      (hip4:Hipotesis {hipotesis_id:'hip4'}), (hip5:Hipotesis {hipotesis_id:'hip5'}),
      (c_pilas:CausaRaiz {causa_id:'pilas_agotadas'}), (c_trab:CausaRaiz {causa_id:'mecanismo_trabado'}),
      (p3:PasoVerificacion {paso_id:'p3'}), (r3:RespuestaPaso {respuesta_id:'r3'}),
      (df2:DiagnosticoFinal {diagnostico_id:'df2'}), (inc2:Incidencia {incidencia_id:'inc2'}),
      (ctx2:ContextoIncidencia {contexto_id:'ctx2'}),
      (cer01:Artefacto {artefacto_id:'cer01'}), (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta'}),
      (s_acc:Servicio {servicio_id:'acceso_principal'}), (i2:Inmueble {inmueble_id:'inm102'})
CREATE (h2)-[:ESCRIBE]->(rel2),
       (rel2)-[:SE_ASOCIA_A]->(res2),
       (rep2)-[:IDENTIFICA]->(cer01),
       (rep2)-[:CONTIENE]->(sin_tec),
       (rep2)-[:INICIA]->(ses2),
       (ses2)-[:GESTIONA]->(inc2),
       (ses2)-[:MANTIENE]->(hip4),
       (ses2)-[:MANTIENE]->(hip5),
       (hip4)-[:SE_REFIERE_A]->(c_pilas),
       (hip5)-[:SE_REFIERE_A]->(c_trab),
       (h2)-[:EMITE]->(r3),
       (r3)-[:RESPONDE_A]->(p3),
       (r3)-[:ACTUALIZA {regla:'R4'}]->(hip4),
       (ses2)-[:PRODUCE]->(df2),
       (df2)-[:CLASIFICA]->(inc2),
       (inc2)-[:VINCULA]->(cer01),
       (inc2)-[:AFECTA_A]->(i2),
       (inc2)-[:AFECTA_A]->(s_acc),
       (inc2)-[:TIENE_CONTEXTO]->(ctx2),
       (ctx2)-[:PROVIENE_DE]->(res2);

// ------------------------------------------------------------------------------
// 6. Caso 3: Ambigüedad Difusa M1 (Pregunta Aclaratoria)
// ------------------------------------------------------------------------------

CREATE (rel3:Relato {relato_id:'rel3', texto:'el aparato del baño tira el agua medio tibia'});
CREATE (cd3a:CandidatoExtraido {candidato_id:'cd3a', artefacto_mencionado:'te01', sintoma_mencionado:'sin_agua_caliente', confianza:0.72, polaridad:'afirmativa', estado:'normalizado'});
CREATE (cd3b:CandidatoExtraido {candidato_id:'cd3b', artefacto_mencionado:'tg02', sintoma_mencionado:'sin_agua_caliente', confianza:0.37, polaridad:'afirmativa', estado:'normalizado'});
CREATE (ev3:EvaluacionSuficiencia {evaluacion_id:'ev3', resultado:'insuficiente_con_rondas', ronda:1});
CREATE (pq1:PreguntaAclaratoria {pregunta_id:'pq1', texto:'¿El equipo es el termotanque eléctrico del baño o el termotanque a gas de la cocina?', tipo:'cerrada_opciones', ronda:1, max_rondas:2});

MATCH (h4:Huesped {huesped_id:'h4'}), (res4:Reserva {reserva_id:'res4'}), (rel3:Relato {relato_id:'rel3'}),
      (cd3a:CandidatoExtraido {candidato_id:'cd3a'}), (cd3b:CandidatoExtraido {candidato_id:'cd3b'}),
      (ev3:EvaluacionSuficiencia {evaluacion_id:'ev3'}), (pq1:PreguntaAclaratoria {pregunta_id:'pq1'}),
      (te01:Artefacto {artefacto_id:'te01'}), (tg02:Artefacto {artefacto_id:'tg02'})
CREATE (h4)-[:ESCRIBE]->(rel3),
       (rel3)-[:SE_ASOCIA_A]->(res4),
       (cd3a)-[:SE_EXTRAE_DE]->(rel3),
       (cd3b)-[:SE_EXTRAE_DE]->(rel3),
       (cd3a)-[:APUNTA_A]->(te01),
       (cd3b)-[:APUNTA_A]->(tg02),
       (ev3)-[:ANALIZA]->(rel3),
       (ev3)-[:EVALUA]->(cd3a),
       (ev3)-[:EVALUA]->(cd3b),
       (ev3)-[:GENERA]->(pq1);

// ------------------------------------------------------------------------------
// 7. Caso 4: Difuso M3 Severo (Ola de Calor, Split Roto)
// ------------------------------------------------------------------------------

CREATE (rel4:Relato {relato_id:'rel4', texto:'el aire no enfría y hace muchísimo calor'});
CREATE (rep4:ReporteEstructurado {reporte_id:'rep4', senal_seguridad:false, estado:'emitido'});
CREATE (ses4:SesionDiagnostico {sesion_id:'ses4', estado:'escalada', max_pasos:4, pasos_intentados:1});

CREATE (hip6:Hipotesis {hipotesis_id:'hip6', estado:'descartada', evidencia_acumulada:0.0});
CREATE (hip7:Hipotesis {hipotesis_id:'hip7', estado:'confirmada', evidencia_acumulada:0.85});

CREATE (r4:RespuestaPaso {respuesta_id:'r4', resultado:'si', detalle:'Limpié los filtros pero sigue sin enfriar'});

CREATE (df4:DiagnosticoFinal {diagnostico_id:'df4', causa_diagnosticada:'gas_refrigerante_bajo', resoluble_por_huesped:false, riesgo_seguridad:false});
CREATE (ctx4:ContextoIncidencia {contexto_id:'ctx4', temperatura_actual:38.0, horas_restantes:48.0, dato_estimado:false});
CREATE (inc4:Incidencia {incidencia_id:'inc4', estado:'escalada'});

MATCH (h3:Huesped {huesped_id:'h3'}), (res3:Reserva {reserva_id:'res3'}), (rel4:Relato {relato_id:'rel4'}),
      (rep4:ReporteEstructurado {reporte_id:'rep4'}), (ses4:SesionDiagnostico {sesion_id:'ses4'}),
      (hip6:Hipotesis {hipotesis_id:'hip6'}), (hip7:Hipotesis {hipotesis_id:'hip7'}),
      (c_filtro:CausaRaiz {causa_id:'filtro_sucio'}), (c_gas:CausaRaiz {causa_id:'gas_refrigerante_bajo'}),
      (p10:PasoVerificacion {paso_id:'p10'}), (r4:RespuestaPaso {respuesta_id:'r4'}),
      (df4:DiagnosticoFinal {diagnostico_id:'df4'}), (inc4:Incidencia {incidencia_id:'inc4'}),
      (ctx4:ContextoIncidencia {contexto_id:'ctx4'}),
      (spl01:Artefacto {artefacto_id:'spl01'}), (sin_enf:Sintoma {sintoma_id:'no_enfria'}),
      (s_cl:Servicio {servicio_id:'climatizacion'}), (i3:Inmueble {inmueble_id:'inm103'})
CREATE (h3)-[:ESCRIBE]->(rel4),
       (rel4)-[:SE_ASOCIA_A]->(res3),
       (rep4)-[:IDENTIFICA]->(spl01),
       (rep4)-[:CONTIENE]->(sin_enf),
       (rep4)-[:INICIA]->(ses4),
       (ses4)-[:GESTIONA]->(inc4),
       (ses4)-[:MANTIENE]->(hip6),
       (ses4)-[:MANTIENE]->(hip7),
       (hip6)-[:SE_REFIERE_A]->(c_filtro),
       (hip7)-[:SE_REFIERE_A]->(c_gas),
       (h3)-[:EMITE]->(r4),
       (r4)-[:RESPONDE_A]->(p10),
       (r4)-[:ACTUALIZA {regla:'R11'}]->(hip6),
       (ses4)-[:PRODUCE]->(df4),
       (df4)-[:DIAGNOSTICA]->(c_gas),
       (df4)-[:CLASIFICA]->(inc4),
       (inc4)-[:VINCULA]->(spl01),
       (inc4)-[:AFECTA_A]->(i3),
       (inc4)-[:AFECTA_A]->(s_cl),
       (inc4)-[:TIENE_CONTEXTO]->(ctx4),
       (ctx4)-[:PROVIENE_DE]->(res3);

// ------------------------------------------------------------------------------
// 8. Caso 5: Difuso M3 Límite (Check-out Inminente)
// ------------------------------------------------------------------------------

CREATE (rel5:Relato {relato_id:'rel5', texto:'no hay agua caliente y salimos en unas horas'});
CREATE (rep5:ReporteEstructurado {reporte_id:'rep5', senal_seguridad:false, estado:'emitido'});
CREATE (ses5:SesionDiagnostico {sesion_id:'ses5', estado:'escalada', max_pasos:4, pasos_intentados:1});

CREATE (hip8:Hipotesis {hipotesis_id:'hip8', estado:'descartada', evidencia_acumulada:0.0});
CREATE (hip9:Hipotesis {hipotesis_id:'hip9', estado:'confirmada', evidencia_acumulada:0.85});

CREATE (r5:RespuestaPaso {respuesta_id:'r5', resultado:'no', detalle:'La llave térmica estaba arriba, no saltó'});

CREATE (df5:DiagnosticoFinal {diagnostico_id:'df5', causa_diagnosticada:'resistencia_quemada', resoluble_por_huesped:false, riesgo_seguridad:false});
CREATE (ctx5:ContextoIncidencia {contexto_id:'ctx5', temperatura_actual:31.0, horas_restantes:3.5, dato_estimado:false});
CREATE (inc5:Incidencia {incidencia_id:'inc5', estado:'escalada'});

MATCH (h4:Huesped {huesped_id:'h4'}), (res4:Reserva {reserva_id:'res4'}), (rel5:Relato {relato_id:'rel5'}),
      (rep5:ReporteEstructurado {reporte_id:'rep5'}), (ses5:SesionDiagnostico {sesion_id:'ses5'}),
      (hip8:Hipotesis {hipotesis_id:'hip8'}), (hip9:Hipotesis {hipotesis_id:'hip9'}),
      (c_term:CausaRaiz {causa_id:'termica_bajada'}), (c_res:CausaRaiz {causa_id:'resistencia_quemada'}),
      (p6:PasoVerificacion {paso_id:'p6'}), (r5:RespuestaPaso {respuesta_id:'r5'}),
      (df5:DiagnosticoFinal {diagnostico_id:'df5'}), (inc5:Incidencia {incidencia_id:'inc5'}),
      (ctx5:ContextoIncidencia {contexto_id:'ctx5'}),
      (te01:Artefacto {artefacto_id:'te01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}),
      (s_ac:Servicio {servicio_id:'agua_caliente'}), (i4:Inmueble {inmueble_id:'inm104'})
CREATE (h4)-[:ESCRIBE]->(rel5),
       (rel5)-[:SE_ASOCIA_A]->(res4),
       (rep5)-[:IDENTIFICA]->(te01),
       (rep5)-[:CONTIENE]->(sin_ac),
       (rep5)-[:INICIA]->(ses5),
       (ses5)-[:GESTIONA]->(inc5),
       (ses5)-[:MANTIENE]->(hip8),
       (ses5)-[:MANTIENE]->(hip9),
       (hip8)-[:SE_REFIERE_A]->(c_term),
       (hip9)-[:SE_REFIERE_A]->(c_res),
       (h4)-[:EMITE]->(r5),
       (r5)-[:RESPONDE_A]->(p6),
       (r5)-[:ACTUALIZA {regla:'R11'}]->(hip8),
       (ses5)-[:PRODUCE]->(df5),
       (df5)-[:DIAGNOSTICA]->(c_res),
       (df5)-[:CLASIFICA]->(inc5),
       (inc5)-[:VINCULA]->(te01),
       (inc5)-[:AFECTA_A]->(i4),
       (inc5)-[:AFECTA_A]->(s_ac),
       (inc5)-[:TIENE_CONTEXTO]->(ctx5),
       (ctx5)-[:PROVIENE_DE]->(res4);

// ------------------------------------------------------------------------------
// 9. Caso 6: Emergencia de Seguridad Nítida (I1 -> R1 -> S1)
// ------------------------------------------------------------------------------

CREATE (rel6:Relato {relato_id:'rel6', texto:'huele mucho a gas en la cocina'});
CREATE (rep6:ReporteEstructurado {reporte_id:'rep6', senal_seguridad:true, estado:'emitido_alerta'});
CREATE (ses6:SesionDiagnostico {sesion_id:'ses6', estado:'abortada_seguridad', max_pasos:1, pasos_intentados:0});
CREATE (df6:DiagnosticoFinal {diagnostico_id:'df6', causa_diagnosticada:'fuga_de_gas_potencial', resoluble_por_huesped:false, riesgo_seguridad:true});
CREATE (inc6:Incidencia {incidencia_id:'inc6', estado:'escalada'});

MATCH (h5:Huesped {huesped_id:'h5'}), (res5:Reserva {reserva_id:'res5'}), (rel6:Relato {relato_id:'rel6'}),
      (la_gas:LexicoAlarma {termino:'gas'}), (rep6:ReporteEstructurado {reporte_id:'rep6'}),
      (ses6:SesionDiagnostico {sesion_id:'ses6'}), (df6:DiagnosticoFinal {diagnostico_id:'df6'}),
      (inc6:Incidencia {incidencia_id:'inc6'}), (tg03:Artefacto {artefacto_id:'tg03'}),
      (sin_gas:Sintoma {sintoma_id:'olor_a_gas'}), (s_ac:Servicio {servicio_id:'agua_caliente'}),
      (i5:Inmueble {inmueble_id:'inm105'})
CREATE (h5)-[:ESCRIBE]->(rel6),
       (rel6)-[:SE_ASOCIA_A]->(res5),
       (rel6)-[:COINCIDE_CON]->(la_gas),
       (rep6)-[:IDENTIFICA]->(tg03),
       (rep6)-[:CONTIENE]->(sin_gas),
       (rep6)-[:REGISTRA]->(sin_gas),
       (rep6)-[:INICIA]->(ses6),
       (ses6)-[:GESTIONA]->(inc6),
       (ses6)-[:PRODUCE]->(df6),
       (df6)-[:INDICA]->(sin_gas),
       (df6)-[:CLASIFICA]->(inc6),
       (inc6)-[:VINCULA]->(tg03),
       (inc6)-[:AFECTA_A]->(i5),
       (inc6)-[:AFECTA_A]->(s_ac);
