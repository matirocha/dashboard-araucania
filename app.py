import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import streamlit.components.v1 as components

DATA_DIR = Path("dashboard_data")

st.set_page_config(page_title="Radiografía a la Araucanía", layout="wide", initial_sidebar_state="collapsed")

# Colores
COLOR_DARK = "#8F3A2F"
COLOR_MED = "#B58C86"
COLOR_LIGHT = "#E9A097"
COLOR_LIGHTEST = "#F3C8C2"
COLOR_URBANO = "#F3C8C2"
COLOR_RURAL = "#8F3A2F"
GRAY_DARK = "#4A4A4A"
GRAY_MED = "#777777"
GRAY_LIGHT = "#A6A6A6"
GRAY_LIGHTEST = "#D9D9D9"
BACKGROUND_COLOR = "#FAF5F0"

# Custom CSS for Premium UI
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Outfit', sans-serif;
    }}
    
    h1, h2, h3, h4 {{
        color: {COLOR_DARK} !important;
        font-weight: 700 !important;
    }}
    
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04);
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s ease-in-out;
        border-left: 6px solid {COLOR_DARK};
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
    }}
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] * {{
        color: #2c2c2c !important;
        font-weight: 600 !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background-color: #E8E0DF;
        padding: 6px;
        border-radius: 16px;
        border: none;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 12px;
        padding: 0px 24px;
        color: #777777 !important;
        transition: all 0.3s ease-in-out;
        border: none !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        color: {COLOR_DARK} !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        border: none !important;
    }}
    
    [data-testid="stPlotlyChart"] {{
        background-color: white;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.03);
    }}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    div[data-testid="stMetric"], div.stPlotlyChart {{
        animation: fadeInUp 0.8s cubic-bezier(0.25, 1, 0.5, 1) both;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Radiografía a la Araucanía: El Ciclo de la Pobreza")
st.markdown("Un análisis profundo de la brecha territorial, económica y educacional.")
st.divider()

@st.cache_data
def load_data():
    DATA_DIR = Path("dashboard_data")
    with open(DATA_DIR / "kpis.json", "r", encoding="utf-8") as f: kpis = json.load(f)
    gdf = gpd.read_file(DATA_DIR / "mapa_pobreza.geojson").clip([-76.0, -60.0, -50.0, -15.0])
    scatter_df = pd.read_csv(DATA_DIR / "scatter.csv")
    df_indig = pd.read_csv(DATA_DIR / "indigena.csv")
    df_radar = pd.read_csv(DATA_DIR / "radar.csv")
    df_growth = pd.read_csv(DATA_DIR / "ingresos_edad.csv")
    df_educ = pd.read_csv(DATA_DIR / "educacion.csv").set_index("region_nombre")
    return kpis, gdf, scatter_df, df_indig, df_radar, df_growth, df_educ

with st.spinner("Cargando dashboard..."):
    kpis, gdf, scatter_df, df_indig, df_radar, df_growth, df_educ = load_data()

# --- FUNCIONES PARA GRÁFICOS ORIGINALES (OTRAS PESTAÑAS) ---
def create_map():
    fig_map = px.choropleth(gdf, geojson=gdf.geometry, locations=gdf.index, color="pobreza", hover_name="Region", hover_data={"pobreza": True}, color_continuous_scale=[BACKGROUND_COLOR, COLOR_LIGHTEST, COLOR_DARK], labels={"pobreza": "Tasa de pobreza (%)"})
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', font_color='black', height=600, dragmode=False)
    return fig_map

def create_scatter():
    fig_scatter = px.scatter(scatter_df, x="Ruralidad", y="Pobreza", color="Region", text="Region", hover_name="Region", color_discrete_map={r: COLOR_DARK if r == 'La Araucanía' else GRAY_LIGHT for r in scatter_df['Region']})
    fig_scatter.update_traces(textposition='top center', textfont_color='black', marker=dict(size=12, line=dict(width=1, color='White')))
    fig_scatter.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', xaxis_title="Población Rural (%)", yaxis_title="Tasa de Pobreza (%)")
    fig_scatter.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"), gridcolor="rgba(0,0,0,0.1)")
    fig_scatter.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"), gridcolor="rgba(0,0,0,0.1)")
    return fig_scatter

def create_radar():
    radar_labels = df_radar['Indicador'].tolist()
    radar_araucania = df_radar['La Araucanía'].tolist()
    radar_chile = df_radar['Chile'].tolist()
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=radar_chile + [radar_chile[0]], theta=radar_labels + [radar_labels[0]], mode='lines+markers', line_color=GRAY_MED, fill='toself', fillcolor='rgba(119, 119, 119, 0.1)', name='Chile'))
    fig_radar.add_trace(go.Scatterpolar(r=radar_araucania + [radar_araucania[0]], theta=radar_labels + [radar_labels[0]], mode='lines+markers', line_color=COLOR_DARK, fill='toself', fillcolor='rgba(143, 58, 47, 0.2)', name='La Araucanía'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, gridcolor='#DDDDDD', linecolor='#CCCCCC'), angularaxis=dict(gridcolor='#DDDDDD', linecolor='#CCCCCC', direction='clockwise', rotation=90, tickfont=dict(color='black'))), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
    return fig_radar

def create_bar():
    fig_bar = px.bar(df_indig, x="Valor", y="Zona", color="Area", barmode="group", orientation='h', color_discrete_map={'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
    fig_bar.update_traces(texttemplate='%{x:.1f}%', textposition='outside', textfont_color='black', cliponaxis=False)
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', xaxis_title="Porcentaje (%)", yaxis_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_bar.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    fig_bar.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    return fig_bar

def create_line():
    df_growth_plot = df_growth.copy()
    df_growth_plot["Ingreso"] = df_growth_plot["Ingreso"] / 1000
    fig_line = px.line(df_growth_plot, x="Edad", y="Ingreso", color="Región", markers=True, color_discrete_map={'Metropolitana': GRAY_DARK, 'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
    fig_line.update_traces(hovertemplate="Rango de edad: %{x}<br>Ingreso: $%{y:,.0f} mil")
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', yaxis_title="Ingreso per cápita (miles de $)")
    fig_line.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    fig_line.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    return fig_line

def create_stack():
    df_educ_sorted = df_educ.sort_values(by="Básica o menos", ascending=True)
    educ_order = ["Básica o menos", "Media", "Técnica", "Universitaria"]
    colors_araucania = [COLOR_DARK, COLOR_MED, COLOR_LIGHT, COLOR_LIGHTEST]
    colors_gray = [GRAY_DARK, GRAY_MED, GRAY_LIGHT, GRAY_LIGHTEST]
    
    fig_stack = go.Figure()
    for i, col in enumerate(educ_order):
        fig_stack.add_trace(go.Bar(y=[df_educ_sorted.index[0]], x=[0], name=col, orientation='h', marker_color=colors_araucania[i], showlegend=True, hoverinfo='none'))
        colors = [colors_araucania[i] if region == 'La Araucanía' else colors_gray[i] for region in df_educ_sorted.index]
        fig_stack.add_trace(go.Bar(y=df_educ_sorted.index, x=df_educ_sorted[col], name=col, orientation='h', marker_color=colors, marker_line_color='white', marker_line_width=0.5, showlegend=False))
        
    fig_stack.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', xaxis_title="Porcentaje (%)", yaxis_title="", legend_title="Nivel")
    fig_stack.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    fig_stack.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
    return fig_stack


m1, m2, m3 = st.columns(3)
m1.metric("Pobreza La Araucanía", f"{kpis['pobreza_araucania']}%", f"+{round(kpis['pobreza_araucania'] - kpis['pobreza_nacional'], 1)}% vs Nacional", delta_color="inverse")
m2.metric("Ruralidad La Araucanía", f"{kpis['ruralidad_araucania']}%", "Mayor concentración del país")
m3.metric("Autocorrelación Espacial", f"I = {kpis['moran_i']}", f"p-value: {kpis['moran_p']} (Clustering)", delta_color="off", help="El Índice positivo confirma un clustering significativo.")

st.divider()

tab_inicio, tab1, tab2, tab3 = st.tabs(["🏠 Inicio (La Historia)", "📍 1. Geografía de la Pobreza", "📉 2. Carencias y Demografía", "🎓 3. Ciclo de Vida y Educación"])

# ----------------- PESTAÑA INICIO (STORYTELLING) -----------------
with tab_inicio:
    import sys, importlib
    import storytelling_html
    importlib.reload(storytelling_html)
    from storytelling_html import get_d3_map, get_chartjs_scatter, get_chartjs_educ, get_chartjs_line, get_chartjs_radar
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>El Fenómeno de La Araucanía: Un viaje a través de los datos</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    @keyframes slideInLeft { from { opacity: 0; transform: translateX(-50px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(50px); } to { opacity: 1; transform: translateX(0); } }
    .story-card-right { animation: slideInRight 1s ease-out 0.4s both; }
    .story-card-left { animation: slideInLeft 1s ease-out 0.4s both; }
    
    .story-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        border-left: 6px solid #8F3A2F;
        margin-top: 20px;
    }
    .story-card h3 { color: #8F3A2F; font-size: 26px; margin-top:0; font-weight: 700; }
    .story-card p { font-size: 18px; line-height: 1.6; color: #555; }
    </style>
    """, unsafe_allow_html=True)
    
    # Capítulo 1
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('''
        <style>
        .colorbar-overlay {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(5px);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            z-index: 99;
        }
        .colorbar-title { font-weight: 700; margin-bottom: 12px; font-size: 16px; color: #4A4A4A; }
        .colorbar { width: 25px; height: 180px; border-radius: 4px; background: linear-gradient(to bottom, #8F3A2F, #F3C8C2, #FAF5F0); }
        .colorbar-labels { position: absolute; left: 55px; top: 45px; height: 180px; display: flex; flex-direction: column; justify-content: space-between; font-size: 14px; font-weight: 600; color: #4A4A4A; }
        </style>
        <div class="story-img-left" style="position: relative;">
            <div class="colorbar-overlay">
                <div class="colorbar-title">Tasa de Pobreza</div>
                <div class="colorbar"></div>
                <div class="colorbar-labels">
                    <span>28%</span>
                    <span></span>
                    <span>10%</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('<div class="story-img-left">', unsafe_allow_html=True)
        st.image(str(DATA_DIR / "map_story_transparent.png"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('''<div class="story-card story-card-right" style="margin-top: 150px;">
            <h3>1. El Mapa de la Desigualdad</h3>
            <p>Al observar el mapa de Chile continental, <b>La Araucanía</b> resalta vívidamente. Es la región con mayor incidencia de pobreza a nivel nacional. Pero, ¿por qué llegamos a esto? ¿Qué factores estructurales hacen que esta región se quede atrás?</p>
        </div>''', unsafe_allow_html=True)
        
    st.divider()
    
    # Capítulo 2
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('''<div class="story-card story-card-left">
            <h3>2. Geografía e Historia</h3>
            <p>La Araucanía no solo es la más pobre, sino también <b>la más rural</b>. Existe una correlación directa entre la ruralidad y la pobreza. Además, concentra más del 54% de <b>población indígena</b> en sus zonas rurales, evidenciando un factor histórico de marginación.</p>
        </div>''', unsafe_allow_html=True)
    with c2:
        components.html(get_chartjs_scatter(scatter_df.to_dict(orient='records')), height=600, scrolling=False)
        
    st.divider()
    
    # Capítulo 3
    c1, c2 = st.columns([1.2, 1])
    with c1:
        components.html(get_chartjs_educ(df_educ.reset_index().to_dict(orient='records')), height=600, scrolling=False)
    with c2:
        st.markdown('''<div class="story-card story-card-right">
            <h3>3. El Rezago Educativo</h3>
            <p>Esta ruralidad se traduce en un acceso deficiente a oportunidades. Hoy, La Araucanía lidera tristemente como la región con <b>mayor población adulta cuyo nivel educativo máximo es la básica</b>. Sin una base sólida, la inserción en la economía formal es muy compleja.</p>
        </div>''', unsafe_allow_html=True)

    st.divider()

    # Capítulo 4
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('''<div class="story-card story-card-left">
            <h3>4. Ingresos Estancados</h3>
            <p>Sin acceso a especialización, los ingresos de las personas crecen muy poco durante su vida. A diferencia de otras regiones, en La Araucanía <b>los ingresos se estancan drásticamente a los 35 años</b>.</p>
        </div>''', unsafe_allow_html=True)
    with c2:
        components.html(get_chartjs_line(df_growth.to_dict(orient='records')), height=600, scrolling=False)

    st.divider()

    # Capítulo 5
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<div class="story-img-left">', unsafe_allow_html=True)
        st.plotly_chart(create_radar(), use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('''<div class="story-card story-card-right">
            <h3>5. Crisis Multidimensional</h3>
            <p>La pobreza monetaria es solo la punta del iceberg. Al analizar otras carencias, La Araucanía presenta una brecha alarmante frente al promedio nacional, viéndose sumamente afectada en años de <b>Escolaridad</b>, falta de <b>Conectividad</b> y un grave <b>Déficit cualitativo de la vivienda</b>. Factores que en conjunto perpetúan el ciclo de vulnerabilidad.</p>
        </div>''', unsafe_allow_html=True)
        
    st.divider()

    # Conclusion
    st.markdown('''
        <div class="story-card" style="border-left: none; border-top: 6px solid #8F3A2F; margin: 40px auto; max-width: 800px; text-align: center;">
            <h3>En Conclusión</h3>
            <p>La extensa ruralidad y composición histórica han alejado las oportunidades, originando un rezago educacional profundo que estanca el crecimiento económico a temprana edad. Romper este ciclo requiere intervenciones estructurales y focalizadas del Estado.</p>
        </div>
    ''', unsafe_allow_html=True)

# ----------------- PESTAÑAS ORIGINALES (EXPLORACIÓN PLOTLY) -----------------
with tab1:
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("Tasa de pobreza por región")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        st.plotly_chart(create_map(), use_container_width=True)
        st.info("💡 **Interpretación:** La Araucanía destaca nítidamente con la mayor incidencia de pobreza a nivel nacional.")

    with col2:
        r_val = scatter_df['Ruralidad'].corr(scatter_df['Pobreza'])
        st.subheader(f"Ruralidad vs Pobreza (r = {r_val:.2f})")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        st.plotly_chart(create_scatter(), use_container_width=True)
        st.info("💡 **Interpretación:** Existe una clara correlación positiva entre la ruralidad y la pobreza.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Carencias Multidimensionales")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        st.plotly_chart(create_radar(), use_container_width=True)
        st.info("💡 **Interpretación:** La región presenta profundas brechas frente al promedio nacional, siendo críticas las carencias en Escolaridad, Informalidad y Conectividad.")

    with col2:
        st.subheader("Proporción de Población Indígena")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        st.plotly_chart(create_bar(), use_container_width=True)
        st.info("💡 **Interpretación:** La Araucanía concentra una proporción significativamente mayor de población indígena que el resto de Chile, superando el 54% en zonas rurales.")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Crecimiento de ingresos en el ciclo de vida")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        st.plotly_chart(create_line(), use_container_width=True)
        st.info("💡 **Interpretación:** A diferencia de la R. Metropolitana y el resto de Chile, los ingresos en La Araucanía se estancan rápidamente después de los 35 años.")

    with col2:
        st.subheader("Nivel Educacional (Población >25 años)")
        st.caption("Fuente: Censo 2024 (N=18.480.432)")
        st.plotly_chart(create_stack(), use_container_width=True)
        st.info("💡 **Interpretación:** Existe un grave rezago educativo histórico. La Araucanía es la región con el mayor porcentaje de población adulta con educación básica o menos.")

st.divider()
st.caption("Nota: Todas las métricas de CASEN utilizan el factor de expansión poblacional para evitar sesgos muestrales.")
