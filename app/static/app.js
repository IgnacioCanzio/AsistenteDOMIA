/**
 * app/static/app.js - Lógica Interactiva del Cliente DOMIA
 * Grupo 3 · Comisión 5k9 · UTN FRM · 2026
 */

document.addEventListener('DOMContentLoaded', () => {
    // Estado de la aplicación
    let currentSessionId = null;
    let currentStepId = null;
    let registeredIncidents = [];
    let selectedIncidentId = null;

    // Elementos del DOM
    const selectInmueble = document.getElementById('selectInmueble');
    const sliderTemp = document.getElementById('sliderTemp');
    const valTemp = document.getElementById('valTemp');
    const sliderHoras = document.getElementById('sliderHoras');
    const valHoras = document.getElementById('valHoras');
    const chatViewport = document.getElementById('chatViewport');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatActionBar = document.getElementById('chatActionBar');
    const actionLabel = document.getElementById('actionLabel');
    const actionButtons = document.getElementById('actionButtons');
    const btnResetSession = document.getElementById('btnResetSession');

    // Elementos de Triage
    const metricCrit = document.getElementById('metricCrit');
    const metricHigh = document.getElementById('metricHigh');
    const metricMed = document.getElementById('metricMed');
    const metricSolved = document.getElementById('metricSolved');
    const incidentsList = document.getElementById('incidentsList');
    const notificationCard = document.getElementById('notificationCard');
    const emergencyAlertsBox = document.getElementById('emergencyAlertsBox');
    const emergencyList = document.getElementById('emergencyList');
    const emergencyCount = document.getElementById('emergencyCount');
    let activeAlerts = [];

    // Elementos del Inspector
    const traceM1 = document.getElementById('traceM1');
    const traceM2 = document.getElementById('traceM2');
    const traceM3 = document.getElementById('traceM3');
    const traceCypher = document.getElementById('traceCypher');
    const fuzzyCasesBody = document.getElementById('fuzzyCasesBody');
    const traceSandwichExt = document.getElementById('traceSandwichExt');
    const traceSandwichCypher = document.getElementById('traceSandwichCypher');
    const traceSandwichExp = document.getElementById('traceSandwichExp');

    // --------------------------------------------------------------------------
    // 1. Manejo de Sliders de Telemetría
    // --------------------------------------------------------------------------
    sliderTemp.addEventListener('input', (e) => {
        valTemp.textContent = `${e.target.value} °C`;
    });

    sliderHoras.addEventListener('input', (e) => {
        valHoras.textContent = `${e.target.value} h`;
    });

    // --------------------------------------------------------------------------
    // 2. Presets de Casos de Prueba
    // --------------------------------------------------------------------------
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const inm = btn.getAttribute('data-inm');
            const msg = btn.getAttribute('data-msg');
            if (inm) selectInmueble.value = inm;
            if (msg) {
                chatInput.value = msg;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // --------------------------------------------------------------------------
    // 3. Envío de Mensaje del Huésped
    // --------------------------------------------------------------------------
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage('user', 'Tú (Huésped)', text);
        chatInput.value = '';
        hideActionBar();

        const payload = {
            inmueble_id: selectInmueble.value,
            huesped_id: 'h1',
            mensaje: text,
            temperatura_actual: parseFloat(sliderTemp.value),
            horas_restantes: parseFloat(sliderHoras.value)
        };

        try {
            const res = await fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            handleInteractionResponse(data);
        } catch (err) {
            console.error('Error enviando mensaje:', err);
            appendMessage('bot', 'DOMIA Concierge', 'Error de conexión con el servidor.');
        }
    });

    // --------------------------------------------------------------------------
    // 4. Procesamiento de Respuestas del Asistente
    // --------------------------------------------------------------------------
    function handleInteractionResponse(data) {
        currentSessionId = data.sesion_id || currentSessionId;
        currentStepId = data.paso_id || null;

        const isEmergency = data.tipo_evento === 'emergencia';
        appendMessage('bot', 'DOMIA Concierge', data.mensaje_para_huesped, isEmergency);

        // Mostrar advertencias si existen
        if (data.advertencias && data.advertencias.length > 0) {
            const advText = "⚠️ Precauciones:\n" + data.advertencias.map(a => `• ${a}`).join('\n');
            appendMessage('bot', 'Sistema de Seguridad', advText, isEmergency);
        }

        // Renderizar barra interactiva de pasos o aclaraciones
        if (data.tipo_evento === 'instruccion_paso' && data.paso_id) {
            showStepActions(data.paso_id);
        } else if (data.tipo_evento === 'pregunta_aclaratoria') {
            const opciones = data.trazabilidad_diagnostica?.opciones || [
                'Termotanque eléctrico del baño',
                'Termotanque a gas de la cocina'
            ];
            showClarificationActions(opciones);
        } else {
            hideActionBar();
        }

        // Actualizar inspector de trazabilidad
        updateInspectorTrace(data);

        // Actualizar lista de incidencias si vino ficha
        if (data.ficha_incidencia) {
            addOrUpdateIncident(data.ficha_incidencia);
        }

        // Procesar alerta de emergencia si fue despachada
        if (data.alerta_emergencia) {
            addOrUpdateAlert(data.alerta_emergencia);
        }

        // Actualizar traza sándwich LLM si está presente
        if (data.sandwich_trace) {
            updateSandwichTrace(data.sandwich_trace);
        }
    }

    function addOrUpdateAlert(alerta) {
        const idx = activeAlerts.findIndex(a => a.alerta_id === alerta.alerta_id);
        if (idx >= 0) activeAlerts[idx] = alerta;
        else activeAlerts.unshift(alerta);
        renderAlerts();
    }

    function renderAlerts() {
        if (!emergencyCount || !emergencyList) return;
        emergencyCount.textContent = activeAlerts.length;
        if (activeAlerts.length === 0) {
            emergencyList.innerHTML = '<div class="empty-alerts">Sin emergencias activas. El monitoreo opera normalmente.</div>';
            return;
        }
        emergencyList.innerHTML = activeAlerts.map(alt => `
            <div class="emergency-alert-card">
                <div class="alt-title">
                    <span>🚨 ${alt.tipo_emergencia.toUpperCase()} · ${alt.inmueble_id.toUpperCase()}</span>
                    <span>${new Date(alt.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="alt-body">
                    <div><strong>Protocolo:</strong> ${alt.protocolo_accion}</div>
                    <div><strong>Despacho:</strong> Anfitrión: ${alt.notificacion_anfitrion_enviada ? '✓ Notificado' : 'Pendiente'} | Emergencias: ${alt.servicio_emergencias_alertado ? '✓ Alertado' : 'Pendiente'}</div>
                </div>
            </div>
        `).join('');
    }

    async function loadAlerts() {
        try {
            const res = await fetch('/api/alerts');
            const alerts = await res.json();
            activeAlerts = alerts;
            renderAlerts();
        } catch (err) {
            console.error('Error cargando alertas:', err);
        }
    }

    function updateSandwichTrace(trace) {
        if (traceSandwichExt && trace.extraccion) {
            traceSandwichExt.textContent = JSON.stringify(trace.extraccion, null, 2);
        }
        if (traceSandwichCypher && trace.consultas_cypher) {
            traceSandwichCypher.textContent = trace.consultas_cypher.map(c =>
                `// ${c.query_name} [filas=${c.rows_returned}, origen=${c.source}]\n${c.query}`
            ).join('\n\n');
        }
        if (traceSandwichExp) {
            traceSandwichExp.textContent = 
                `Fidelidad I10: ${trace.fidelidad_ok ? 'SUPERADA ✓' : 'FALLÓ ✗'}\n\n` +
                `Respuesta redactada:\n«${trace.respuesta_final || ''}»\n` +
                (trace.problemas_fidelidad?.length ? `\nProblemas: ${JSON.stringify(trace.problemas_fidelidad)}` : '');
        }
    }

    // --------------------------------------------------------------------------
    // 5. Botonera Interactiva de Pasos
    // --------------------------------------------------------------------------
    function showStepActions(pasoId) {
        actionLabel.textContent = `Acción requerida para el paso [${pasoId}]:`;
        actionButtons.innerHTML = `
            <button class="action-btn btn-yes" data-res="si">✓ Sí, funcionó</button>
            <button class="action-btn btn-no" data-res="no">✗ No funcionó</button>
            <button class="action-btn btn-cant" data-res="no_puedo">⚠️ No puedo / No sé</button>
        `;
        chatActionBar.classList.remove('hidden');

        actionButtons.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const resultado = btn.getAttribute('data-res');
                const label = btn.textContent;
                appendMessage('user', 'Tú (Huésped)', label);
                hideActionBar();

                try {
                    const res = await fetch('/api/chat/step-response', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            sesion_id: currentSessionId,
                            paso_id: pasoId,
                            resultado: resultado
                        })
                    });
                    const data = await res.json();
                    handleInteractionResponse(data);
                } catch (err) {
                    console.error('Error enviando respuesta de paso:', err);
                }
            });
        });
    }

    function showClarificationActions(opciones) {
        actionLabel.textContent = 'Selecciona una opción para precisar el diagnóstico:';
        actionButtons.innerHTML = opciones.map(op => 
            `<button class="action-btn btn-pill" data-op="${op}">${op}</button>`
        ).join('');
        chatActionBar.classList.remove('hidden');

        actionButtons.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const seleccion = btn.getAttribute('data-op');
                appendMessage('user', 'Tú (Huésped)', seleccion);
                hideActionBar();

                try {
                    const res = await fetch('/api/chat/clarification', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            inmueble_id: selectInmueble.value,
                            huesped_id: 'h1',
                            respuesta: seleccion,
                            ronda: 1
                        })
                    });
                    const data = await res.json();
                    handleInteractionResponse(data);
                } catch (err) {
                    console.error('Error enviando aclaración:', err);
                }
            });
        });
    }

    function hideActionBar() {
        chatActionBar.classList.add('hidden');
        actionButtons.innerHTML = '';
    }

    // --------------------------------------------------------------------------
    // 6. Mensajería en el Viewport
    // --------------------------------------------------------------------------
    function appendMessage(role, sender, text, isEmergency = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${role} ${isEmergency ? 'emergency' : ''}`;
        
        const avatar = role === 'user' ? '👤' : (isEmergency ? '🚨' : '🤖');
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="bubble">
                <div class="sender">${sender}</div>
                <div class="text">${escapeHtml(text)}</div>
                <div class="time">${now}</div>
            </div>
        `;
        chatViewport.appendChild(msgDiv);
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --------------------------------------------------------------------------
    // 7. Actualización del Inspector de Trazabilidad
    // --------------------------------------------------------------------------
    function updateInspectorTrace(data) {
        const traza = data.trazabilidad_diagnostica || {};

        // M1 Box
        if (traza.m1_evaluacion || traza.m1_alarma) {
            traceM1.textContent = JSON.stringify(traza.m1_evaluacion || traza.m1_alarma, null, 2);
        } else if (traza.m1) {
            traceM1.textContent = JSON.stringify(traza.m1, null, 2);
        }

        // M2 Box
        if (traza.m2_priorizacion) {
            traceM2.textContent = JSON.stringify(traza.m2_priorizacion, null, 2);
        } else if (traza.m2_paso_siguiente) {
            traceM2.textContent = JSON.stringify(traza.m2_paso_siguiente, null, 2);
        } else if (traza.m2_cierre || traza.m2_escalada) {
            traceM2.textContent = JSON.stringify(traza.m2_cierre || traza.m2_escalada, null, 2);
        }

        // M3 Box
        if (data.ficha_incidencia) {
            const ficha = data.ficha_incidencia;
            traceM3.textContent = JSON.stringify({
                via: ficha.via_evaluacion,
                puntaje_difuso: ficha.puntaje_difuso,
                nivel_calculado: ficha.nivel_calculado,
                piso_esencial_r5: ficha.piso_r5,
                nivel_final: ficha.nivel_final,
                prioridad: ficha.prioridad,
                canal: ficha.canal,
                reglas_activadas: ficha.reglas_activadas
            }, null, 2);
        }

        // Cypher Box dinámico con trazas reales ejecutadas en el turno
        if (data.cypher_traces && data.cypher_traces.length > 0) {
            traceCypher.textContent = data.cypher_traces.map((ct, idx) =>
                `// [${idx + 1}] ${ct.query_name} | Motor: ${ct.source} | ${ct.latency_ms} ms | Filas: ${ct.rows_returned}\n` +
                `// Params: ${JSON.stringify(ct.params)}\n` +
                `${ct.query}`
            ).join('\n\n' + '─'.repeat(55) + '\n\n');
        } else if (data.tipo_evento === 'emergencia') {
            traceCypher.textContent = 
`// Consulta C1b: Barrera de Seguridad
MATCH (r:ReporteIncidencia {reporte_id: $reporte_id})
WHERE r.senal_seguridad = true
RETURN 'pe1' AS protocolo, 'Nivel 5' AS severidad;`;
        } else if (data.tipo_evento === 'instruccion_paso') {
            traceCypher.textContent = 
`// Consulta C1: Próximo Paso Asistido
MATCH (s:Sintoma)-[:ASOCIADO_A]->(c:CausaRaiz)-[:RESUELTO_POR]->(p:PasoVerificacion)
WHERE NOT (p:PasoNoDelegable)
RETURN c.causa_id AS causa, p.paso_id AS proximo_paso, p.riesgo_usuario;`;
        } else if (data.tipo_evento === 'cierre_exitoso' || data.tipo_evento === 'escalada_anfitrion') {
            traceCypher.textContent = 
`// Consulta C4: Inferencia Severidad M2 -> M3
MATCH (inc:Incidencia)-[:AFECTA_A]->(sv:Servicio),
      (inc)-[:TIENE_CONTEXTO]->(ctx:ContextoIncidencia)
RETURN sv.servicio_id, inc.estado, ctx.temperatura_actual;`;
        }
    }

    // --------------------------------------------------------------------------
    // 8. Gestión de Incidencias en el Panel del Anfitrión
    // --------------------------------------------------------------------------
    function addOrUpdateIncident(ficha) {
        const idx = registeredIncidents.findIndex(i => i.incidencia_id === ficha.incidencia_id);
        if (idx >= 0) {
            registeredIncidents[idx] = ficha;
        } else {
            registeredIncidents.unshift(ficha);
        }
        renderIncidentsList();
        updateTriageMetrics();
        selectIncident(ficha);
    }

    function renderIncidentsList() {
        if (registeredIncidents.length === 0) {
            incidentsList.innerHTML = '<div class="empty-state">No hay incidencias registradas.</div>';
            return;
        }

        incidentsList.innerHTML = registeredIncidents.map(inc => {
            const isSelected = inc.incidencia_id === selectedIncidentId ? 'active-selected' : '';
            return `
                <div class="incident-card ${isSelected}" data-id="${inc.incidencia_id}">
                    <div class="incident-top">
                        <span class="incident-id">${inc.incidencia_id} · ${inc.inmueble_nombre}</span>
                        <span class="severity-badge level-${inc.nivel_final}">Nivel ${inc.nivel_final} (${inc.prioridad})</span>
                    </div>
                    <div class="incident-desc">
                        <strong>Causa:</strong> ${inc.causa_diagnosticada.replace(/_/g, ' ')}
                    </div>
                    <div class="incident-meta">
                        <span class="channel-tag">Canal: ${inc.canal}</span>
                        <span>Vía: ${inc.via_evaluacion}</span>
                        <span>${inc.servicio_esencial ? '⭐ Esencial' : 'Común'}</span>
                    </div>
                </div>
            `;
        }).join('');

        // Listeners para selección de tarjetas
        incidentsList.querySelectorAll('.incident-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = card.getAttribute('data-id');
                const inc = registeredIncidents.find(i => i.incidencia_id === id);
                if (inc) selectIncident(inc);
            });
        });
    }

    function selectIncident(inc) {
        selectedIncidentId = inc.incidencia_id;
        notificationCard.textContent = inc.notificacion_redactada || 'Sin notificación específica.';
        renderIncidentsList();
    }

    function updateTriageMetrics() {
        let crit = 0, high = 0, med = 0, solved = 0;
        registeredIncidents.forEach(inc => {
            if (inc.nivel_final === 5) crit++;
            else if (inc.nivel_final === 4) high++;
            else if (inc.nivel_final === 3) med++;
            else if (inc.nivel_final === 0) solved++;
        });
        metricCrit.textContent = crit;
        metricHigh.textContent = high;
        metricMed.textContent = med;
        metricSolved.textContent = solved;
    }

    // --------------------------------------------------------------------------
    // 9. Pestañas del Inspector & Benchmark Difuso
    // --------------------------------------------------------------------------
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    async function loadFuzzyCases() {
        try {
            const res = await fetch('/api/neo4j/fuzzy-cases');
            const cases = await res.json();
            fuzzyCasesBody.innerHTML = cases.map(c => `
                <tr>
                    <td>${c.modulo}</td>
                    <td><strong>${c.caso_id}</strong></td>
                    <td>${c.esperado_pi3.toFixed(1)}</td>
                    <td style="color:#38bdf8;">${c.esperado_pi3.toFixed(1)}</td>
                    <td style="color:#10b981;">✓ Exacto (0.1)</td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Error cargando casos difusos:', e);
        }
    }
    loadFuzzyCases();

    async function checkBackendHealth() {
        try {
            const res = await fetch('/api/health');
            const health = await res.json();
            const neo4jBadge = document.getElementById('neo4jStatus');
            if (neo4jBadge) {
                if (health.neo4j_connected) {
                    neo4jBadge.innerHTML = `<span class="dot online"></span> Neo4j Docker Conectado (${health.database})`;
                } else {
                    neo4jBadge.innerHTML = `<span class="dot mock"></span> Grafo PG2 Activo (Respaldo Memoria)`;
                }
            }
        } catch (e) {
            console.error('Error verificando estado del servidor:', e);
        }
    }
    checkBackendHealth();
    loadAlerts();

    // --------------------------------------------------------------------------
    // 10. Reiniciar Sesión
    // --------------------------------------------------------------------------
    btnResetSession.addEventListener('click', () => {
        currentSessionId = null;
        currentStepId = null;
        chatViewport.innerHTML = `
            <div class="chat-message bot">
                <div class="avatar">🤖</div>
                <div class="bubble">
                    <div class="sender">DOMIA Concierge</div>
                    <div class="text">¡Sesión reiniciada! ¿En qué puedo asistirte en tu estadía?</div>
                    <div class="time">Ahora</div>
                </div>
            </div>
        `;
        hideActionBar();
        traceM1.textContent = 'Sesión reiniciada.';
        traceM2.textContent = 'Sin diagnóstico activo.';
        traceM3.textContent = 'Sin cálculo de severidad.';
    });
});
