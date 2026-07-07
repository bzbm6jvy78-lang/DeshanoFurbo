import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import requests
import re
import json

st.set_page_config(page_title="Analizador Automático de WhoScored", layout="wide")

st.title("📊 Extractor y Analizador de Partidos de WhoScored")
st.write("Introduce el enlace del partido de WhoScored y la app dibujará todos los eventos automáticamente.")

# --- CONTROLES LATERALES ---
st.sidebar.header("Configuración del Gráfico")
url_input = st.sidebar.text_input(
    "Enlace del partido de WhoScored:", 
    placeholder="https://www.whoscored.com/Matches/..."
)
event_filter = st.sidebar.selectbox("Filtrar por tipo de acción:", ["Todos los eventos", "Pases", "Tiros", "Faltas", "Recuperaciones"])
line_color = st.sidebar.color_picker("Color de los puntos", "#00FFCC")
marker_size = st.sidebar.slider("Tamaño de los puntos", 100, 500, 250)

# --- FUNCIÓN PARA RASPAR LA URL ---
def obtener_datos_whoscored(url):
    try:
        # Simulamos un navegador real para que WhoScored no nos bloquee
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"No se pudo acceder a la página (Código de error: {response.status_code})")
            return None
        
        # Buscamos la variable matchCentreData que contiene todos los eventos del partido
        match = re.search(r"matchCentreData\s*=\s*({.*?});", response.text)
        if match:
            json_data = match.group(1)
            return json.loads(json_data)
        else:
            st.error("No se encontraron datos de eventos en este enlace. Asegúrate de que es un partido finalizado o en directo de WhoScored.")
            return None
    except Exception as e:
        st.error(f"Error al conectar con WhoScored: {e}")
        return None

# --- PROCESAMIENTO Y DIBUJO ---
events_to_plot = []
home_team = "Equipo Local"
away_team = "Equipo Visitante"

if url_input:
    with st.spinner("Extrayendo datos de WhoScored..."):
        data = obtener_datos_whoscored(url_input)
        
        if data:
            home_team = data.get('home', {}).get('name', 'Local')
            away_team = data.get('away', {}).get('name', 'Visitante')
            
            # Extraemos la lista de eventos del partido
            all_events = data.get('events', [])
            
            for ev in all_events:
                if 'x' in ev and 'y' in ev:
                    # Filtrado básico por tipo de evento
                    tipo = ev.get('type', {}).get('displayName', '')
                    
                    if event_filter == "Todos los eventos":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Pases" and tipo == "Pass":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Tiros" and tipo == "SavedShot" or tipo == "MissedShots" or tipo == "Goal":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Faltas" and tipo == "Foul":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Recuperaciones" and tipo == "Tackle" or tipo == "Interception":
                        events_to_plot.append((ev['x'], ev['y']))

            st.success(f"¡Éxito! Se han cargado {len(events_to_plot)} eventos de tipo '{event_filter}'.")

# --- DISEÑO DEL CAMPO DE FÚTBOL ---
pitch = Pitch(pitch_type='opta', pitch_color='#0e1117', line_color='#444444', goal_type='line')
fig, ax = pitch.draw(figsize=(11, 8))

# Pintar las coordenadas extraídas si existen
if events_to_plot:
    for x, y in events_to_plot:
        pitch.scatter(x, y, ax=ax, s=marker_size, color=line_color, edgecolors='white', linewidth=1, alpha=0.7, zorder=3)

# Títulos del gráfico automatizados con los nombres reales de los equipos
fig.text(0.5, 0.94, f"{home_team} vs {away_team}", size=22, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, f"Mapa de acciones: {event_filter}", size=14, color='#888888', ha='center')
fig.text(0.5, 0.04, "Gráfico generado automáticamente | Datos extraídos de WhoScored", size=10, color='#666666', ha='center')

# Mostrar en Streamlit
st.pyplot(fig)

# --- BOTÓN DE DESCARGA ---
if events_to_plot:
    fig.savefig("mapa_autowhoscored.png", bbox_inches='tight', dpi=300, facecolor='#0e1117')
    with open("mapa_autowhoscored.png", "rb") as file:
        st.download_button(
            label="💾 Descargar Gráfico para Redes Sociales",
            data=file,
            file_name=f"mapa_{home_team.lower()}_vs_{away_team.lower()}.png",
            mime="image/png"
        )
