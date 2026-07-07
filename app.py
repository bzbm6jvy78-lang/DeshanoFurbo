import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import re
import json

st.set_page_config(page_title="Analizador Táctico Antí-Bloqueo", layout="wide")

st.title("📊 Extractor de Eventos por Jugador - WhoScored")
st.write("Esquiva las restricciones de Cloudflare pegando el código fuente del partido.")

# --- BARRA LATERAL ---
st.sidebar.header("1. Datos del Partido")

# Cuadro para pegar el código fuente directamente
html_paste = st.sidebar.text_area(
    "Pega aquí el código fuente (Ctrl+U / Cmd+U):", 
    height=150,
    placeholder="Pega todo el texto copiado de la pestaña del código fuente..."
)

# --- PROCESAMIENTO DE DATOS LOCAL (SIN BLOQUEOS DE RED) ---
match_data = None
lista_jugadores = {}
player_selected_id = None

if html_paste:
    # Buscamos la variable matchCentreData directamente en el texto pegado
    match = re.search(r"matchCentreData\s*=\s*({.*?});", html_paste)
    if match:
        try:
            match_data = json.loads(match.group(1))
            st.sidebar.success("¡Datos del partido procesados correctamente!")
        except Exception as e:
            st.sidebar.error(f"Error al procesar el formato de los datos: {e}")
    else:
        st.sidebar.error("No se encontró la variable 'matchCentreData'. Asegúrate de haber copiado todo el código fuente de la página correcta.")

if match_data:
    for team in ['home', 'away']:
        players = match_data.get(team, {}).get('players', [])
        for p in players:
            p_id = p.get('playerId')
            p_name = p.get('name')
            if p_id and p_name:
                lista_jugadores[p_name] = p_id

# --- CONTROLES DE FILTRADO ---
st.sidebar.header("2. Filtros del Mapa")
if lista_jugadores:
    nombres_ordenados = sorted(list(lista_jugadores.keys()))
    player_selected_name = st.sidebar.selectbox("Selecciona un Jugador:", nombres_ordenados)
    player_selected_id = lista_jugadores[player_selected_name]
else:
    st.sidebar.warning("Sigue las instrucciones de abajo para cargar los jugadores.")
    player_selected_name = "Jugador"

event_filter = st.sidebar.selectbox("Acción táctica:", ["Todos los eventos", "Pases", "Tiros", "Recuperaciones (Entradas/Intercepciones)"])
tipo_grafico = st.sidebar.selectbox("Tipo de visualización:", ["Mapa de Puntos", "Mapa de Calor"])
line_color = st.sidebar.color_picker("Color del elemento", "#00FFCC")

# --- FILTRAR EVENTOS DEL JUGADOR ---
events_to_plot = []

if match_data and player_selected_id:
    all_events = match_data.get('events', [])
    for ev in all_events:
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

fig.text(0.5, 0.94, player_selected_name, size=24, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, f"Mapa de acciones: {event_filter}", size=14, color='#888888', ha='center')

st.pyplot(fig)

# --- INSTRUCCIONES EN PANTALLA PRINCIPAL ---
if not html_paste:
    st.info("""
    ### 📖 Cómo usar la app en 10 segundos:
    1. Abre el partido que quieras en **WhoScored** desde tu navegador.
    2. Pulsa **`Ctrl + U`** (en Windows) o **`Cmd + Option + U`** (en Mac). Se abrirá una pestaña nueva llena de código de texto.
    3. Pulsa **`Ctrl + A`** (o `Cmd + A`) para seleccionar todo ese texto y **cópialo**.
    4. Pégalo en la caja grande de la barra lateral de esta app.
    
    ¡Listo! Al momento aparecerá el desplegable con todos los jugadores del partido sin sufrir bloqueos de Cloudflare.
    """)
