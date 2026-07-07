import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import json

st.set_page_config(page_title="Analizador Opta Pro", layout="wide")

st.title("📊 Extractor Táctico Opta (WhoScored)")
st.write("Pega el JSON de la API obtenido en la pestaña Chalkboard.")

# --- BARRA LATERAL ---
st.sidebar.header("1. Carga de Datos")
json_paste = st.sidebar.text_area("Pega aquí el JSON completo:", height=150)

match_data = None
lista_jugadores = {}
player_selected_id = None

if json_paste:
    try:
        match_data = json.loads(json_paste)
        st.sidebar.success("¡Datos cargados correctamente!")
    except Exception as e:
        st.sidebar.error(f"Error en el formato del texto: {e}")

if match_data:
    # Mapear los nombres de los jugadores de ambos equipos
    for team_key in ['home', 'away']:
        players = match_data.get(team_key, {}).get('players', [])
        for p in players:
            p_id = p.get('playerId')
            p_name = p.get('name')
            if p_id and p_name:
                lista_jugadores[p_name] = p_id

# --- FILTROS DE INTERFAZ ---
st.sidebar.header("2. Opciones de Filtrado")
if lista_jugadores:
    nombres_ordenados = sorted(list(lista_jugadores.keys()))
    player_selected_name = st.sidebar.selectbox("Selecciona un Jugador:", nombres_ordenados)
    player_selected_id = lista_jugadores[player_selected_name]
else:
    st.sidebar.warning("Esperando datos válidos...")
    player_selected_name = "Jugador"

event_filter = st.sidebar.selectbox(
    "Filtro de acciones:", 
    ["Todos los eventos", "Pases Completados", "Pases Fallados", "Tiros a puerta", "Recuperaciones"]
)
line_color = st.sidebar.color_picker("Color de visualización", "#00FFCC")

# --- PROCESAR COORDENADAS ---
events_to_plot = []

if match_data and player_selected_id:
    all_events = match_data.get('events', [])
    for ev in all_events:
        if ev.get('playerId') == player_selected_id and 'x' in ev and 'y' in ev:
            # Identificadores estándar de Opta
            tipo = ev.get('type', {}).get('displayName', '')
            outcome = ev.get('outcomeType', {}).get('displayName', 'Successful')
            
            if event_filter == "Todos los eventos":
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Pases Completados" and tipo == "Pass" and outcome == "Successful":
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Pases Fallados" and tipo == "Pass" and outcome == "Unsuccessful":
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Tiros a puerta" and tipo in ["SavedShot", "MissedShots", "Goal"]:
                events_to_plot.append((ev['x'], ev['y']))
            elif event_filter == "Recuperaciones" and tipo in ["Tackle", "Interception"]:
                events_to_plot.append((ev['x'], ev['y']))

# --- DIBUJAR CAMPO ---
pitch = Pitch(pitch_type='opta', pitch_color='#0e1117', line_color='#444444', goal_type='line')
fig, ax = pitch.draw(figsize=(11, 8))

if events_to_plot:
    x_coords, y_coords = zip(*events_to_plot)
    pitch.scatter(x_coords, y_coords, ax=ax, s=250, color=line_color, edgecolors='white', linewidth=1.2, alpha=0.8, zorder=3)
    st.info(f"Mostrando {len(events_to_plot)} acciones registradas para {player_selected_name}.")

fig.text(0.5, 0.94, player_selected_name, size=24, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, f"Mapeo Opta: {event_filter}", size=14, color='#888888', ha='center')

st.pyplot(fig)
