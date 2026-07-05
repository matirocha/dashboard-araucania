import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

DATA_DIR = Path("dashboard_data")

gdf = gpd.read_file(DATA_DIR / "mapa_pobreza.geojson").clip([-76.0, -60.0, -50.0, -15.0])
scatter_df = pd.read_csv(DATA_DIR / "scatter.csv")
df_indig = pd.read_csv(DATA_DIR / "indigena.csv")
df_radar = pd.read_csv(DATA_DIR / "radar.csv")
df_growth = pd.read_csv(DATA_DIR / "ingresos_edad.csv")
df_educ = pd.read_csv(DATA_DIR / "educacion.csv").set_index("region_nombre")

COLOR_DARK = "#8F3A2F"
COLOR_MED = "#B58C86"
COLOR_LIGHT = "#E9A097"
COLOR_LIGHTEST = "#F3C8C2"
GRAY_DARK = "#4A4A4A"
GRAY_MED = "#777777"
GRAY_LIGHT = "#A6A6A6"
GRAY_LIGHTEST = "#D9D9D9"
BACKGROUND_COLOR = "#FAF5F0"

print("Generando mapa...")
fig_map = px.choropleth(gdf, geojson=gdf.geometry, locations=gdf.index, color="pobreza", hover_name="Region", hover_data={"pobreza": True}, color_continuous_scale=[BACKGROUND_COLOR, COLOR_LIGHTEST, COLOR_DARK], labels={"pobreza": ""})
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_coloraxes(colorbar=dict(
    title=dict(text="Pobreza (%)", font=dict(size=16, color="#4A4A4A")),
    thickness=12,
    len=0.6,
    yanchor="middle", y=0.5,
    xanchor="left", x=0.05,
    tickfont=dict(size=14, color="#4A4A4A"),
    outlinewidth=0,
    bgcolor="rgba(255,255,255,0.5)"
))
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black')
fig_map.write_image(DATA_DIR / "map_story.png", width=700, height=1000, scale=2)

print("Generando scatter...")
fig_scatter = px.scatter(scatter_df, x="Ruralidad", y="Pobreza", color="Region", text="Region", hover_name="Region", color_discrete_map={r: COLOR_DARK if r == 'La Araucanía' else GRAY_LIGHT for r in scatter_df['Region']})
fig_scatter.update_traces(textposition='top center', textfont_color='black', marker=dict(size=12, line=dict(width=1, color='White')))
fig_scatter.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', xaxis_title="Población Rural (%)", yaxis_title="Tasa de Pobreza (%)")
fig_scatter.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"), gridcolor="rgba(0,0,0,0.1)")
fig_scatter.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"), gridcolor="rgba(0,0,0,0.1)")
fig_scatter.write_image(DATA_DIR / "scatter_story.png", width=800, height=500, scale=2)

print("Generando radar...")
radar_labels = df_radar['Indicador'].tolist()
radar_araucania = df_radar['La Araucanía'].tolist()
radar_chile = df_radar['Chile'].tolist()
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(r=radar_chile + [radar_chile[0]], theta=radar_labels + [radar_labels[0]], mode='lines+markers', line_color=GRAY_MED, fill='toself', fillcolor='rgba(119, 119, 119, 0.1)', name='Chile'))
fig_radar.add_trace(go.Scatterpolar(r=radar_araucania + [radar_araucania[0]], theta=radar_labels + [radar_labels[0]], mode='lines+markers', line_color=COLOR_DARK, fill='toself', fillcolor='rgba(143, 58, 47, 0.2)', name='La Araucanía'))
fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, gridcolor='#DDDDDD', linecolor='#CCCCCC'), angularaxis=dict(gridcolor='#DDDDDD', linecolor='#CCCCCC', direction='clockwise', rotation=90, tickfont=dict(color='black'))), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
fig_radar.write_image(DATA_DIR / "radar_story.png", width=700, height=500, scale=2)

print("Generando linea...")
df_growth_plot = df_growth.copy()
df_growth_plot["Ingreso"] = df_growth_plot["Ingreso"] / 1000
fig_line = px.line(df_growth_plot, x="Edad", y="Ingreso", color="Región", markers=True, color_discrete_map={'Metropolitana': GRAY_DARK, 'La Araucanía': COLOR_DARK, 'Chile': GRAY_LIGHT})
fig_line.update_traces(hovertemplate="Rango de edad: %{x}<br>Ingreso: $%{y:,.0f} mil")
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='black', yaxis_title="Ingreso per cápita (miles de $)")
fig_line.update_xaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
fig_line.update_yaxes(color="black", title_font=dict(color="black"), tickfont=dict(color="black"))
fig_line.write_image(DATA_DIR / "line_story.png", width=800, height=500, scale=2)

print("Generando stack...")
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
fig_stack.write_image(DATA_DIR / "educ_story.png", width=800, height=500, scale=2)

print("¡Imágenes generadas con éxito!")
