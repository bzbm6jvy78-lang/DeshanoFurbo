import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import cloudscraper
import re
import json

st.set_page_config(page_title="Analizador Táctico de WhoScored", layout="wide")

st.title("📊 Extractor de Eventos mediante URL de WhoScored")
st.write("Introduce el enlace de un partido finalizado para procesar la base de datos de eventos.")

# --- BARRA LATERAL ---
st.sidebar.header("Filtros y Estilo")
url_input = st.sidebar.text_input(
    "URL del Partido:", 
    placeholder="https://www.whoscored.com/Matches/..."
)

tipo_grafico = st.sidebar.selectbox("Tipo de visualización:", ["Mapa de Puntos", "Mapa de Calor"])
event_filter = st.sidebar.selectbox("Acción táctica:", ["Todos los eventos", "Pases", "Tiros", "Recuperaciones (Entradas/Intercepciones)"])
line_color = st.sidebar.color_picker("Color del elemento", "#00FFCC")

# --- BACKEND: EXTRACCIÓN SIN BLOQUEO ---
def scraping_whoscored(url):
    try:
        # Creamos un scraper que hereda características de evasión de bloqueos
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        response = scraper.get(url)
        
        if response.status_code == 403:
            st.error("❌ WhoScored ha bloqueado la petición automática (Error 403 - Cloudflare). Las IPs públicas de Streamlit suelen estar en lista negra.")
            return None
            
        if response.status_code != 200:
            st.error(f"Error de conexión: Código {response.status_code}")
            return None
            
        # Extraer la variable que aloja el JSON del partido
        match = re.search(r"matchCentreData\s*=\s*({.*?});", response.text)
        if match:
            return json.loads(match.group(1))
        else:
            st.error("No se pudo localizar la estructura 'matchCentreData' en el HTML. Verifica que sea un partido con estadísticas completas.")
            return None
            
    except Exception as e:
        st.error(f"Fallo en el proceso de extracción: {e}")
        return None

# --- PROCESADO DE LAS COORDENADAS OPTA ---
events_to_plot = []
title_home, title_away = "Local", "Visitante"

if url_input:
    with st.spinner("Conectando con el servidor de WhoScored..."):
        match_data = scraping_whoscored(url_input)
        
        if match_data:
            title_home = match_data.get('home', {}).get('name', 'Local')
            title_away = match_data.get('away', {}).get('name', 'Visitante')
            all_events = match_data.get('events', [])
            
            for ev in all_events:
                if 'x' in ev and 'y' in ev:
                    tipo_nombre = ev.get('type', {}).get('displayName', '')
                    
                    # Clasificación por tipos según la nomenclatura de WhoScored
                    if event_filter == "Todos los eventos":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Pases" and tipo_nombre == "Pass":
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Tiros" and tipo_nombre in ["SavedShot", "MissedShots", "Goal"]:
                        events_to_plot.append((ev['x'], ev['y']))
                    elif event_filter == "Recuperaciones (Entradas/Intercepciones)" and tipo_nombre in ["Tackle", "Interception"]:
                        events_to_plot.append((ev['x'], ev['y']))

            st.success(f"Datos procesados correctamente. Se encontraron {len(events_to_plot)} eventos.")

# --- RENDERIZADO DEL GRÁFICO ---
# Usamos las dimensiones nativas de Opta (100x100)
pitch = Pitch(pitch_type='opta', pitch_color='#0e1117', line_color='#444444', goal_type='line')
fig, ax = pitch.draw(figsize=(12, 9))

if events_to_plot:
    x_coords, y_coords = zip(*events_to_plot)
    
    if tipo_grafico == "Mapa de Puntos":
        pitch.scatter(x_coords, y_coords, ax=ax, s=250, color=line_color, edgecolors='white', linewidth=1, alpha=0.7, zorder=3)
    elif tipo_grafico == "Mapa de Calor":
        # Genera una densidad de puntos estilizada sobre el lienzo oscuro
        import seaborn as sns
        sns.kdeplot(x=x_coords, y=y_coords, ax=ax, fill=True, cmap="mako", alpha=0.5, thresh=0.05, levels=100, zorder=2)

# Estética de cabeceras
fig.text(0.5, 0.94, f"{title_home} vs {title_away}", size=24, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, f"Mapeo de eventos: {event_filter}", size=14, color='#888888', ha='center')

st.pyplot(fig)
