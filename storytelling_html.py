import json

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        body {
            margin: 0; padding: 0;
            font-family: 'Outfit', sans-serif;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100vw;
            background: transparent;
        }
        canvas, svg {
            max-width: 100%;
            max-height: 100%;
        }
    </style>
</head>
<body>
"""

def get_d3_map(gdf_json):
    return BASE_HTML + f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        #map-container {{ width: 100%; height: 100%; border-radius: 12px; overflow: hidden; }}
        .leaflet-container {{ background: transparent; font-family: 'Outfit', sans-serif; }}
        .colorbar-container {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(5px);
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        .colorbar-title {{ font-weight: 700; margin-bottom: 8px; font-size: 14px; color: #4A4A4A; }}
        .colorbar {{ width: 20px; height: 150px; border-radius: 4px; background: linear-gradient(to bottom, #8F3A2F, #F3C8C2); }}
        .colorbar-labels {{ position: absolute; left: 45px; top: 35px; height: 150px; display: flex; flex-direction: column; justify-content: space-between; font-size: 12px; color: #777; }}
        .custom-tooltip {{
            background: rgba(255,255,255,0.95);
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            padding: 10px 15px;
            font-size: 14px;
            color: #4A4A4A;
            border-left: 4px solid #8F3A2F;
        }}
    </style>
    <div id="map-container">
        <div class="colorbar-container">
            <div class="colorbar-title">Pobreza (%)</div>
            <div class="colorbar"></div>
            <div class="colorbar-labels">
                <span id="cb-max"></span>
                <span></span>
                <span id="cb-min">0%</span>
            </div>
        </div>
    </div>
    <script>
        const gdf = {gdf_json};
        
        // Setup Leaflet map (disable zoom/pan to keep it like a static graphic)
        const map = L.map('map-container', {{ zoomControl: false, dragging: false, scrollWheelZoom: false, doubleClickZoom: false }});
        
        // Color scale logic
        const maxPob = Math.max(...gdf.features.map(f => f.properties.pobreza || 0));
        document.getElementById('cb-max').innerText = maxPob.toFixed(1) + "%";
        
        function getColor(pobreza) {{
            // Rango de F3C8C2 a 8F3A2F
            const pct = pobreza / maxPob;
            // Interpolacion lineal manual sencilla
            const r = Math.round(243 - pct * (243 - 143));
            const g = Math.round(200 - pct * (200 - 58));
            const b = Math.round(194 - pct * (194 - 47));
            return `rgb(${{r}},${{g}},${{b}})`;
        }}

        // Add GeoJSON Layer
        const geojsonLayer = L.geoJSON(gdf, {{
            style: function(feature) {{
                return {{
                    fillColor: getColor(feature.properties.pobreza || 0),
                    weight: 1,
                    opacity: 1,
                    color: 'white',
                    fillOpacity: 0.95
                }};
            }},
            onEachFeature: function(feature, layer) {{
                layer.bindTooltip(`<b>${{feature.properties.Region}}</b><br>Tasa de pobreza: <b>${{feature.properties.pobreza}}%</b>`, {{
                    className: 'custom-tooltip',
                    sticky: true,
                    direction: 'top'
                }});
                layer.on({{
                    mouseover: function(e) {{
                        const l = e.target;
                        l.setStyle({{ weight: 2.5, color: '#4A4A4A' }});
                        l.bringToFront();
                    }},
                    mouseout: function(e) {{
                        geojsonLayer.resetStyle(e.target);
                    }}
                }});
            }}
        }}).addTo(map);
        
        // Ajustar el mapa exactamente a los límites de Chile
        map.fitBounds(geojsonLayer.getBounds(), {{ padding: [10, 10] }});
    </script>
</body>
</html>
"""

def get_chartjs_scatter(scatter_data):
    return BASE_HTML + f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <div style="width: 95%; height: 95%;"><canvas id="chart"></canvas></div>
    <script>
        Chart.defaults.font.family = 'Outfit';
        Chart.defaults.color = '#4A4A4A';
        Chart.register(ChartDataLabels);
        const data = {json.dumps(scatter_data)};
        
        new Chart(document.getElementById('chart'), {{
            type: 'scatter',
            plugins: [ChartDataLabels],
            data: {{
                datasets: [{{
                    label: 'Regiones',
                    data: data.map(d => ({{x: d.Ruralidad, y: d.Pobreza, r: d.Region === 'La Araucanía' ? 14 : 8, region: d.Region}})),
                    backgroundColor: data.map(d => d.Region === 'La Araucanía' ? '#8F3A2F' : '#A6A6A6'),
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                animation: {{ duration: 1500, easing: 'easeOutQuart' }},
                plugins: {{
                    legend: {{display: false}},
                    datalabels: {{
                        display: true,
                        color: '#4A4A4A',
                        anchor: 'end',
                        align: 'top',
                        formatter: function(value, context) {{
                            return context.dataset.data[context.dataIndex].region;
                        }},
                        font: {{ size: 10, family: 'Outfit' }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        titleColor: '#8F3A2F', bodyColor: '#4A4A4A', borderColor: 'rgba(0,0,0,0.1)', borderWidth: 1,
                        callbacks: {{
                            label: function(ctx) {{ return ctx.raw.region + ': Ruralidad ' + ctx.raw.x.toFixed(1) + '%, Pobreza ' + ctx.raw.y.toFixed(1) + '%'; }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ title: {{display: true, text: 'Población Rural (%)', font: {{weight: 'bold'}} }}, grid: {{color: 'rgba(0,0,0,0.05)'}} }},
                    y: {{ title: {{display: true, text: 'Tasa de Pobreza (%)', font: {{weight: 'bold'}} }}, grid: {{color: 'rgba(0,0,0,0.05)'}} }}
                }}
            }}
        }});
    </script>
</body></html>"""

def get_chartjs_educ(educ_data):
    return BASE_HTML + f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <div style="width: 95%; height: 95%;"><canvas id="chart"></canvas></div>
    <script>
        Chart.defaults.font.family = 'Outfit';
        Chart.defaults.color = '#4A4A4A';
        const data = {json.dumps(educ_data)};
        const labels = data.map(d => d.region_nombre);
        
        new Chart(document.getElementById('chart'), {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [
                    {{ label: 'Básica o menos', data: data.map(d => d['Básica o menos']), backgroundColor: labels.map(r => r === 'La Araucanía' ? '#8F3A2F' : '#4A4A4A') }},
                    {{ label: 'Media', data: data.map(d => d['Media']), backgroundColor: labels.map(r => r === 'La Araucanía' ? '#B58C86' : '#777777') }},
                    {{ label: 'Técnica', data: data.map(d => d['Técnica']), backgroundColor: labels.map(r => r === 'La Araucanía' ? '#E9A097' : '#A6A6A6') }},
                    {{ label: 'Universitaria', data: data.map(d => d['Universitaria']), backgroundColor: labels.map(r => r === 'La Araucanía' ? '#F3C8C2' : '#D9D9D9') }}
                ]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true, maintainAspectRatio: false,
                animation: {{ duration: 1500, easing: 'easeOutBounce' }},
                plugins: {{ 
                    legend: {{
                        position: 'bottom', 
                        labels: {{
                            usePointStyle: true,
                            generateLabels: function(chart) {{
                                const colors = ['#8F3A2F', '#B58C86', '#E9A097', '#F3C8C2'];
                                return chart.data.datasets.map((dataset, i) => ({{
                                    text: dataset.label,
                                    fillStyle: colors[i],
                                    strokeStyle: colors[i],
                                    lineWidth: 0,
                                    hidden: !chart.isDatasetVisible(i),
                                    datasetIndex: i
                                }}));
                            }}
                        }} 
                    }} 
                }},
                scales: {{
                    x: {{ stacked: true, title: {{display:true, text:'Porcentaje (%)', font: {{weight: 'bold'}}}}, grid: {{color: 'rgba(0,0,0,0.05)'}} }},
                    y: {{ stacked: true, grid: {{display: false}} }}
                }}
            }}
        }});
    </script>
</body></html>"""

def get_chartjs_line(growth_data):
    return BASE_HTML + f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <div style="width: 95%; height: 95%;"><canvas id="chart"></canvas></div>
    <script>
        Chart.defaults.font.family = 'Outfit';
        Chart.defaults.color = '#4A4A4A';
        const data = {json.dumps(growth_data)};
        
        const lineAraucania = data.filter(d => d.Región === 'La Araucanía');
        const lineMetro = data.filter(d => d.Región === 'Metropolitana');
        const lineChile = data.filter(d => d.Región === 'Chile');
        const edades = [...new Set(data.map(d => d.Edad))];
        
        new Chart(document.getElementById('chart'), {{
            type: 'line',
            data: {{
                labels: edades,
                datasets: [
                    {{ label: 'La Araucanía', data: lineAraucania.map(d => d.Ingreso/1000), borderColor: '#8F3A2F', backgroundColor: '#8F3A2F', tension: 0.4, borderWidth: 4 }},
                    {{ label: 'Metropolitana', data: lineMetro.map(d => d.Ingreso/1000), borderColor: '#4A4A4A', backgroundColor: '#4A4A4A', tension: 0.4 }},
                    {{ label: 'Chile', data: lineChile.map(d => d.Ingreso/1000), borderColor: '#A6A6A6', backgroundColor: '#A6A6A6', tension: 0.4 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                animation: {{
                    x: {{ type: 'number', easing: 'linear', duration: 1000, from: NaN, delay(ctx) {{ return ctx.type === 'data' && ctx.xStarted === undefined ? ctx.index * 100 : 0; }} }},
                    y: {{ type: 'number', easing: 'linear', duration: 1000, from: (ctx) => ctx.chart.scales.y.getPixelForValue(100) }}
                }},
                plugins: {{ legend: {{position: 'bottom', labels: {{usePointStyle: true}} }} }},
                scales: {{
                    y: {{ title: {{display: true, text: 'Ingreso per cápita (miles $)', font: {{weight: 'bold'}} }}, grid: {{color: 'rgba(0,0,0,0.05)'}} }},
                    x: {{ grid: {{display: false}} }}
                }}
            }}
        }});
    </script>
</body></html>"""

def get_chartjs_radar(radar_data):
    return BASE_HTML + f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <div style="width: 95%; height: 95%;"><canvas id="chart"></canvas></div>
    <script>
        Chart.defaults.font.family = 'Outfit';
        Chart.defaults.color = '#4A4A4A';
        const data = {json.dumps(radar_data)};
        const labels = data.map(d => d.Indicador.replace('<br>', ' '));
        
        new Chart(document.getElementById('chart'), {{
            type: 'radar',
            data: {{
                labels: labels,
                datasets: [
                    {{ label: 'Chile', data: data.map(d => d.Chile), borderColor: '#A6A6A6', backgroundColor: 'rgba(166, 166, 166, 0.2)', pointBackgroundColor: '#A6A6A6' }},
                    {{ label: 'La Araucanía', data: data.map(d => d['La Araucanía']), borderColor: '#8F3A2F', backgroundColor: 'rgba(143, 58, 47, 0.3)', pointBackgroundColor: '#8F3A2F' }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                animation: {{ duration: 2000, easing: 'easeOutCirc' }},
                plugins: {{ legend: {{position: 'bottom', labels: {{usePointStyle: true}} }} }},
                scales: {{
                    r: {{
                        angleLines: {{color: 'rgba(0,0,0,0.1)'}},
                        grid: {{color: 'rgba(0,0,0,0.1)'}},
                        pointLabels: {{font: {{size: 13, family: 'Outfit'}} }}
                    }}
                }}
            }}
        }});
    </script>
</body></html>"""
