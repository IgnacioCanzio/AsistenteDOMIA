// ==============================================================================
// Grupo_3_PG2_U1.cypher - Carga Consolidada de Base de Conocimiento DOMIA
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/01_esquema_restricciones.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

CREATE CONSTRAINT anfitrion_id IF NOT EXISTS FOR (n:Anfitrion) REQUIRE n.anfitrion_id IS UNIQUE;
CREATE CONSTRAINT huesped_id IF NOT EXISTS FOR (n:Huesped) REQUIRE n.huesped_id IS UNIQUE;
CREATE CONSTRAINT inmueble_id IF NOT EXISTS FOR (n:Inmueble) REQUIRE n.inmueble_id IS UNIQUE;
CREATE CONSTRAINT reserva_id IF NOT EXISTS FOR (n:Reserva) REQUIRE n.reserva_id IS UNIQUE;
CREATE CONSTRAINT artefacto_id IF NOT EXISTS FOR (n:Artefacto) REQUIRE n.artefacto_id IS UNIQUE;
CREATE CONSTRAINT servicio_id IF NOT EXISTS FOR (n:Servicio) REQUIRE n.servicio_id IS UNIQUE;
CREATE CONSTRAINT sintoma_id IF NOT EXISTS FOR (n:Sintoma) REQUIRE n.sintoma_id IS UNIQUE;
CREATE CONSTRAINT causa_id IF NOT EXISTS FOR (n:CausaRaiz) REQUIRE n.causa_id IS UNIQUE;
CREATE CONSTRAINT paso_id IF NOT EXISTS FOR (n:PasoVerificacion) REQUIRE n.paso_id IS UNIQUE;
CREATE CONSTRAINT protocolo_id IF NOT EXISTS FOR (n:ProtocoloEmergencia) REQUIRE n.protocolo_id IS UNIQUE;
CREATE CONSTRAINT vocabulario_id IF NOT EXISTS FOR (n:VocabularioControlado) REQUIRE n.vocabulario_id IS UNIQUE;
CREATE CONSTRAINT expresion_id IF NOT EXISTS FOR (n:ExpresionLexica) REQUIRE n.expresion IS UNIQUE;
CREATE CONSTRAINT lexico_alarma_id IF NOT EXISTS FOR (n:LexicoAlarma) REQUIRE n.termino IS UNIQUE;
CREATE CONSTRAINT nivel_severidad_id IF NOT EXISTS FOR (n:NivelSeveridad) REQUIRE n.nivel IS UNIQUE;
CREATE CONSTRAINT relato_id IF NOT EXISTS FOR (n:Relato) REQUIRE n.relato_id IS UNIQUE;
CREATE CONSTRAINT candidato_id IF NOT EXISTS FOR (n:CandidatoExtraido) REQUIRE n.candidato_id IS UNIQUE;
CREATE CONSTRAINT evaluacion_id IF NOT EXISTS FOR (n:EvaluacionSuficiencia) REQUIRE n.evaluacion_id IS UNIQUE;
CREATE CONSTRAINT pregunta_id IF NOT EXISTS FOR (n:PreguntaAclaratoria) REQUIRE n.pregunta_id IS UNIQUE;
CREATE CONSTRAINT reporte_id IF NOT EXISTS FOR (n:ReporteEstructurado) REQUIRE n.reporte_id IS UNIQUE;
CREATE CONSTRAINT sesion_id IF NOT EXISTS FOR (n:SesionDiagnostico) REQUIRE n.sesion_id IS UNIQUE;
CREATE CONSTRAINT hipotesis_id IF NOT EXISTS FOR (n:Hipotesis) REQUIRE n.hipotesis_id IS UNIQUE;
CREATE CONSTRAINT respuesta_id IF NOT EXISTS FOR (n:RespuestaPaso) REQUIRE n.respuesta_id IS UNIQUE;
CREATE CONSTRAINT diagnostico_id IF NOT EXISTS FOR (n:DiagnosticoFinal) REQUIRE n.diagnostico_id IS UNIQUE;
CREATE CONSTRAINT incidencia_id IF NOT EXISTS FOR (n:Incidencia) REQUIRE n.incidencia_id IS UNIQUE;
CREATE CONSTRAINT contexto_id IF NOT EXISTS FOR (n:ContextoIncidencia) REQUIRE n.contexto_id IS UNIQUE;
CREATE CONSTRAINT variable_id IF NOT EXISTS FOR (n:VariableLinguistica) REQUIRE n.variable_id IS UNIQUE;
CREATE CONSTRAINT etiqueta_id IF NOT EXISTS FOR (n:EtiquetaDifusa) REQUIRE n.etiqueta_id IS UNIQUE;
CREATE CONSTRAINT regla_difusa_id IF NOT EXISTS FOR (n:ReglaDifusa) REQUIRE n.regla_id IS UNIQUE;
CREATE CONSTRAINT regla_crisp_id IF NOT EXISTS FOR (n:ReglaCrisp) REQUIRE n.regla_id IS UNIQUE;
CREATE CONSTRAINT caso_id IF NOT EXISTS FOR (n:CasoDifuso) REQUIRE n.caso_id IS UNIQUE;

CREATE INDEX regla_difusa_modulo IF NOT EXISTS FOR (n:ReglaDifusa) ON (n.modulo);
CREATE INDEX incidencia_estado IF NOT EXISTS FOR (n:Incidencia) ON (n.estado);

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/02_catalogo_conocimiento.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

CREATE (s_ac:Servicio {servicio_id:'agua_caliente', nombre:'Agua Caliente', tipo:'agua_caliente', esencial:false, sensibilidad_base:5.5});
CREATE (s_ap:Servicio:ServicioEsencial {servicio_id:'agua_potable', nombre:'Agua Potable', tipo:'agua_potable', esencial:true, sensibilidad_base:9.5});
CREATE (s_acc:Servicio:ServicioEsencial {servicio_id:'acceso_principal', nombre:'Acceso Principal', tipo:'acceso_principal', esencial:true, sensibilidad_base:9.5});
CREATE (s_cl:Servicio {servicio_id:'climatizacion', nombre:'Climatización', tipo:'climatizacion', esencial:false, sensibilidad_base:5.0});
CREATE (s_el:Servicio {servicio_id:'electricidad', nombre:'Suministro Eléctrico', tipo:'electricidad', esencial:false, sensibilidad_base:5.0});

CREATE (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente', nombre:'Sin agua caliente', descripcion:'No sale agua caliente en la ducha o canilla', requiere_seguridad:false});
CREATE (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta', nombre:'Teclado sin respuesta', descripcion:'El teclado numérico o lector de la cerradura no responde', requiere_seguridad:false});
CREATE (sin_enf:Sintoma {sintoma_id:'no_enfria', nombre:'No enfría', descripcion:'El equipo de aire acondicionado enciende pero no enfría', requiere_seguridad:false});
CREATE (sin_gas:Sintoma:SenalSeguridad {sintoma_id:'olor_a_gas', nombre:'Olor a gas', descripcion:'Olor a gas en el ambiente', requiere_seguridad:true});

CREATE (c_llave:CausaRaiz {causa_id:'llave_gas_cerrada', descripcion:'Llave de paso de gas cerrada', frecuencia:'frecuente', indice_frecuencia:0.75, resoluble_por_huesped:true, aplica_a:['TermotanqueGas']});
CREATE (c_pil:CausaRaiz {causa_id:'piloto_apagado', descripcion:'Piloto del termotanque apagado', frecuencia:'frecuente', indice_frecuencia:0.82, resoluble_por_huesped:true, aplica_a:['TermotanqueGas']});
CREATE (c_tc:CausaRaiz {causa_id:'falla_termocupla', descripcion:'Termocupla dañada o descalibrada', frecuencia:'rara', indice_frecuencia:0.15, resoluble_por_huesped:false, aplica_a:['TermotanqueGas']});
CREATE (c_term:CausaRaiz {causa_id:'termica_bajada', descripcion:'Interruptor termomagnético en posición OFF', frecuencia:'frecuente', indice_frecuencia:0.80, resoluble_por_huesped:true, aplica_a:['TermotanqueElectrico']});
CREATE (c_res:CausaRaiz {causa_id:'resistencia_quemada', descripcion:'Resistencia calefactora cortada o quemada', frecuencia:'rara', indice_frecuencia:0.10, resoluble_por_huesped:false, aplica_a:['TermotanqueElectrico']});
CREATE (c_pilas:CausaRaiz {causa_id:'pilas_agotadas', descripcion:'Pilas de la cerradura electrónica sin carga', frecuencia:'frecuente', indice_frecuencia:0.75, resoluble_por_huesped:true, aplica_a:['CerraduraElectronica']});
CREATE (c_trab:CausaRaiz {causa_id:'mecanismo_trabado', descripcion:'Perno o pestillo trabado mecánicamente', frecuencia:'rara', indice_frecuencia:0.12, resoluble_por_huesped:false, aplica_a:['CerraduraElectronica']});
CREATE (c_filtro:CausaRaiz {causa_id:'filtro_sucio', descripcion:'Filtros de aire obstruidos por polvo', frecuencia:'frecuente', indice_frecuencia:0.78, resoluble_por_huesped:true, aplica_a:['SplitAC']});
CREATE (c_gas:CausaRaiz {causa_id:'gas_refrigerante_bajo', descripcion:'Fuga o nivel bajo de gas refrigerante R410A', frecuencia:'poco_frecuente', indice_frecuencia:0.45, resoluble_por_huesped:false, aplica_a:['SplitAC']});

CREATE (p1:PasoVerificacion {paso_id:'p1', instruccion_huesped:'Verifique que la llave de gas esté abierta', riesgo_usuario:'bajo', riesgo_esfuerzo:1.2, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'abierta', advertencias:[]});
CREATE (p2:PasoVerificacion {paso_id:'p2', instruccion_huesped:'Gire la perilla a piloto y use el chispero', riesgo_usuario:'medio', riesgo_esfuerzo:4.2, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'encendido', advertencias:['Mantenga presionada la perilla 10 segundos tras encender']});
CREATE (p3:PasoVerificacion {paso_id:'p3', instruccion_huesped:'Pruebe el código maestro', riesgo_usuario:'bajo', riesgo_esfuerzo:1.5, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'abre', advertencias:[]});
CREATE (p5:PasoVerificacion:PasoNoDelegable {paso_id:'p5', instruccion_huesped:'Verifique la termocupla con tester multímetro', riesgo_usuario:'alto', riesgo_esfuerzo:8.5, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'voltaje_correcto', advertencias:['Paso reservado para técnico matriculado']});
CREATE (p6:PasoVerificacion {paso_id:'p6', instruccion_huesped:'Rearme la llave térmica', riesgo_usuario:'medio', riesgo_esfuerzo:4.0, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'energizado', advertencias:['Asegúrese de tener manos secas']});
CREATE (p7:PasoVerificacion:PasoNoDelegable {paso_id:'p7', instruccion_huesped:'Desmonte la tapa del termotanque y mida la resistencia', riesgo_usuario:'alto', riesgo_esfuerzo:9.0, requiere_herramientas:true, manipula_cableado:true, resultado_normal:'resistencia_correcta', advertencias:['Riesgo eléctrico: desconectar alimentación general']});
CREATE (p9:PasoVerificacion:PasoNoDelegable {paso_id:'p9', instruccion_huesped:'Desmonte el cilindro mecánico de la cerradura', riesgo_usuario:'alto', riesgo_esfuerzo:8.0, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'perno_libre', advertencias:['Requiere herramientas de cerrajería']});
CREATE (p10:PasoVerificacion {paso_id:'p10', instruccion_huesped:'Limpie los filtros de aire del split', riesgo_usuario:'bajo', riesgo_esfuerzo:2.0, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'filtro_limpio', advertencias:[]});
CREATE (p11:PasoVerificacion:PasoNoDelegable {paso_id:'p11', instruccion_huesped:'Mida la presión del circuito con manómetro frigorífico', riesgo_usuario:'alto', riesgo_esfuerzo:9.2, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'presion_nominal', advertencias:['Riesgo de quemadura por frío criogénico']});

MATCH (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}),
      (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta'}),
      (sin_enf:Sintoma {sintoma_id:'no_enfria'}),
      (c_llave:CausaRaiz {causa_id:'llave_gas_cerrada'}),
      (c_pil:CausaRaiz {causa_id:'piloto_apagado'}),
      (c_tc:CausaRaiz {causa_id:'falla_termocupla'}),
      (c_term:CausaRaiz {causa_id:'termica_bajada'}),
      (c_res:CausaRaiz {causa_id:'resistencia_quemada'}),
      (c_pilas:CausaRaiz {causa_id:'pilas_agotadas'}),
      (c_trab:CausaRaiz {causa_id:'mecanismo_trabado'}),
      (c_filtro:CausaRaiz {causa_id:'filtro_sucio'}),
      (c_gas:CausaRaiz {causa_id:'gas_refrigerante_bajo'})
CREATE (sin_ac)-[:ASOCIADO_A]->(c_llave),
       (sin_ac)-[:ASOCIADO_A]->(c_pil),
       (sin_ac)-[:ASOCIADO_A]->(c_tc),
       (sin_ac)-[:ASOCIADO_A]->(c_term),
       (sin_ac)-[:ASOCIADO_A]->(c_res),
       (sin_tec)-[:ASOCIADO_A]->(c_pilas),
       (sin_tec)-[:ASOCIADO_A]->(c_trab),
       (sin_enf)-[:ASOCIADO_A]->(c_filtro),
       (sin_enf)-[:ASOCIADO_A]->(c_gas);

MATCH (c_llave:CausaRaiz {causa_id:'llave_gas_cerrada'}),
      (c_pil:CausaRaiz {causa_id:'piloto_apagado'}),
      (c_tc:CausaRaiz {causa_id:'falla_termocupla'}),
      (c_term:CausaRaiz {causa_id:'termica_bajada'}),
      (c_res:CausaRaiz {causa_id:'resistencia_quemada'}),
      (c_pilas:CausaRaiz {causa_id:'pilas_agotadas'}),
      (c_trab:CausaRaiz {causa_id:'mecanismo_trabado'}),
      (c_filtro:CausaRaiz {causa_id:'filtro_sucio'}),
      (c_gas:CausaRaiz {causa_id:'gas_refrigerante_bajo'}),
      (p1:PasoVerificacion {paso_id:'p1'}),
      (p2:PasoVerificacion {paso_id:'p2'}),
      (p3:PasoVerificacion {paso_id:'p3'}),
      (p5:PasoVerificacion {paso_id:'p5'}),
      (p6:PasoVerificacion {paso_id:'p6'}),
      (p7:PasoVerificacion {paso_id:'p7'}),
      (p9:PasoVerificacion {paso_id:'p9'}),
      (p10:PasoVerificacion {paso_id:'p10'}),
      (p11:PasoVerificacion {paso_id:'p11'})
CREATE (c_llave)-[:SE_COMPRUEBA_CON]->(p1),
       (c_pil)-[:SE_COMPRUEBA_CON]->(p2),
       (c_tc)-[:SE_COMPRUEBA_CON]->(p5),
       (c_term)-[:SE_COMPRUEBA_CON]->(p6),
       (c_res)-[:SE_COMPRUEBA_CON]->(p7),
       (c_pilas)-[:SE_COMPRUEBA_CON]->(p3),
       (c_trab)-[:SE_COMPRUEBA_CON]->(p9),
       (c_filtro)-[:SE_COMPRUEBA_CON]->(p10),
       (c_gas)-[:SE_COMPRUEBA_CON]->(p11);

CREATE (pe1:ProtocoloEmergencia {protocolo_id:'pe1', nombre:'Protocolo Fuga de Gas', texto_fijo:'Cierre la llave general, ventile el ambiente y salga del inmueble. No use fuego ni interruptores.', nivel_fijo:5});

MATCH (sin_gas:Sintoma:SenalSeguridad {sintoma_id:'olor_a_gas'}), (pe1:ProtocoloEmergencia {protocolo_id:'pe1'})
CREATE (sin_gas)-[:DISPARA]->(pe1);

CREATE (vc1:VocabularioControlado {vocabulario_id:'vc1', nombre:'Vocabulario Estándar DOMIA'});

CREATE (exp1:ExpresionLexica {expresion:'no sale agua caliente', estado:'normalizado'});
CREATE (exp2:ExpresionLexica {expresion:'teclado no responde', estado:'normalizado'});
CREATE (exp3:ExpresionLexica {expresion:'aire no enfria', estado:'normalizado'});

CREATE (la_gas:LexicoAlarma {termino:'gas'});
CREATE (la_humo:LexicoAlarma {termino:'humo'});
CREATE (la_chispa:LexicoAlarma {termino:'chispa'});
CREATE (la_quemado:LexicoAlarma {termino:'quemado'});

MATCH (vc1:VocabularioControlado {vocabulario_id:'vc1'}),
      (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}),
      (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta'}),
      (sin_enf:Sintoma {sintoma_id:'no_enfria'}),
      (sin_gas:Sintoma {sintoma_id:'olor_a_gas'}),
      (exp1:ExpresionLexica {expresion:'no sale agua caliente'}),
      (exp2:ExpresionLexica {expresion:'teclado no responde'}),
      (exp3:ExpresionLexica {expresion:'aire no enfria'}),
      (la_gas:LexicoAlarma {termino:'gas'}),
      (la_humo:LexicoAlarma {termino:'humo'}),
      (la_chispa:LexicoAlarma {termino:'chispa'}),
      (la_quemado:LexicoAlarma {termino:'quemado'})
CREATE (vc1)-[:DEFINE]->(sin_ac),
       (vc1)-[:DEFINE]->(sin_tec),
       (vc1)-[:DEFINE]->(sin_enf),
       (vc1)-[:DEFINE]->(sin_gas),
       (vc1)-[:CONTIENE]->(exp1),
       (vc1)-[:CONTIENE]->(exp2),
       (vc1)-[:CONTIENE]->(exp3),
       (exp1)-[:SE_MAPEA_A]->(sin_ac),
       (exp2)-[:SE_MAPEA_A]->(sin_tec),
       (exp3)-[:SE_MAPEA_A]->(sin_enf),
       (vc1)-[:INCLUYE]->(la_gas),
       (vc1)-[:INCLUYE]->(la_humo),
       (vc1)-[:INCLUYE]->(la_chispa),
       (vc1)-[:INCLUYE]->(la_quemado),
       (la_gas)-[:IDENTIFICA]->(sin_gas),
       (la_humo)-[:IDENTIFICA]->(sin_gas),
       (la_chispa)-[:IDENTIFICA]->(sin_gas),
       (la_quemado)-[:IDENTIFICA]->(sin_gas);

CREATE (ns1:NivelSeveridad {nivel:1, puntaje_min:0, puntaje_max:20, prioridad:'Baja', canal:'reporte_diario', descripcion:'Incidencia leve sin impacto habitacional'});
CREATE (ns2:NivelSeveridad {nivel:2, puntaje_min:20, puntaje_max:40, prioridad:'Baja', canal:'reporte_diario', descripcion:'Incomodidad menor'});
CREATE (ns3:NivelSeveridad {nivel:3, puntaje_min:40, puntaje_max:60, prioridad:'Media', canal:'cola_priorizada', descripcion:'Falla funcional moderada'});
CREATE (ns4:NivelSeveridad {nivel:4, puntaje_min:60, puntaje_max:80, prioridad:'Alta', canal:'alerta_inmediata', descripcion:'Afectación severa o servicio esencial'});
CREATE (ns5:NivelSeveridad {nivel:5, puntaje_min:80, puntaje_max:100, prioridad:'Emergencia', canal:'alerta_inmediata', descripcion:'Peligro inminente a la seguridad o evacuación'});

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/03_reglas_nitidas.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

CREATE (:ReglaCrisp {regla_id:'I1', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Pre-filtro de seguridad léxico de alarma', expresion:'SI Relato coincide con LéxicoAlarma sin negación ENTONCES marcar señal_seguridad=true'});
CREATE (:ReglaCrisp {regla_id:'I2', modulo:'M1', tipo:'heuristica', cobertura:'documentada_pi4', descripcion:'Alarma negada', expresion:'SI término de alarma aparece explícitamente negado ENTONCES no marcar señal_seguridad'});
CREATE (:ReglaCrisp {regla_id:'I3', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Validación contra vocabulario controlado', expresion:'SI CandidatoExtraído no pertenece al VocabularioControlado ENTONCES descartar o pedir aclaración'});
CREATE (:ReglaCrisp {regla_id:'I4', modulo:'M1', tipo:'heuristica', cobertura:'reflejada_en_datos', descripcion:'Desambiguación de artefactos múltiples', expresion:'SI ExpresiónLéxica mapea a múltiples artefactos del inmueble ENTONCES generar PreguntaAclaratoria'});
CREATE (:ReglaCrisp {regla_id:'I5', modulo:'M1', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Suficiencia mínima para emisión de reporte', expresion:'SI exactamente 1 artefacto y al menos 1 síntoma válido identificado ENTONCES emitir ReporteEstructurado'});
CREATE (:ReglaCrisp {regla_id:'I6', modulo:'M1', tipo:'heuristica', cobertura:'reflejada_en_datos', descripcion:'Una sola pregunta aclaratoria por turno', expresion:'SI evaluación de suficiencia es insuficiente_con_rondas ENTONCES formular exactamente 1 pregunta cerrada'});
CREATE (:ReglaCrisp {regla_id:'I7', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Límite estricto de 2 rondas aclaratorias', expresion:'SI ronda >= 2 y persiste ambigüedad ENTONCES cerrar diálogo y escalar a anfitrión'});
CREATE (:ReglaCrisp {regla_id:'I8', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4', descripcion:'Mención de artefacto inexistente en inmueble', expresion:'SI artefacto mencionado no existe en Inmueble ENTONCES informar al huésped y no crear incidencia'});
CREATE (:ReglaCrisp {regla_id:'I9', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Normalización de respuestas del huésped', expresion:'SI respuesta huésped expresa confirmación o negativa ENTONCES mapear a sí/no/no_puedo/no_se'});
CREATE (:ReglaCrisp {regla_id:'I10', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4', descripcion:'Garantía de fidelidad del payload verbalizado', expresion:'SI mensaje verbalizado por LLM discrepa de hechos estructurados ENTONCES rechazar y usar fallback'});
CREATE (:ReglaCrisp {regla_id:'I11', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Protocolo de emergencia con plantilla fija inmutable', expresion:'SI señal_seguridad=true ENTONCES emitir ProtocoloEmergencia.texto_fijo sin intervención de LLM'});
CREATE (:ReglaCrisp {regla_id:'I12', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4', descripcion:'Verificación de reserva vigente', expresion:'SI Reserva no está vigente o huésped no registrado ENTONCES rechazar solicitud'});
CREATE (:ReglaCrisp {regla_id:'I13', modulo:'M1', tipo:'contextual', cobertura:'documentada_pi4', descripcion:'Detección de consultas fuera de dominio', expresion:'SI relato es ajeno a incidencias del inmueble ENTONCES responder cortésmente sin abrir diagnóstico'});
CREATE (:ReglaCrisp {regla_id:'I14', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4', descripcion:'Modo determinístico ante falla del LLM', expresion:'SI LLM falla por timeout o formato inválido ENTONCES aplicar extracción léxica determinística'});

CREATE (:ReglaCrisp {regla_id:'R1', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Seguridad crítica aborta sesión de diagnóstico', expresion:'SI señal_seguridad=true ENTONCES abortar diagnóstico de inmediato y derivar a protocolo de emergencia'});
CREATE (:ReglaCrisp {regla_id:'R1b', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Precaución ante olor extraño o persistente', expresion:'SI síntoma incluye olor a gas o quemado ENTONCES marcar riesgo_seguridad=true'});
CREATE (:ReglaCrisp {regla_id:'R2', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Límite de autonomía del huésped', expresion:'SI PasoVerificación requiere_herramientas o manipula_cableado ENTONCES etiquetar como PasoNoDelegable'});
CREATE (:ReglaCrisp {regla_id:'R3', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Resolución de falla operativa por el huésped', expresion:'SI respuesta al paso confirma resolución exitosa ENTONCES cerrar sesión como resuelta_por_huesped'});
CREATE (:ReglaCrisp {regla_id:'R4', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Bloqueo de cerradura electrónica', expresion:'SI cerradura no abre con código maestro ENTONCES diagnosticar bloqueo sin causa determinada y escalar'});
CREATE (:ReglaCrisp {regla_id:'R6', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Compatibilidad estructural entre causa y artefacto', expresion:'SI tipo de artefacto no está incluido en CausaRaiz.aplica_a ENTONCES descartar causa del árbol'});
CREATE (:ReglaCrisp {regla_id:'R7', modulo:'M2', tipo:'heuristica', cobertura:'consulta_ejecutable', descripcion:'Selección del próximo paso por riesgo y frecuencia', expresion:'SI existen múltiples pasos candidatos ENTONCES ordenar por menor riesgo_usuario y mayor frecuencia'});
CREATE (:ReglaCrisp {regla_id:'R8', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Límite de pasos intentados o negativas consecutivas', expresion:'SI pasos_intentados >= max_pasos o dos respuestas "no puedo" consecutivas ENTONCES escalar'});
CREATE (:ReglaCrisp {regla_id:'R9', modulo:'M2', tipo:'inferencial', cobertura:'documentada_pi4', descripcion:'Térmica con disparo reincidente', expresion:'SI la llave térmica vuelve a dispararse tras rearmado ENTONCES no reintentar y escalar por sospecha de cortocircuito'});
CREATE (:ReglaCrisp {regla_id:'R10', modulo:'M2', tipo:'heuristica', cobertura:'documentada_pi4', descripcion:'Detección de causa común por servicio compartido', expresion:'SI fallan dos artefactos dependientes del mismo servicio ENTONCES sospechar falla troncal'});
CREATE (:ReglaCrisp {regla_id:'R11', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos', descripcion:'Descarte de hipótesis por verificación normal', expresion:'SI resultado del paso confirma condición normal ENTONCES descartar la hipótesis asociada'});
CREATE (:ReglaCrisp {regla_id:'R12', modulo:'M2', tipo:'deterministica', cobertura:'documentada_pi4', descripcion:'Escalada cuando se agotan hipótesis resolubles', expresion:'SI no restan hipótesis con pasos delegables ENTONCES generar DiagnosticoFinal y escalar a M3'});

CREATE (:ReglaCrisp {regla_id:'R5', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Piso obligatorio de nivel 4 para servicios esenciales', expresion:'SI incidencia afecta ServicioEsencial (agua potable o acceso) ENTONCES nivel_final >= 4'});
CREATE (:ReglaCrisp {regla_id:'S1', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Riesgo de seguridad impone nivel 5 Emergencia', expresion:'SI DiagnosticoFinal.riesgo_seguridad=true ENTONCES asignar nivel 5 Emergencia sin lógica difusa'});
CREATE (:ReglaCrisp {regla_id:'S2', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Cierre silencioso de incidencias resueltas', expresion:'SI incidencia.estado=resuelta_por_huesped ENTONCES cerrar ficha sin notificación al anfitrión'});
CREATE (:ReglaCrisp {regla_id:'S3', modulo:'M3', tipo:'contextual', cobertura:'reflejada_en_datos', descripcion:'Contexto ausente adopta política conservadora', expresion:'SI temperatura o tiempo_restante no disponibles ENTONCES usar valores por defecto conservadores'});
CREATE (:ReglaCrisp {regla_id:'S4', modulo:'M3', tipo:'contextual', cobertura:'consulta_ejecutable', descripcion:'Múltiples incidencias simultáneas', expresion:'SI existen dos o más incidencias activas en el mismo inmueble ENTONCES elevar prioridad'});
CREATE (:ReglaCrisp {regla_id:'S5', modulo:'M3', tipo:'contextual', cobertura:'consulta_ejecutable', descripcion:'Sensibilidad contextual continua de climatización', expresion:'SI servicio es climatización ENTONCES sensibilidad = base + 4.5 * max(mu_Alto, mu_Extremo)'});
CREATE (:ReglaCrisp {regla_id:'T1', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Mapeo de puntaje difuso a nivel de severidad', expresion:'SI puntaje in [0,20)->1, [20,40)->2, [40,60)->3, [60,80)->4, [80,100]->5'});
CREATE (:ReglaCrisp {regla_id:'T2', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable', descripcion:'Canal de notificación y SLA por nivel', expresion:'SI nivel 1-2 -> reporte diario; nivel 3 -> cola priorizada; nivel 4-5 -> alerta inmediata push/SMS'});

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/04_logica_difusa.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

CREATE (:VariableLinguistica {variable_id:'ConfianzaExtraccion', nombre:'ConfianzaExtraccion', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'CoincidenciaLexica', nombre:'CoincidenciaLexica', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'DistanciaCandidatos', nombre:'DistanciaCandidatos', modulo:'M1', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'SuficienciaInterpretacion', nombre:'SuficienciaInterpretacion', modulo:'M1', rol:'salida', universo_min:0.0, universo_max:100.0});

CREATE (:VariableLinguistica {variable_id:'FrecuenciaCausa', nombre:'FrecuenciaCausa', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'RiesgoEsfuerzoPaso', nombre:'RiesgoEsfuerzoPaso', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:10.0});
CREATE (:VariableLinguistica {variable_id:'EvidenciaAcumulada', nombre:'EvidenciaAcumulada', modulo:'M2', rol:'entrada', universo_min:0.0, universo_max:1.0});
CREATE (:VariableLinguistica {variable_id:'PrioridadHipotesisPaso', nombre:'PrioridadHipotesisPaso', modulo:'M2', rol:'salida', universo_min:0.0, universo_max:100.0});

CREATE (:VariableLinguistica {variable_id:'ImpactoClimatico', nombre:'ImpactoClimatico', modulo:'M3', rol:'entrada', universo_min:-30.0, universo_max:55.0});
CREATE (:VariableLinguistica {variable_id:'TiempoRestante', nombre:'TiempoRestante', modulo:'M3', rol:'entrada', universo_min:0.0, universo_max:72.0});
CREATE (:VariableLinguistica {variable_id:'SensibilidadServicio', nombre:'SensibilidadServicio', modulo:'M3', rol:'entrada', universo_min:0.0, universo_max:10.0});
CREATE (:VariableLinguistica {variable_id:'CriticidadDifusa', nombre:'CriticidadDifusa', modulo:'M3', rol:'salida', universo_min:0.0, universo_max:100.0});

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

CREATE (:ReglaDifusa {regla_id:'IF1', modulo:'M1', activa:true, origen_pg1:'I5', consecuente:'SuficienciaInterpretacion.Suficiente', expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Fuerte Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Suficiente'});
CREATE (:ReglaDifusa {regla_id:'IF2', modulo:'M1', activa:true, origen_pg1:'I3', consecuente:'SuficienciaInterpretacion.Suficiente', expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Parcial Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Suficiente'});
CREATE (:ReglaDifusa {regla_id:'IF3', modulo:'M1', activa:true, origen_pg1:'I6', consecuente:'SuficienciaInterpretacion.Parcial', expresion:'SI (ConfianzaExtraccion ES Media O CoincidenciaLexica ES Parcial) Y DistanciaCandidatos ES Moderada ENTONCES SuficienciaInterpretacion ES Parcial'});
CREATE (:ReglaDifusa {regla_id:'IF4', modulo:'M1', activa:true, origen_pg1:'I4', consecuente:'SuficienciaInterpretacion.Parcial', expresion:'SI DistanciaCandidatos ES Pequena Y NO (ConfianzaExtraccion ES Baja) ENTONCES SuficienciaInterpretacion ES Parcial'});
CREATE (:ReglaDifusa {regla_id:'IF5', modulo:'M1', activa:true, origen_pg1:'I3', consecuente:'SuficienciaInterpretacion.Insuficiente', expresion:'SI ConfianzaExtraccion ES Baja O CoincidenciaLexica ES Debil ENTONCES SuficienciaInterpretacion ES Insuficiente'});
CREATE (:ReglaDifusa {regla_id:'IF6', modulo:'M1', activa:true, origen_pg1:'I4', consecuente:'SuficienciaInterpretacion.Parcial', expresion:'SI ConfianzaExtraccion ES Alta Y CoincidenciaLexica ES Fuerte Y DistanciaCandidatos ES Moderada ENTONCES SuficienciaInterpretacion ES Parcial'});
CREATE (:ReglaDifusa {regla_id:'IF7', modulo:'M1', activa:false, origen_pg1:'I6', consecuente:'SuficienciaInterpretacion.Parcial', expresion:'(cobertura) SI ConfianzaExtraccion ES Media Y DistanciaCandidatos ES Grande ENTONCES SuficienciaInterpretacion ES Parcial'});

MATCH (r:ReglaDifusa {regla_id:'IF1'}), (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}), (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Fuerte'}), (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Suficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF2'}), (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}), (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Parcial'}), (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Suficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF3'}), (a1:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Media'}), (a2:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Parcial'}), (b:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Moderada'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1), (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF4'}), (a:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Pequena'}), (b:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Baja'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF5'}), (a1:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Baja'}), (a2:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Debil'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Insuficiente'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1), (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF6'}), (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Alta'}), (b:EtiquetaDifusa {etiqueta_id:'CoincidenciaLexica.Fuerte'}), (c:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Moderada'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'IF7'}), (a:EtiquetaDifusa {etiqueta_id:'ConfianzaExtraccion.Media'}), (b:EtiquetaDifusa {etiqueta_id:'DistanciaCandidatos.Grande'}), (cons:EtiquetaDifusa {etiqueta_id:'SuficienciaInterpretacion.Parcial'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

CREATE (:ReglaDifusa {regla_id:'RF1', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Alta', expresion:'SI (FrecuenciaCausa ES Frecuente O EvidenciaAcumulada ES Fuerte) Y RiesgoEsfuerzoPaso ES Bajo ENTONCES PrioridadHipotesisPaso ES Alta'});
CREATE (:ReglaDifusa {regla_id:'RF2', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Alta', expresion:'SI FrecuenciaCausa ES Frecuente Y EvidenciaAcumulada ES Fuerte Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Alta'});
CREATE (:ReglaDifusa {regla_id:'RF3', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media', expresion:'SI FrecuenciaCausa ES PocoFrecuente Y EvidenciaAcumulada ES Moderada Y NO (RiesgoEsfuerzoPaso ES Alto) ENTONCES PrioridadHipotesisPaso ES Media'});
CREATE (:ReglaDifusa {regla_id:'RF4', modulo:'M2', activa:true, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media', expresion:'SI FrecuenciaCausa ES Frecuente Y EvidenciaAcumulada ES Moderada Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Media'});
CREATE (:ReglaDifusa {regla_id:'RF5', modulo:'M2', activa:true, origen_pg1:'R8', consecuente:'PrioridadHipotesisPaso.Baja', expresion:'SI RiesgoEsfuerzoPaso ES Alto O EvidenciaAcumulada ES Debil ENTONCES PrioridadHipotesisPaso ES Baja'});
CREATE (:ReglaDifusa {regla_id:'RF6', modulo:'M2', activa:true, origen_pg1:'R12', consecuente:'PrioridadHipotesisPaso.Baja', expresion:'SI FrecuenciaCausa ES Rara Y NO (EvidenciaAcumulada ES Fuerte) ENTONCES PrioridadHipotesisPaso ES Baja'});
CREATE (:ReglaDifusa {regla_id:'RF7', modulo:'M2', activa:false, origen_pg1:'R7', consecuente:'PrioridadHipotesisPaso.Media', expresion:'(cobertura) SI EvidenciaAcumulada ES Fuerte Y RiesgoEsfuerzoPaso ES Medio ENTONCES PrioridadHipotesisPaso ES Media'});

MATCH (r:ReglaDifusa {regla_id:'RF1'}), (a1:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}), (a2:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}), (b:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Bajo'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1), (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF2'}), (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}), (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}), (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF3'}), (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.PocoFrecuente'}), (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Moderada'}), (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Alto'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:true}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF4'}), (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Frecuente'}), (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Moderada'}), (c:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:false}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF5'}), (a1:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Alto'}), (a2:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Debil'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a1), (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a2), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF6'}), (a:EtiquetaDifusa {etiqueta_id:'FrecuenciaCausa.Rara'}), (b:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'RF7'}), (a:EtiquetaDifusa {etiqueta_id:'EvidenciaAcumulada.Fuerte'}), (b:EtiquetaDifusa {etiqueta_id:'RiesgoEsfuerzoPaso.Medio'}), (cons:EtiquetaDifusa {etiqueta_id:'PrioridadHipotesisPaso.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

CREATE (:ReglaDifusa {regla_id:'F1', modulo:'M3', activa:true, origen_pg1:'F1', consecuente:'CriticidadDifusa.Emergencia', expresion:'SI SensibilidadServicio ES Critico Y ImpactoClimatico ES Extremo ENTONCES CriticidadDifusa ES Emergencia'});
CREATE (:ReglaDifusa {regla_id:'F2', modulo:'M3', activa:true, origen_pg1:'F2', consecuente:'CriticidadDifusa.Alta', expresion:'SI SensibilidadServicio ES Critico Y ImpactoClimatico ES Alto ENTONCES CriticidadDifusa ES Alta'});
CREATE (:ReglaDifusa {regla_id:'F3', modulo:'M3', activa:true, origen_pg1:'F3', consecuente:'CriticidadDifusa.Alta', expresion:'SI SensibilidadServicio ES Molesto Y ImpactoClimatico ES Alto Y NO (TiempoRestante ES Inminente) ENTONCES CriticidadDifusa ES Alta'});
CREATE (:ReglaDifusa {regla_id:'F4a', modulo:'M3', activa:true, origen_pg1:'F4', consecuente:'CriticidadDifusa.Baja', expresion:'SI SensibilidadServicio ES Tolerable ENTONCES CriticidadDifusa ES Baja'});
CREATE (:ReglaDifusa {regla_id:'F4b', modulo:'M3', activa:true, origen_pg1:'F4', consecuente:'CriticidadDifusa.Baja', expresion:'SI ImpactoClimatico ES Bajo Y NO (SensibilidadServicio ES Critico) ENTONCES CriticidadDifusa ES Baja'});
CREATE (:ReglaDifusa {regla_id:'F5', modulo:'M3', activa:true, origen_pg1:'F5', consecuente:'CriticidadDifusa.Media', expresion:'SI TiempoRestante ES Inminente Y NO (SensibilidadServicio ES Critico) ENTONCES CriticidadDifusa ES Media'});
CREATE (:ReglaDifusa {regla_id:'F6', modulo:'M3', activa:true, origen_pg1:'F6', consecuente:'CriticidadDifusa.Alta', expresion:'SI TiempoRestante ES Prolongado Y SensibilidadServicio ES Critico ENTONCES CriticidadDifusa ES Alta'});
CREATE (:ReglaDifusa {regla_id:'F7', modulo:'M3', activa:false, origen_pg1:'F6', consecuente:'CriticidadDifusa.Alta', expresion:'(cobertura) SI SensibilidadServicio ES Critico ENTONCES CriticidadDifusa ES Alta'});

MATCH (r:ReglaDifusa {regla_id:'F1'}), (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Extremo'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Emergencia'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F2'}), (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Alto'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F3'}), (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Molesto'}), (b:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Alto'}), (c:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Inminente'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:EVALUA_ANTECEDENTE {grupo:2, negada:true}]->(c), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F4a'}), (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Tolerable'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F4b'}), (a:EtiquetaDifusa {etiqueta_id:'ImpactoClimatico.Bajo'}), (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Baja'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F5'}), (a:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Inminente'}), (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Media'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:true}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F6'}), (a:EtiquetaDifusa {etiqueta_id:'TiempoRestante.Prolongado'}), (b:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:EVALUA_ANTECEDENTE {grupo:1, negada:false}]->(b), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

MATCH (r:ReglaDifusa {regla_id:'F7'}), (a:EtiquetaDifusa {etiqueta_id:'SensibilidadServicio.Critico'}), (cons:EtiquetaDifusa {etiqueta_id:'CriticidadDifusa.Alta'})
CREATE (r)-[:EVALUA_ANTECEDENTE {grupo:0, negada:false}]->(a), (r)-[:IMPLICA_CONSECUENTE {metodo:'Mamdani-recorte'}]->(cons);

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


// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/05_instancias_casos.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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

CREATE (tg01:Artefacto:TermotanqueGas {artefacto_id:'tg01', tipo:'TermotanqueGas', marca:'Eskabe', modelo:'Aquapiú 80L', ubicacion:'Lavadero', tiene_piloto:true});
CREATE (cer01:Artefacto:CerraduraElectronica {artefacto_id:'cer01', tipo:'CerraduraElectronica', marca:'Samsung', modelo:'SHP-DH538', ubicacion:'Puerta Principal'});
CREATE (spl01:Artefacto:SplitAC {artefacto_id:'spl01', tipo:'SplitAC', marca:'BGH', modelo:'Silent Air 3000', ubicacion:'Estar Comedor'});
CREATE (te01:Artefacto:TermotanqueElectrico {artefacto_id:'te01', tipo:'TermotanqueElectrico', marca:'Philco', modelo:'TE-50L', ubicacion:'Baño Principal'});
CREATE (tg02:Artefacto:TermotanqueGas {artefacto_id:'tg02', tipo:'TermotanqueGas', marca:'Rheem', modelo:'TG-120', ubicacion:'Cocina', tiene_piloto:true});
CREATE (tg03:Artefacto:TermotanqueGas {artefacto_id:'tg03', tipo:'TermotanqueGas', marca:'Orbis', modelo:'Eurotrend', ubicacion:'Cocina', tiene_piloto:true});

MATCH (i1:Inmueble {inmueble_id:'inm101'}), (tg01:Artefacto {artefacto_id:'tg01'}) CREATE (i1)-[:CONTIENE]->(tg01);
MATCH (i2:Inmueble {inmueble_id:'inm102'}), (cer01:Artefacto {artefacto_id:'cer01'}) CREATE (i2)-[:CONTIENE]->(cer01);
MATCH (i3:Inmueble {inmueble_id:'inm103'}), (spl01:Artefacto {artefacto_id:'spl01'}) CREATE (i3)-[:CONTIENE]->(spl01);
MATCH (i4:Inmueble {inmueble_id:'inm104'}), (te01:Artefacto {artefacto_id:'te01'}), (tg02:Artefacto {artefacto_id:'tg02'})
CREATE (i4)-[:CONTIENE]->(te01), (i4)-[:CONTIENE]->(tg02);
MATCH (i5:Inmueble {inmueble_id:'inm105'}), (tg03:Artefacto {artefacto_id:'tg03'}) CREATE (i5)-[:CONTIENE]->(tg03);

MATCH (tg01:Artefacto {artefacto_id:'tg01'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg01)-[:DEPENDE_DE]->(s_ac);
MATCH (cer01:Artefacto {artefacto_id:'cer01'}), (s_acc:Servicio {servicio_id:'acceso_principal'}) CREATE (cer01)-[:DEPENDE_DE]->(s_acc);
MATCH (spl01:Artefacto {artefacto_id:'spl01'}), (s_cl:Servicio {servicio_id:'climatizacion'}) CREATE (spl01)-[:DEPENDE_DE]->(s_cl);
MATCH (te01:Artefacto {artefacto_id:'te01'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (te01)-[:DEPENDE_DE]->(s_ac);
MATCH (tg02:Artefacto {artefacto_id:'tg02'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg02)-[:DEPENDE_DE]->(s_ac);
MATCH (tg03:Artefacto {artefacto_id:'tg03'}), (s_ac:Servicio {servicio_id:'agua_caliente'}) CREATE (tg03)-[:DEPENDE_DE]->(s_ac);

MATCH (tg01:Artefacto {artefacto_id:'tg01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (tg01)-[:MANIFIESTA]->(sin_ac);
MATCH (cer01:Artefacto {artefacto_id:'cer01'}), (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta'}) CREATE (cer01)-[:MANIFIESTA]->(sin_tec);
MATCH (spl01:Artefacto {artefacto_id:'spl01'}), (sin_enf:Sintoma {sintoma_id:'no_enfria'}) CREATE (spl01)-[:MANIFIESTA]->(sin_enf);
MATCH (te01:Artefacto {artefacto_id:'te01'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (te01)-[:MANIFIESTA]->(sin_ac);
MATCH (tg02:Artefacto {artefacto_id:'tg02'}), (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente'}) CREATE (tg02)-[:MANIFIESTA]->(sin_ac);
MATCH (tg03:Artefacto {artefacto_id:'tg03'}), (sin_gas:Sintoma {sintoma_id:'olor_a_gas'}) CREATE (tg03)-[:MANIFIESTA]->(sin_gas);

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

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
// SECCIÓN: pg2_neo4j/scripts/06_casos_difusos.cypher
// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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
