import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

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
    /* Background and global fonts */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {COLOR_DARK} !important;
        font-weight: 700 !important;
    }}
    
    /* Metrics Cards */
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        border-left: 5px solid {COLOR_DARK};
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 10px 10px 0px 0px;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.02);
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_LIGHTEST};
        color: {COLOR_DARK} !important;
        border-bottom: 3px solid {COLOR_DARK};
    }}
    
    /* Plotly containers shadow */
    [data-testid="stPlotlyChart"] {{
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Radiografía a la Araucanía: Factores Críticos de la Pobreza")
st.markdown("Un análisis profundo de la brecha territorial, económica y educacional.")
st.divider()

@st.cache_data
def load_data():
    DATA_DIR = Path("dashboard_data")
    
    with open(DATA_DIR / "kpis.json", "r", encoding="utf-8") as f:
        kpis = json.load(f)
        
    gdf = gpd.read_file(DATA_DIR / "mapa_pobreza.geojson")
    scatter_df = pd.read_csv(DATA_DIR / "scatter.csv")
    df_indig = pd.read_csv(DATA_DIR / "indigena.csv")
    df_radar = pd.read_csv(DATA_DIR / "radar.csv")
    df_growth = pd.read_csv(DATA_DIR / "ingresos_edad.csv")
    df_educ = pd.read_csv(DATA_DIR / "educacion.csv").set_index("region_nombre")
    
    return kpis, gdf, scatter_df, df_indig, df_radar, df_growth, df_educ

with st.spinner("Cargando dashboard..."):
    kpis, gdf, scatter_df, df_indig, df_radar, df_growth, df_educ = load_data()

# --- KPIs SUPERIORES ---
m1, m2, m3 = st.columns(3)
m1.metric("Pobreza La Araucanía", f"{kpis['pobreza_araucania']}%", f"+{round(kpis['pobreza_araucania'] - kpis['pobreza_nacional'], 1)}% vs Nacional", delta_color="inverse")
m2.metric("Ruralidad La Araucanía", f"{kpis['ruralidad_araucania']}%", "Mayor concentración del país")
m3.metric("Autocorrelación Espacial", f"I = {kpis['moran_i']}", f"p-value: {kpis['moran_p']} (Clustering)", delta_color="off")

st.divider()

# --- LAYOUT DE TABS ---
tab1, tab2, tab3 = st.tabs(["1. Geografía de la Pobreza", "2. Carencias y Demografía", "3. Ciclo de Vida y Educación"])

with tab1:
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("Tasa de pobreza por región")
        # Mapa
        fig_map = px.choropleth(
            gdf,
            geojson=gdf.geometry,
            locations=gdf.index,
            color="pobreza",
            hover_name="Region",
            hover_data={"pobreza": True},
            color_continuous_scale=[BACKGROUND_COLOR, COLOR_LIGHTEST, COLOR_DARK],
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, width='stretch')

    with col2:
        r_val = scatter_df['Ruralidad'].corr(scatter_df['Pobreza'])
        st.subheader(f"Ruralidad vs Pobreza (r = {r_val:.2f})")
        
        fig_scatter = px.scatter(
            scatter_df, x="Ruralidad", y="Pobreza", color="Region", text="Region",
            hover_name="Region",
            color_discrete_map={r: COLOR_DARK if r == 'La Araucanía' else GRAY_LIGHT for r in scatter_df['Region']}
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=1, color='White')))
        fig_scatter.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  xaxis_title="Población Rural (%)", yaxis_title="Tasa de Pobreza (%)")
        st.plotly_chart(fig_scatter, width='stretch')

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Carencias Multidimensionales")
        # Radar
        radar_labels = df_radar['Indicador'].tolist()
        radar_araucania = df_radar['La Araucanía'].tolist()
        radar_chile = df_radar['Chile'].tolist()
        
        df_radar_plot = pd.DataFrame({
            'r': radar_araucania + radar_chile,
            'theta': radar_labels + radar_labels,
            'Area': ['La Araucanía']*len(radar_labels) + ['Chile']*len(radar_labels)
        })
        fig_radar = px.line_polar(df_radar_plot, r='r', theta='theta', color='Area', line_close=True,
                                  color_discrete_map={'La Araucanía': COLOR_DARK, 'Chile': GRAY_MED})
        fig_radar.update_traces(fill='toself', hovertemplate="%{theta}: %{r:.1f}%")
        fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_DARK)
        st.plotly_chart(fig_radar, width='stretch')

    with col2:
        st.subheader("Proporción de Población Indígena")
        fig_bar = px.bar(df_indig, x="Valor", y="Zona", color="Area", barmode="group", orientation='h',
                         color_discrete_map={'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT},
                         text_auto='.1f')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_DARK,
                              xaxis_title="Porcentaje (%)", yaxis_title="")
        st.plotly_chart(fig_bar, width='stretch')

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Crecimiento de ingresos en el ciclo de vida")
        fig_line = px.line(df_growth, x="Edad", y="Ingreso", color="Región", markers=True,
                           color_discrete_map={'Metropolitana': GRAY_DARK, 'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
        fig_line.update_traces(hovertemplate="Rango de edad: %{x}<br>Ingreso: $%{y:,.0f}")
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               yaxis_title="Ingreso per cápita ($)")
        st.plotly_chart(fig_line, width='stretch')

    with col2:
        st.subheader("Nivel Educacional (Población >25 años)")
        fig_stack = px.bar(df_educ, x=df_educ.columns, y=df_educ.index, orientation='h',
                           color_discrete_sequence=[COLOR_DARK, COLOR_MED, GRAY_LIGHT, GRAY_LIGHTEST])
        fig_stack.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                xaxis_title="Porcentaje (%)", yaxis_title="",
                                legend_title="Nivel", barmode='stack')
        st.plotly_chart(fig_stack, width='stretch')

st.divider()
st.markdown("""
<div style="text-align: center; color: #777; font-size: 0.85em;">
    <b>Notas Técnicas</b><br>
    • <b>Representatividad (Ponderador):</b> Todas las métricas de CASEN utilizan el factor de expansión poblacional para evitar sesgos muestrales.<br>
    • <b>Autocorrelación Espacial:</b> El Índice positivo confirma un clustering significativo, evidenciando que la pobreza no es un caso aislado sino un bloque concentrado en la macro-zona sur.<br>
    • <b>Ingresos del Ciclo Vital:</b> La curva 'Chile' excluye a La Araucanía y a la Región Metropolitana para permitir una comparación aislada frente a los extremos socioeconómicos del país.
</div>
""", unsafe_allow_html=True)
