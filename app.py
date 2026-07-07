import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from soccerplots.radar_chart import Radar

# Configuración de la página web
st.set_page_config(page_title="Creador de Radares Pro", layout="centered")

st.title("📊 Creador de Gráficos de Radar de Fútbol")
st.write("Introduce los datos de tu jugador de WhoScored para generar un gráfico profesional.")

# --- SECCIÓN 1: DATOS BÁSICOS ---
st.subheader("1. Información del Jugador")
col1, col2 = st.columns(2)
with col1:
    player_name = st.text_input("Nombre del Jugador", "Vinícius Jr.")
with col2:
    season = st.text_input("Temporada / Competición", "LaLiga 2025/26")

# --- SECCIÓN 2: MÉTRICAS Y VALORES ---
st.subheader("2. Estadísticas (Elige 5 métricas de WhoScored)")
st.write("Introduce el nombre de la estadística y la puntuación/percentil del jugador (0 a 100).")

metrics = []
values = []

# Creamos 5 filas para introducir datos de forma cómoda
for i in range(1, 6):
    c1, c2 = st.columns([3, 1])
    with c1:
        met = st.text_input(f"Métrica {i}", value=f"Estadística {i}", key=f"met_{i}")
    with c2:
        val = st.number_input(f"Valor {i}", min_value=0, max_value=100, value=50 + i*5, key=f"val_{i}")
    metrics.append(met)
    values.append(val)

# --- SECCIÓN 3: PERSONALIZACIÓN ---
st.subheader("3. Estilo del Gráfico")
radar_color = st.color_picker("Color del Radar", "#00FFCC")

# --- GENERACIÓN DEL GRÁFICO ---
if st.button("✨ Generar Gráfico de Radar"):
    
    # Rangos para un radar basado en percentiles (0 a 100)
    ranges = [(0, 100) for _ in range(5)]
    
    # Configuración de colores estilo Twitter/X Analytics
    background_color = "#0e1117"
    text_color = "#FFFFFF"
    
    # Inicializar el radar
    radar = Radar(
        background_color=background_color,
        patch_color=background_color,
        label_color=text_color,
        range_color="#555555",
        label_size=12,
        range_size=9,
        num_rings=4,
        ring_color="#222222"
    )
    
    # Dibujar las líneas y rellenar con los datos
    fig, ax = radar.plot_radar(
        ranges=ranges,
        params=metrics,
        values=values,
        radar_color=[radar_color],
        alpha=[0.4]
    )
    
    # Añadir títulos
    fig.text(0.5, 0.95, player_name, size=22, color=text_color, ha="center", weight="bold")
    fig.text(0.5, 0.91, season, size=12, color="#888888", ha="center")
    fig.text(0.5, 0.05, "Datos: WhoScored | Creado con RadarApp", size=9, color="#555555", ha="center")
    
    # Mostrar en la web
    st.pyplot(fig)
    
    # Opción para descargar la imagen directamente
    fig.savefig("radar_player.png", bbox_inches='tight', dpi=300)
    with open("radar_player.png", "rb") as file:
        st.download_button(
            label="💾 Descargar Gráfico en Alta Calidad",
            data=file,
            file_name=f"radar_{player_name.lower().replace(' ', '_')}.png",
            mime="image/png"
        )
