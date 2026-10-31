// ==============================================================================
// Script 02: Catálogo de Conocimiento
// Servicios, Síntomas, Causas Raíz, Pasos de Verificación, Protocolos,
// Vocabulario y Niveles de Severidad
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Servicios (5 nodos: 2 con subetiqueta :ServicioEsencial)
// ------------------------------------------------------------------------------

CREATE (s_ac:Servicio {servicio_id:'agua_caliente', nombre:'Agua Caliente', tipo:'agua_caliente', esencial:false, sensibilidad_base:5.5});
CREATE (s_ap:Servicio:ServicioEsencial {servicio_id:'agua_potable', nombre:'Agua Potable', tipo:'agua_potable', esencial:true, sensibilidad_base:9.5});
CREATE (s_acc:Servicio:ServicioEsencial {servicio_id:'acceso_principal', nombre:'Acceso Principal', tipo:'acceso_principal', esencial:true, sensibilidad_base:9.5});
CREATE (s_cl:Servicio {servicio_id:'climatizacion', nombre:'Climatización', tipo:'climatizacion', esencial:false, sensibilidad_base:5.0});
CREATE (s_el:Servicio {servicio_id:'electricidad', nombre:'Suministro Eléctrico', tipo:'electricidad', esencial:false, sensibilidad_base:5.0});

// ------------------------------------------------------------------------------
// 2. Síntomas (4 nodos: 1 con subetiqueta :SenalSeguridad)
// ------------------------------------------------------------------------------

CREATE (sin_ac:Sintoma {sintoma_id:'sin_agua_caliente', nombre:'Sin agua caliente', descripcion:'No sale agua caliente en la ducha o canilla', requiere_seguridad:false});
CREATE (sin_tec:Sintoma {sintoma_id:'teclado_sin_respuesta', nombre:'Teclado sin respuesta', descripcion:'El teclado numérico o lector de la cerradura no responde', requiere_seguridad:false});
CREATE (sin_enf:Sintoma {sintoma_id:'no_enfria', nombre:'No enfría', descripcion:'El equipo de aire acondicionado enciende pero no enfría', requiere_seguridad:false});
CREATE (sin_gas:Sintoma:SenalSeguridad {sintoma_id:'olor_a_gas', nombre:'Olor a gas', descripcion:'Olor a gas en el ambiente', requiere_seguridad:true});

// ------------------------------------------------------------------------------
// 3. Causas Raíz (9 nodos con propiedad aplica_a para R6)
// ------------------------------------------------------------------------------

CREATE (c_llave:CausaRaiz {causa_id:'llave_gas_cerrada', descripcion:'Llave de paso de gas cerrada', frecuencia:'frecuente', indice_frecuencia:0.75, resoluble_por_huesped:true, aplica_a:['TermotanqueGas']});
CREATE (c_pil:CausaRaiz {causa_id:'piloto_apagado', descripcion:'Piloto del termotanque apagado', frecuencia:'frecuente', indice_frecuencia:0.82, resoluble_por_huesped:true, aplica_a:['TermotanqueGas']});
CREATE (c_tc:CausaRaiz {causa_id:'falla_termocupla', descripcion:'Termocupla dañada o descalibrada', frecuencia:'rara', indice_frecuencia:0.15, resoluble_por_huesped:false, aplica_a:['TermotanqueGas']});
CREATE (c_term:CausaRaiz {causa_id:'termica_bajada', descripcion:'Interruptor termomagnético en posición OFF', frecuencia:'frecuente', indice_frecuencia:0.80, resoluble_por_huesped:true, aplica_a:['TermotanqueElectrico']});
CREATE (c_res:CausaRaiz {causa_id:'resistencia_quemada', descripcion:'Resistencia calefactora cortada o quemada', frecuencia:'rara', indice_frecuencia:0.10, resoluble_por_huesped:false, aplica_a:['TermotanqueElectrico']});
CREATE (c_pilas:CausaRaiz {causa_id:'pilas_agotadas', descripcion:'Pilas de la cerradura electrónica sin carga', frecuencia:'frecuente', indice_frecuencia:0.75, resoluble_por_huesped:true, aplica_a:['CerraduraElectronica']});
CREATE (c_trab:CausaRaiz {causa_id:'mecanismo_trabado', descripcion:'Perno o pestillo trabado mecánicamente', frecuencia:'rara', indice_frecuencia:0.12, resoluble_por_huesped:false, aplica_a:['CerraduraElectronica']});
CREATE (c_filtro:CausaRaiz {causa_id:'filtro_sucio', descripcion:'Filtros de aire obstruidos por polvo', frecuencia:'frecuente', indice_frecuencia:0.78, resoluble_por_huesped:true, aplica_a:['SplitAC']});
CREATE (c_gas:CausaRaiz {causa_id:'gas_refrigerante_bajo', descripcion:'Fuga o nivel bajo de gas refrigerante R410A', frecuencia:'poco_frecuente', indice_frecuencia:0.45, resoluble_por_huesped:false, aplica_a:['SplitAC']});

// ------------------------------------------------------------------------------
// 4. Pasos de Verificación (9 nodos: 4 con subetiqueta :PasoNoDelegable según R2)
// ------------------------------------------------------------------------------

CREATE (p1:PasoVerificacion {paso_id:'p1', instruccion_huesped:'Verifique que la llave de gas esté abierta', riesgo_usuario:'bajo', riesgo_esfuerzo:1.2, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'abierta', advertencias:[]});
CREATE (p2:PasoVerificacion {paso_id:'p2', instruccion_huesped:'Gire la perilla a piloto y use el chispero', riesgo_usuario:'medio', riesgo_esfuerzo:4.2, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'encendido', advertencias:['Mantenga presionada la perilla 10 segundos tras encender']});
CREATE (p3:PasoVerificacion {paso_id:'p3', instruccion_huesped:'Pruebe el código maestro', riesgo_usuario:'bajo', riesgo_esfuerzo:1.5, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'abre', advertencias:[]});
CREATE (p5:PasoVerificacion:PasoNoDelegable {paso_id:'p5', instruccion_huesped:'Verifique la termocupla con tester multímetro', riesgo_usuario:'alto', riesgo_esfuerzo:8.5, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'voltaje_correcto', advertencias:['Paso reservado para técnico matriculado']});
CREATE (p6:PasoVerificacion {paso_id:'p6', instruccion_huesped:'Rearme la llave térmica', riesgo_usuario:'medio', riesgo_esfuerzo:4.0, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'energizado', advertencias:['Asegúrese de tener manos secas']});
CREATE (p7:PasoVerificacion:PasoNoDelegable {paso_id:'p7', instruccion_huesped:'Desmonte la tapa del termotanque y mida la resistencia', riesgo_usuario:'alto', riesgo_esfuerzo:9.0, requiere_herramientas:true, manipula_cableado:true, resultado_normal:'resistencia_correcta', advertencias:['Riesgo eléctrico: desconectar alimentación general']});
CREATE (p9:PasoVerificacion:PasoNoDelegable {paso_id:'p9', instruccion_huesped:'Desmonte el cilindro mecánico de la cerradura', riesgo_usuario:'alto', riesgo_esfuerzo:8.0, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'perno_libre', advertencias:['Requiere herramientas de cerrajería']});
CREATE (p10:PasoVerificacion {paso_id:'p10', instruccion_huesped:'Limpie los filtros de aire del split', riesgo_usuario:'bajo', riesgo_esfuerzo:2.0, requiere_herramientas:false, manipula_cableado:false, resultado_normal:'filtro_limpio', advertencias:[]});
CREATE (p11:PasoVerificacion:PasoNoDelegable {paso_id:'p11', instruccion_huesped:'Mida la presión del circuito con manómetro frigorífico', riesgo_usuario:'alto', riesgo_esfuerzo:9.2, requiere_herramientas:true, manipula_cableado:false, resultado_normal:'presion_nominal', advertencias:['Riesgo de quemadura por frío criogénico']});

// ------------------------------------------------------------------------------
// 5. Relaciones Síntoma -> CausaRaiz (9 relaciones ASOCIADO_A)
// ------------------------------------------------------------------------------

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

// ------------------------------------------------------------------------------
// 6. Relaciones CausaRaiz -> PasoVerificacion (9 relaciones SE_COMPRUEBA_CON)
// ------------------------------------------------------------------------------

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

// ------------------------------------------------------------------------------
// 7. Protocolo de Emergencia y Señal de Seguridad (1 Protocolo, 1 DISPARA)
// ------------------------------------------------------------------------------

CREATE (pe1:ProtocoloEmergencia {protocolo_id:'pe1', nombre:'Protocolo Fuga de Gas', texto_fijo:'Cierre la llave general, ventile el ambiente y salga del inmueble. No use fuego ni interruptores.', nivel_fijo:5});

MATCH (sin_gas:Sintoma:SenalSeguridad {sintoma_id:'olor_a_gas'}), (pe1:ProtocoloEmergencia {protocolo_id:'pe1'})
CREATE (sin_gas)-[:DISPARA]->(pe1);

// ------------------------------------------------------------------------------
// 8. Vocabulario Controlado, Expresiones Léxicas y Léxico de Alarma
// ------------------------------------------------------------------------------

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

// ------------------------------------------------------------------------------
// 9. Niveles de Severidad (5 nodos T1 y T2)
// ------------------------------------------------------------------------------

CREATE (ns1:NivelSeveridad {nivel:1, puntaje_min:0, puntaje_max:20, prioridad:'Baja', canal:'reporte_diario', descripcion:'Incidencia leve sin impacto habitacional'});
CREATE (ns2:NivelSeveridad {nivel:2, puntaje_min:20, puntaje_max:40, prioridad:'Baja', canal:'reporte_diario', descripcion:'Incomodidad menor'});
CREATE (ns3:NivelSeveridad {nivel:3, puntaje_min:40, puntaje_max:60, prioridad:'Media', canal:'cola_priorizada', descripcion:'Falla funcional moderada'});
CREATE (ns4:NivelSeveridad {nivel:4, puntaje_min:60, puntaje_max:80, prioridad:'Alta', canal:'alerta_inmediata', descripcion:'Afectación severa o servicio esencial'});
CREATE (ns5:NivelSeveridad {nivel:5, puntaje_min:80, puntaje_max:100, prioridad:'Emergencia', canal:'alerta_inmediata', descripcion:'Peligro inminente a la seguridad o evacuación'});
