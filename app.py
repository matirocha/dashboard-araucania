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
m3.metric("Autocorrelación Espacial", f"I = {kpis['moran_i']}", f"p-value: {kpis['moran_p']} (Clustering)", delta_color="off", help="El Índice positivo confirma un clustering significativo, evidenciando que la pobreza no es un caso aislado sino un bloque concentrado en la macro-zona sur.")

st.divider()

# --- LAYOUT DE TABS ---
tab1, tab2, tab3 = st.tabs(["1. Geografía de la Pobreza", "2. Carencias y Demografía", "3. Ciclo de Vida y Educación"])

with tab1:
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("Tasa de pobreza por región")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
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
        st.info("💡 **Interpretación:** La Araucanía destaca nítidamente con la mayor incidencia de pobreza a nivel nacional, superando ampliamente al resto de las regiones.")

    with col2:
        r_val = scatter_df['Ruralidad'].corr(scatter_df['Pobreza'])
        st.subheader(f"Ruralidad vs Pobreza (r = {r_val:.2f})")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        
        fig_scatter = px.scatter(
            scatter_df, x="Ruralidad", y="Pobreza", color="Region", text="Region",
            hover_name="Region",
            color_discrete_map={r: COLOR_DARK if r == 'La Araucanía' else GRAY_LIGHT for r in scatter_df['Region']}
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=1, color='White')))
        fig_scatter.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  xaxis_title="Población Rural (%)", yaxis_title="Tasa de Pobreza (%)")
        st.plotly_chart(fig_scatter, width='stretch')
        st.info("💡 **Interpretación:** Existe una clara correlación positiva entre la ruralidad y la pobreza. La Araucanía se posiciona como un caso extremo en ambos factores.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Carencias Multidimensionales")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        # Radar
        radar_labels = df_radar['Indicador'].tolist()
        radar_araucania = df_radar['La Araucanía'].tolist()
        radar_chile = df_radar['Chile'].tolist()
        
        radar_labels_c = radar_labels + [radar_labels[0]]
        radar_araucania_c = radar_araucania + [radar_araucania[0]]
        radar_chile_c = radar_chile + [radar_chile[0]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_chile_c, theta=radar_labels_c, mode='lines+markers',
            line_color=GRAY_MED, fill='toself', fillcolor='rgba(119, 119, 119, 0.1)', name='Chile'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_araucania_c, theta=radar_labels_c, mode='lines+markers',
            line_color=COLOR_DARK, fill='toself', fillcolor='rgba(143, 58, 47, 0.2)', name='La Araucanía'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, gridcolor='#DDDDDD', linecolor='#CCCCCC'),
                angularaxis=dict(gridcolor='#DDDDDD', linecolor='#CCCCCC', direction='clockwise', rotation=90)
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_DARK,
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_radar, width='stretch')
        st.info("💡 **Interpretación:** La región presenta profundas brechas frente al promedio nacional, siendo críticas las carencias en Escolaridad, Informalidad y Conectividad.")

    with col2:
        st.subheader("Proporción de Población Indígena")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        fig_bar = px.bar(df_indig, x="Valor", y="Zona", color="Area", barmode="group", orientation='h',
                         color_discrete_map={'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
        fig_bar.update_traces(texttemplate='%{x:.1f}%', textposition='outside', cliponaxis=False)
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_DARK,
                              xaxis_title="Porcentaje (%)", yaxis_title="")
        st.plotly_chart(fig_bar, width='stretch')
        st.info("💡 **Interpretación:** La Araucanía concentra una proporción significativamente mayor de población indígena que el resto de Chile, superando el 54% en zonas rurales.")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Crecimiento de ingresos en el ciclo de vida")
        st.caption("Fuente: Encuesta CASEN 2024 (N=218.367)")
        df_growth_plot = df_growth.copy()
        df_growth_plot["Ingreso"] = df_growth_plot["Ingreso"] / 1000
        fig_line = px.line(df_growth_plot, x="Edad", y="Ingreso", color="Región", markers=True,
                           color_discrete_map={'Metropolitana': GRAY_DARK, 'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
        fig_line.update_traces(hovertemplate="Rango de edad: %{x}<br>Ingreso: $%{y:,.0f} mil")
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               yaxis_title="Ingreso per cápita (miles de $)")
        st.plotly_chart(fig_line, width='stretch')
        st.info("💡 **Interpretación:** A diferencia de la R. Metropolitana y el resto de Chile, los ingresos en La Araucanía se estancan rápidamente después de los 35 años.")
        st.caption("Nota: La curva 'Chile' excluye a La Araucanía y a la Región Metropolitana para permitir una comparación aislada frente a los extremos socioeconómicos del país.")

    with col2:
        st.subheader("Nivel Educacional (Población >25 años)")
        st.caption("Fuente: Censo 2024 (N=18.480.432)")
        
        df_educ = df_educ.sort_values(by="Básica o menos", ascending=True)
        educ_order = ["Básica o menos", "Media", "Técnica", "Universitaria"]
        colors_araucania = [COLOR_DARK, COLOR_MED, COLOR_LIGHT, COLOR_LIGHTEST]
        colors_gray = [GRAY_DARK, GRAY_MED, GRAY_LIGHT, GRAY_LIGHTEST]
        
        fig_stack = go.Figure()
        for i, col in enumerate(educ_order):
            # Trazo invisible solo para generar la leyenda con el color correcto
            fig_stack.add_trace(go.Bar(
                y=[df_educ.index[0]], x=[0], name=col, orientation='h',
                marker_color=colors_araucania[i], showlegend=True, hoverinfo='none'
            ))
            # Trazo real con los colores condicionales (array) ocultando su leyenda
            colors = [colors_araucania[i] if region == 'La Araucanía' else colors_gray[i] for region in df_educ.index]
            fig_stack.add_trace(go.Bar(
                y=df_educ.index, x=df_educ[col], name=col, orientation='h',
                marker_color=colors, marker_line_color='white', marker_line_width=0.5,
                showlegend=False
            ))
            
        fig_stack.update_layout(
            barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Porcentaje (%)", yaxis_title="", legend_title="Nivel"
        )
        st.plotly_chart(fig_stack, width='stretch')
        st.info("💡 **Interpretación:** Existe un grave rezago educativo histórico. La Araucanía es la región con el mayor porcentaje de población adulta con educación básica o menos.")

st.divider()
st.caption("Nota: Todas las métricas de CASEN utilizan el factor de expansión poblacional para evitar sesgos muestrales.")

