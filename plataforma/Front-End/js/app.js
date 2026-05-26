// js/app.js
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Conexión Real de Login con la API (Python)
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Evita que la página recargue
            
            // Obtenemos los valores de los inputs
            const inputs = loginForm.querySelectorAll('.login-input');
            const email = inputs[0].value;
            const password = inputs[1].value;

            try {
                // Hacemos la petición a Python (Back-End)
                const respuesta = await fetch('http://127.0.0.1:5000/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ usuario: email, password: password })
                });

                const datos = await respuesta.json();

                if (datos.estado === "EXITO") {
                    // Si Python dice que todo está bien, entramos a la plataforma
                    alert(datos.mensaje);
                    window.location.href = 'capa1.html';
                } else {
                    // Si Python detecta un error (contraseña mala)
                    alert("Acceso Denegado: " + datos.mensaje);
                }
            } catch (error) {
                alert("Error de conexión con el servidor Back-End.");
                console.error(error);
            }
        });
    }

    // 2. Funcionalidad de ocultar/mostrar Sidebar
    const toggleBtn = document.getElementById('toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });
    }

   // 3. Subida REAL de archivo en Capa 1 con Vista Previa Dinámica
    const fileInput = document.getElementById('file-upload');
    const previewContainer = document.getElementById('preview-container');
    const previewTable = document.getElementById('preview-table');

    if (fileInput) {
        fileInput.addEventListener('change', async function() {
            if (this.files && this.files.length > 0) {
                const archivo = this.files[0];
                
                // --- PARTE DINÁMICA: LEER EL CSV PARA LA VISTA PREVIA ---
                const reader = new FileReader();
                reader.onload = function(e) {
                    const texto = e.target.result;
                    // Quitamos el ".slice" para que lea TODAS las líneas, ignorando las vacías
                    const lineas = texto.split('\n').filter(linea => linea.trim() !== ''); 
                    
                    let htmlTabla = "";
                    lineas.forEach((linea, index) => {
                        const columnas = linea.split(',');
                        if (columnas.length > 1) {
                            if (index === 0) {
                                htmlTabla += `<thead class="font-mono" style="background: rgba(255,255,255,0.02); position: sticky; top: 0;"><tr>`;
                                columnas.forEach(col => htmlTabla += `<th style="padding: 10px; border-bottom: 1px solid var(--border-color);">${col.trim()}</th>`);
                                htmlTabla += `</tr></thead><tbody>`;
                            } else {
                                htmlTabla += `<tr style="border-bottom: 1px solid rgba(255,255,255,0.02);">`;
                                columnas.forEach(col => htmlTabla += `<td style="padding: 10px; color: var(--text-secondary);">${col.trim()}</td>`);
                                htmlTabla += `</tr>`;
                            }
                        }
                    });
                    htmlTabla += `</tbody>`;
                    
                    previewTable.innerHTML = htmlTabla;
                    // Agregamos el scroll dinámico (máximo ~8 registros de alto)
                    previewTable.parentElement.style.maxHeight = "350px"; 
                    previewTable.parentElement.style.overflowY = "auto";
                    previewContainer.style.display = "block";
                };
                reader.readAsText(archivo);
                // --- FIN DE LA PARTE DE VISTA PREVIA ---

                // Enviamos el archivo al Back-End (Python) tal como funcionaba antes
                const formData = new FormData();
                formData.append('file', archivo);

                try {
                    const respuesta = await fetch('http://127.0.0.1:5000/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const datos = await respuesta.json();

                    if(datos.estado === "EXITO") {
                        console.log("Servidor Python recibió el archivo.");
                    } else {
                        alert("❌ Error en servidor: " + datos.mensaje);
                    }
                } catch(error) {
                    alert("Error de conexión al subir el archivo.");
                    console.error(error);
                }
            }
        });
    }

    // 4. Cargar dinámicamente la tabla de la Capa 2 desde Python
    const stagingTbody = document.getElementById('staging-tbody');
    if (stagingTbody) {
        // Ejecutamos una petición GET a Python apenas entramos a la Capa 2
        fetch('http://127.0.0.1:5000/staging-files')
            .then(respuesta => respuesta.json())
            .then(datos => {
                if (datos.estado === "EXITO" && datos.archivos.length > 0) {
                    let htmlFilas = "";
                    
                    datos.archivos.forEach(file => {
                        // Decidimos el color del badge según el estado que envió Python
                        const badgeClass = file.estado.includes("Errores") ? "status-error" : "status-wait";
                        const icon = file.estado.includes("Errores") ? "fa-circle-exclamation" : "fa-hourglass-half";
                        
                        htmlFilas += `
                            <tr>
                                <td style="color: var(--cyan);">${file.id}</td>
                                <td>${file.nombre}</td>
                                <td>${file.fecha}</td>
                                <td>${file.tamano}</td>
                                <td><span class="status-badge ${badgeClass}"><i class="fa-solid ${icon}"></i> ${file.estado}</span></td>
                            </tr>
                        `;
                    });
                    stagingTbody.innerHTML = htmlFilas;
                } else {
                    stagingTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--text-secondary);">No hay archivos pendientes en la carpeta de uploads.</td></tr>`;
                }
            })
            .catch(error => {
                console.error("Error al mapear el Staging Area:", error);
                stagingTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 20px; color: #f87171;">Error al conectar con la API de Staging.</td></tr>`;
            });
    }

    // 5. Animación y ejecución del ETL (Capa 3)
    const btnEtl = document.getElementById('btn-iniciar-etl');
    if (btnEtl) {
        btnEtl.addEventListener('click', async () => {
            const progressBar = document.getElementById('etl-progress');
            const statusText = document.getElementById('etl-status');
            const step1 = document.getElementById('step-1');
            const step2 = document.getElementById('step-2');
            const step3 = document.getElementById('step-3');
            
            // Iniciamos la animación visual
            btnEtl.disabled = true;
            statusText.innerText = '1. Extrayendo archivo CSV...';
            progressBar.style.width = '30%';
            step1.style.borderColor = '#10b981'; // Verde
            
            try {
                // Llamamos a Python para que haga el trabajo real
                const respuesta = await fetch('http://127.0.0.1:5000/run-etl', { method: 'POST' });
                const datos = await respuesta.json();
                
                // Simulamos un pequeño retraso visual para que el usuario vea la "Transformación"
                setTimeout(() => {
                    statusText.innerText = '2. Limpiando datos con Pandas...';
                    progressBar.style.width = '65%';
                    step2.style.borderColor = '#f59e0b'; // Amarillo
                }, 1000);

                setTimeout(() => {
                    if(datos.estado === "EXITO") {
                        statusText.innerText = '3. Carga exitosa: 100%';
                        progressBar.style.width = '100%';
                        step3.style.borderColor = 'var(--cyan)';
                        alert("✅ " + datos.mensaje);
                    } else {
                        statusText.innerText = 'Error en el proceso';
                        statusText.style.color = '#f87171';
                        alert("❌ Error: " + datos.mensaje);
                    }
                    btnEtl.disabled = false;
                }, 2500);

            } catch (error) {
                console.error("Error en ETL:", error);
                alert("Error crítico de conexión con el motor ETL.");
                btnEtl.disabled = false;
            }
        });
    }

    // 6. Consultar métricas del Data Warehouse (Capa 4)
    const dwTotalRows = document.getElementById('dw-total-rows');
    if (dwTotalRows) {
        fetch('http://127.0.0.1:5000/dw-stats')
            .then(res => res.json())
            .then(datos => {
                if(datos.estado === "EXITO") {
                    // Actualizamos el número en la pantalla
                    dwTotalRows.innerText = datos.total_registros;
                }
            })
            .catch(err => console.error("Error consultando DW:", err));
    }
    

    // 7. Ejecutar modelo IA (Capa 5)
    const btnIa = document.getElementById('btn-ejecutar-ia');
    if (btnIa) {
        btnIa.addEventListener('click', async () => {
            const tbody = document.getElementById('ia-tbody');
            const precisionLabel = document.getElementById('ia-precision');
            
            btnIa.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Calculando...';
            btnIa.disabled = true;

            try {
                const res = await fetch('http://127.0.0.1:5000/run-predictions');
                const datos = await res.json();

                if(datos.estado === "EXITO") {
                    precisionLabel.innerText = datos.precision_modelo;
                    let filas = "";
                    datos.datos.forEach(p => {
                        // Colores según el riesgo
                        let color = p.riesgo === 'ALTO' ? '#f87171' : (p.riesgo === 'MEDIO' ? '#f59e0b' : '#10b981');
                        let bg = p.riesgo === 'ALTO' ? 'rgba(248,113,113,0.1)' : (p.riesgo === 'MEDIO' ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.1)');
                        
                        filas += `<tr>
                            <td style="color: white;">${p.distrito} - ${p.zona}</td>
                            <td>${p.horario}</td>
                            <td><div style="width: 100%; background: var(--bg-main); border-radius: 4px; height: 8px;"><div style="width: ${p.probabilidad}%; background: ${color}; height: 8px; border-radius: 4px;"></div></div><span style="font-size: 10px; color: var(--text-secondary);">${p.probabilidad}%</span></td>
                            <td><span class="status-badge" style="color: ${color}; border-color: ${color}; background: ${bg};">${p.riesgo} RIESGO</span></td>
                        </tr>`;
                    });
                    tbody.innerHTML = filas;
                    alert("✅ " + datos.mensaje);
                }
            } catch (e) {
                alert("Error conectando con el motor de IA.");
            }
            btnIa.innerHTML = '<i class="fa-solid fa-microchip"></i> Entrenar y Predecir';
            btnIa.disabled = false;
        });
    }
// ==========================================
    // 8. CARGAR MÉTRICAS DINÁMICAS (Capa 6)
    // ==========================================
    const kpi1 = document.getElementById('kpi-1');
    if (kpi1) {
        fetch('http://127.0.0.1:5000/kpi-metrics')
            .then(res => res.json())
            .then(datos => {
                if (datos.estado === "EXITO") {
                    document.getElementById('kpi-1').innerText = datos.kpis.total_incidentes;
                    document.getElementById('kpi-2').innerHTML = `${datos.kpis.tiempo_respuesta}`;
                    document.getElementById('kpi-3').innerText = datos.kpis.porcentaje_extorsion;
                    document.getElementById('kpi-4').innerText = datos.kpis.tasa_captura;
                    document.getElementById('kpi-5').innerText = datos.kpis.indice_uso_armas;
                } else {
                    console.error("Error desde Python en Capa 6:", datos.mensaje);
                }
            })
            .catch(err => console.error("Fallo de conexión Capa 6:", err));
    }
    // ==========================================
    // 9. LÓGICA INTEGRADA DE CONTROL DE LA CAPA 7
    // ==========================================
    const btnToggleSidebar = document.getElementById('toggle-sidebar');
    const sidebarElement = document.getElementById('sidebar');
    if (btnToggleSidebar && sidebarElement) {
        btnToggleSidebar.addEventListener('click', () => {
            sidebarElement.classList.toggle('collapsed');
        });
    }

    const ctxCheck = document.getElementById('gEstadistico1');
    if (ctxCheck) {
        Chart.defaults.color = '#9ca3af';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.02)';

        let chartE1, chartE2, chartE3, chartP1, chartP2, chartP3;

        async function refrescarDashboardCompleto() {
            const parametrosFiltro = {
                distrito: document.getElementById('filtro-distrito').value,
                delito: document.getElementById('filtro-delito').value,
                horario: document.getElementById('filtro-horario').value
            };

            try {
                const res = await fetch('http://127.0.0.1:5000/dashboard-analytics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(parametrosFiltro)
                });
                const datos = await res.json();

                if (datos.estado === "EXITO") {
                    // Actualizar KPIs superiores
                    // Actualización inmediata de los 5 KPIs exactos de la Capa 6
                    document.getElementById('kpi-total').innerText = datos.total;
                    document.getElementById('kpi-tiempo').innerText = datos.avg_tiempo;
                    document.getElementById('kpi-extorsion').innerText = datos.pct_extorsion;
                    document.getElementById('kpi-captura').innerText = datos.pct_captura;
                    document.getElementById('kpi-armas').innerText = datos.pct_armas;

                    // Actualizar Tabla
                    const tbodyData = document.getElementById('tabla-dashboard-dinamica');
                    let htmlFilas = "";
                    if (datos.tabla.length > 0) {
                        datos.tabla.forEach(fila => {
                            const badge = fila.estado === "Crítico" ? "status-error" : "status-accept";
                            htmlFilas += `<tr><td style='color:white;'>${fila.cuadrante}</td><td>${fila.delito}</td><td>${fila.efectivos}</td><td><span class='status-badge ${badge}'>${fila.estado}</span></td></tr>`;
                        });
                    } else {
                        htmlFilas = `<tr><td colspan='4' style='text-align:center; padding:15px; color:#9ca3af;'>Sin datos para estos filtros.</td></tr>`;
                    }
                    tbodyData.innerHTML = htmlFilas;

                    // Destruir gráficos anteriores para redibujar
                    if(chartE1) chartE1.destroy(); if(chartE2) chartE2.destroy(); if(chartE3) chartE3.destroy();
                    if(chartP1) chartP1.destroy(); if(chartP2) chartP2.destroy(); if(chartP3) chartP3.destroy();

                    // Dibujar gráficos nuevos
                    chartE1 = new Chart(document.getElementById('gEstadistico1'), { type: 'bar', data: { labels: Object.keys(datos.distritos), datasets: [{ data: Object.values(datos.distritos), backgroundColor: '#22d3ee' }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } });
                    chartE2 = new Chart(document.getElementById('gEstadistico2'), { type: 'doughnut', data: { labels: Object.keys(datos.delitos), datasets: [{ data: Object.values(datos.delitos), backgroundColor: ['#f87171', '#f59e0b', '#22d3ee', '#10b981', '#a78bfa', '#6b7280'], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } });
                    chartE3 = new Chart(document.getElementById('gEstadistico3'), { type: 'polarArea', data: { labels: Object.keys(datos.horarios), datasets: [{ data: Object.values(datos.horarios), backgroundColor: ['rgba(34,211,238,0.4)', 'rgba(167,139,250,0.4)', 'rgba(245,158,11,0.4)', 'rgba(16,185,129,0.4)'], borderWidth: 0 }] }, options: { responsive: true, maintainAspectRatio: false } });
                    
                    chartP1 = new Chart(document.getElementById('gPredictivo1'), { type: 'radar', data: { labels: Object.keys(datos.distritos), datasets: [{ label: 'Riesgo %', data: Object.values(datos.distritos).map(v => Math.min(35 + (v * 4.5), 97)), borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)' }] }, options: { responsive: true, maintainAspectRatio: false } });
                    chartP2 = new Chart(document.getElementById('gPredictivo2'), { type: 'line', data: { labels: ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'], datasets: [{ label: 'Proyección', data: [0.12, 0.14, 0.11, 0.13, 0.18, 0.22, 0.10].map(p => Math.floor(datos.total * p)), borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.02)', fill: true }] }, options: { responsive: true, maintainAspectRatio: false } });
                    chartP3 = new Chart(document.getElementById('gPredictivo3'), { type: 'bar', data: { labels: ['Violencia', 'Hurto', 'Nulo'], datasets: [{ data: [datos.total - (datos.total*0.3), Math.floor(datos.total * 0.2), Math.floor(datos.total * 0.1)], backgroundColor: '#f87171' }] }, options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } });
                }
            } catch (err) {
                console.error("Error al actualizar Dashboard:", err);
            }
        }

        document.getElementById('filtro-distrito').addEventListener('change', refrescarDashboardCompleto);
        document.getElementById('filtro-delito').addEventListener('change', refrescarDashboardCompleto);
        document.getElementById('filtro-horario').addEventListener('change', refrescarDashboardCompleto);
        
        refrescarDashboardCompleto();
    }

});