import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import cloudscraper
import re
import json

st.set_page_config(page_title="Analizador Táctico de WhoScored", layout="wide")

st.title("📊 Extractor de Eventos por Jugador - WhoScored")
st.write("Introduce el enlace del partido, elige al jugador y genera su mapa de acciones individual.")

# --- BARRA LATERAL ---
st.sidebar.header("1. Enlace del Partido")
url_input = st.sidebar.text_input(
    "URL de WhoScored:", 
    placeholder="https://www.whoscored.com/Matches/..."
)

# --- BACKEND: EXTRACCIÓN DE DATOS ---
@st.cache_data(show_spinner=False)
def descargar_datos_partido(url):
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        response = scraper.get(url)
        if response.status_code != 200:
            return None
            
        match = re.search(r"matchCentreData\s*=\s*({.*?});", response.text)
        if match:
            return json.loads(match.group(1))
        return None
    except:
        return None

# --- PROCESAMIENTO DE JUGADORES Y EVENTOS ---
match_data = None
lista_jugadores = {}
player_selected_id = None

if url_input:
    match_data = descargar_datos_partido(url_input)
    
    if match_data:
        # Creamos un diccionario con el ID del jugador y su Nombre Real
        # WhoScored separa los jugadores por equipo local (home) y visitante (away)
        for team in ['home', 'away']:
            players = match_data.get(team, {}).get('players', [])
            for p in players:
                p_id = p.get('playerId')
                p_name = p.get('name')
                if p_id and p_name:
                    lista_jugadores[p_name] = p_id
                    
        st.sidebar.success("¡Datos del partido cargados con éxito!")
    else:
        st.sidebar.error("No se pudieron extraer los datos. Verifica el enlace o las restricciones de Cloudflare.")

# --- CONTROLES DE FILTRADO (Solo aparecen si hay datos) ---
st.sidebar.header("2. Filtros del Mapa")
if lista_jugadores:
    # Menú desplegable con los nombres ordenados alfabéticamente
    nombres_ordenados = sorted(list(lista_jugadores.keys()))
    player_selected_name = st.sidebar.selectbox("Selecciona un Jugador:", nombres_ordenados)
    player_selected_id = lista_jugadores[player_selected_name]
else:
    st.sidebar.warning("Introduce una URL válida para ver la lista de jugadores.")
    player_selected_name = "Jugador"

event_filter = st.sidebar.selectbox("Acción táctica:", ["Todos los eventos", "Pases", "Tiros", "Recuperaciones (Entradas/Intercepciones)"])
tipo_grafico = st.sidebar.selectbox("Tipo de visualización:", ["Mapa de Puntos", "Mapa de Calor"])
line_color = st.sidebar.color_picker("Color del elemento", "#00FFCC")

# --- FILTRAR EVENTOS DEL JUGADOR SELECCIONADO ---
events_to_plot = []

if match_data and player_selected_id:
    all_events = match_data.get('events', [])
    for ev in all_events:
        # Condición clave: Que el evento pertenezca al ID del jugador seleccionado
        if ev.get('playerId') == player_selected_id and 'x' in ev and 'y' in ev:
            tipo_nombre = ev.get('type', {}).get('displayName', '')
            
            if event_filter == "Todos los eventos":
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Pases" and tipo_nombre == "Pass":
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Tiros" and tipo_nombre in ["SavedShot", "MissedShots", "Goal"]:
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Recuperaciones (Entradas/Intercepciones)" and tipo_nombre in ["Tackle", "Interception"]:
                events_to_plot.append((ev['x'], ev['y']))

# --- RENDERIZADO DEL CAMPO ---
pitch = Pitch(pitch_type='opta', pitch_color='#0e1117', line_color='#444444', goal_type='line')
fig, ax = pitch.draw(figsize=(12, 9))

if events_to_plot:
    x_coords, y_coords = zip(*events_to_plot)
    if tipo_grafico == "Mapa de Puntos":
        pitch.scatter(x_coords, y_coords, ax=ax, s=250, color=line_color, edgecolors='white', linewidth=1, alpha=0.8, zorder=3)
    elif tipo_grafico == "Mapa de Calor":
        import seaborn as sns
        sns.kdeplot(x=x_coords, y=y_coords, ax=ax, fill=True, cmap="mako", alpha=0.5, thresh=0.05, levels=100, zorder=2)
    st.info(f"Mostrando {len(events_to_plot)} acciones de {player_selected_name}.")
elif url_input and match_data:
    st.warning(f"No se encontraron eventos de tipo '{event_filter}' para {player_selected_name} en este partido.")

# Títulos dinámicos con el nombre del futbolista elegido
fig.text(0.5, 0.94, player_name_title := player_selected_name, size=24, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, f"Mapa de acciones: {event_filter}", size=14, color='#888888', ha='center')

st.pyplot(fig)
