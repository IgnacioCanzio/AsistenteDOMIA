// ==============================================================================
// Script 03: Catálogo de Reglas Nítidas (34 nodos :ReglaCrisp)
// Proyecto: DOMIA - Asistente Experto de Conserjería para Alquileres Temporarios
// Grupo 3 · Comisión 5k9 · UTN FRM · 2026
// ==============================================================================

// ------------------------------------------------------------------------------
// Submódulo M1: Interpretación, Diálogo y Explicación (14 reglas)
// ------------------------------------------------------------------------------

CREATE (:ReglaCrisp {regla_id:'I1', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Pre-filtro de seguridad léxico de alarma (gas, humo, chispa, quemado sin negación)',
  expresion:'SI Relato coincide con LéxicoAlarma sin negación ENTONCES marcar señal_seguridad=true'});

CREATE (:ReglaCrisp {regla_id:'I2', modulo:'M1', tipo:'heuristica', cobertura:'documentada_pi4',
  descripcion:'Alarma negada (ej: no huele a gas)',
  expresion:'SI término de alarma aparece explícitamente negado ENTONCES no marcar señal_seguridad'});

CREATE (:ReglaCrisp {regla_id:'I3', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Validación contra vocabulario controlado',
  expresion:'SI CandidatoExtraído no pertenece al VocabularioControlado ENTONCES descartar o pedir aclaración'});

CREATE (:ReglaCrisp {regla_id:'I4', modulo:'M1', tipo:'heuristica', cobertura:'reflejada_en_datos',
  descripcion:'Desambiguación de artefactos múltiples',
  expresion:'SI ExpresiónLéxica mapea a múltiples artefactos del inmueble ENTONCES generar PreguntaAclaratoria'});

CREATE (:ReglaCrisp {regla_id:'I5', modulo:'M1', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Suficiencia mínima para emisión de reporte',
  expresion:'SI exactamente 1 artefacto y al menos 1 síntoma válido identificado ENTONCES emitir ReporteEstructurado'});

CREATE (:ReglaCrisp {regla_id:'I6', modulo:'M1', tipo:'heuristica', cobertura:'reflejada_en_datos',
  descripcion:'Una sola pregunta aclaratoria por turno',
  expresion:'SI evaluación de suficiencia es insuficiente_con_rondas ENTONCES formular exactamente 1 pregunta cerrada'});

CREATE (:ReglaCrisp {regla_id:'I7', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Límite estricto de 2 rondas aclaratorias',
  expresion:'SI ronda >= 2 y persiste ambigüedad ENTONCES cerrar diálogo y escalar a anfitrión'});

CREATE (:ReglaCrisp {regla_id:'I8', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4',
  descripcion:'Mención de artefacto inexistente en inmueble',
  expresion:'SI artefacto mencionado no existe en Inmueble ENTONCES informar al huésped y no crear incidencia'});

CREATE (:ReglaCrisp {regla_id:'I9', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Normalización de respuestas del huésped',
  expresion:'SI respuesta huésped expresa confirmación o negativa ENTONCES mapear a sí/no/no_puedo/no_se'});

CREATE (:ReglaCrisp {regla_id:'I10', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4',
  descripcion:'Garantía de fidelidad del payload verbalizado',
  expresion:'SI mensaje verbalizado por LLM discrepa de hechos estructurados ENTONCES rechazar y usar fallback'});

CREATE (:ReglaCrisp {regla_id:'I11', modulo:'M1', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Protocolo de emergencia con plantilla fija inmutable',
  expresion:'SI señal_seguridad=true ENTONCES emitir ProtocoloEmergencia.texto_fijo sin intervención de LLM'});

CREATE (:ReglaCrisp {regla_id:'I12', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4',
  descripcion:'Verificación de reserva vigente',
  expresion:'SI Reserva no está vigente o huésped no registrado ENTONCES rechazar solicitud'});

CREATE (:ReglaCrisp {regla_id:'I13', modulo:'M1', tipo:'contextual', cobertura:'documentada_pi4',
  descripcion:'Detección de consultas fuera de dominio',
  expresion:'SI relato es ajeno a incidencias del inmueble ENTONCES responder cortésmente sin abrir diagnóstico'});

CREATE (:ReglaCrisp {regla_id:'I14', modulo:'M1', tipo:'deterministica', cobertura:'documentada_pi4',
  descripcion:'Modo determinístico ante falla del LLM',
  expresion:'SI LLM falla por timeout o formato inválido ENTONCES aplicar extracción léxica determinística'});

// ------------------------------------------------------------------------------
// Submódulo M2: Motor de Diagnóstico y Troubleshooting (12 reglas)
// ------------------------------------------------------------------------------

CREATE (:ReglaCrisp {regla_id:'R1', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Seguridad crítica aborta sesión de diagnóstico',
  expresion:'SI señal_seguridad=true ENTONCES abortar diagnóstico de inmediato y derivar a protocolo de emergencia'});

CREATE (:ReglaCrisp {regla_id:'R1b', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Precaución ante olor extraño o persistente',
  expresion:'SI síntoma incluye olor a gas o quemado ENTONCES marcar riesgo_seguridad=true'});

CREATE (:ReglaCrisp {regla_id:'R2', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Límite de autonomía del huésped (no delegabilidad)',
  expresion:'SI PasoVerificación requiere_herramientas o manipula_cableado ENTONCES etiquetar como PasoNoDelegable y no emitir a huésped'});

CREATE (:ReglaCrisp {regla_id:'R3', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Resolución de falla operativa por el huésped',
  expresion:'SI respuesta al paso confirma resolución exitosa ENTONCES cerrar sesión como resuelta_por_huesped'});

CREATE (:ReglaCrisp {regla_id:'R4', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Bloqueo de cerradura electrónica',
  expresion:'SI cerradura no abre con código maestro ENTONCES diagnosticar bloqueo sin causa determinada y escalar'});

CREATE (:ReglaCrisp {regla_id:'R6', modulo:'M2', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Compatibilidad estructural entre causa y artefacto',
  expresion:'SI tipo de artefacto no está incluido en CausaRaiz.aplica_a ENTONCES descartar causa del árbol'});

CREATE (:ReglaCrisp {regla_id:'R7', modulo:'M2', tipo:'heuristica', cobertura:'consulta_ejecutable',
  descripcion:'Selección del próximo paso por riesgo y frecuencia',
  expresion:'SI existen múltiples pasos candidatos ENTONCES ordenar por menor riesgo_usuario y mayor frecuencia'});

CREATE (:ReglaCrisp {regla_id:'R8', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Límite de pasos intentados o respuestas negativas consecutivas',
  expresion:'SI pasos_intentados >= max_pasos o dos respuestas "no puedo" consecutivas ENTONCES escalar'});

CREATE (:ReglaCrisp {regla_id:'R9', modulo:'M2', tipo:'inferencial', cobertura:'documentada_pi4',
  descripcion:'Térmica con disparo reincidente',
  expresion:'SI la llave térmica vuelve a dispararse tras rearmado ENTONCES no reintentar y escalar por sospecha de cortocircuito'});

CREATE (:ReglaCrisp {regla_id:'R10', modulo:'M2', tipo:'heuristica', cobertura:'documentada_pi4',
  descripcion:'Detección de causa común por servicio compartido',
  expresion:'SI fallan dos artefactos dependientes del mismo servicio ENTONCES sospechar falla troncal de suministro'});

CREATE (:ReglaCrisp {regla_id:'R11', modulo:'M2', tipo:'deterministica', cobertura:'reflejada_en_datos',
  descripcion:'Descarte de hipótesis por verificación normal',
  expresion:'SI resultado del paso confirma condición normal ENTONCES descartar la hipótesis asociada y actualizar evidencia'});

CREATE (:ReglaCrisp {regla_id:'R12', modulo:'M2', tipo:'deterministica', cobertura:'documentada_pi4',
  descripcion:'Escalada cuando se agotan hipótesis resolubles',
  expresion:'SI no restan hipótesis con pasos delegables ENTONCES generar DiagnosticoFinal y escalar a M3'});

// ------------------------------------------------------------------------------
// Submódulo M3: Evaluación Difusa e Incidencias (8 reglas)
// ------------------------------------------------------------------------------

CREATE (:ReglaCrisp {regla_id:'R5', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Piso obligatorio de nivel 4 para servicios esenciales',
  expresion:'SI incidencia afecta ServicioEsencial (agua potable o acceso) ENTONCES nivel_final >= 4 (Alta)'});

CREATE (:ReglaCrisp {regla_id:'S1', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Riesgo de seguridad impone nivel 5 Emergencia sin lógica difusa',
  expresion:'SI DiagnosticoFinal.riesgo_seguridad=true ENTONCES asignar nivel 5 Emergencia de forma determinística'});

CREATE (:ReglaCrisp {regla_id:'S2', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Cierre silencioso de incidencias resueltas por el huésped',
  expresion:'SI incidencia.estado=resuelta_por_huesped ENTONCES cerrar ficha sin notificación al anfitrión'});

CREATE (:ReglaCrisp {regla_id:'S3', modulo:'M3', tipo:'contextual', cobertura:'reflejada_en_datos',
  descripcion:'Contexto ausente adopta política conservadora de peor caso',
  expresion:'SI temperatura_actual o tiempo_restante no disponibles ENTONCES usar valores por defecto conservadores'});

CREATE (:ReglaCrisp {regla_id:'S4', modulo:'M3', tipo:'contextual', cobertura:'consulta_ejecutable',
  descripcion:'Múltiples incidencias simultáneas en el mismo inmueble',
  expresion:'SI existen dos o más incidencias activas en el mismo inmueble ENTONCES elevar prioridad de atención'});

CREATE (:ReglaCrisp {regla_id:'S5', modulo:'M3', tipo:'contextual', cobertura:'consulta_ejecutable',
  descripcion:'Sensibilidad contextual continua de climatización',
  expresion:'SI servicio es climatización ENTONCES sensibilidad = base + 4.5 * max(mu_Alto, mu_Extremo)'});

CREATE (:ReglaCrisp {regla_id:'T1', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Mapeo de puntaje difuso a nivel de severidad',
  expresion:'SI puntaje in [0,20)->1, [20,40)->2, [40,60)->3, [60,80)->4, [80,100]->5'});

CREATE (:ReglaCrisp {regla_id:'T2', modulo:'M3', tipo:'deterministica', cobertura:'consulta_ejecutable',
  descripcion:'Canal de notificación y SLA por nivel de severidad',
  expresion:'SI nivel 1-2 -> reporte diario; nivel 3 -> cola priorizada; nivel 4-5 -> alerta inmediata push/SMS'});
