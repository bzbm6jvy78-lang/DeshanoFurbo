import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd

st.set_page_config(page_title="Analizador de Partidos", layout="wide")

st.title("⚽ Creador de Mapas de Eventos por Partido")
st.write("Haz clic en el campo para añadir las acciones del partido (pases, tiros, etc.)")

# Inicializar la lista de eventos en la sesión si no existe
if 'events' not in st.session_state:
    st.session_state.events = pd.DataFrame(columns=['x', 'y', 'Tipo'])

# --- CONTROLES EN LA BARRA LATERAL ---
st.sidebar.header("Configuración del Partido")
player_name = st.sidebar.text_input("Jugador / Equipo", "Pedri")
match_name = st.sidebar.text_input("Partido", "Barcelona vs Real Madrid")
event_type = st.sidebar.selectbox("Tipo de Acción a añadir:", ["Pase Completado", "Tiro", "Asistencia", "Recuperación"])
line_color = st.sidebar.color_picker("Color de los eventos", "#00FFCC")

if st.sidebar.button("🗑️ Borrar todos los eventos"):
    st.session_state.events = pd.DataFrame(columns=['x', 'y', 'Tipo'])
    st.rerun()

# --- CONFIGURACIÓN DEL CAMPO ---
# Estilo oscuro profesional (Opta/WhoScored style)
pitch = Pitch(pitch_type='opta', pitch_color='#0e1117', line_color='#555555', goal_type='line')
fig, ax = pitch.draw(figsize=(10, 7))

# Dibujar los eventos que ya se hayan guardado
if not st.session_state.events.empty:
    for _, row in st.session_state.events.iterrows():
        # Cambiamos la forma según el tipo de acción
        marker = 'o' if row['Tipo'] == 'Pase Completado' else '*' if row['Tipo'] == 'Tiro' else 'X'
        pitch.scatter(row['x'], row['y'], ax=ax, s=200, color=line_color, edgecolors='white', marker=marker, alpha=0.8)

# Títulos del gráfico
fig.text(0.5, 0.93, f"{player_name} - Acciones del Partido", size=18, color='white', ha='center', weight='bold')
fig.text(0.5, 0.89, match_name, size=12, color='#888888', ha='center')
fig.text(0.5, 0.05, "Cancha interactiva | Creado con tu App de Fútbol", size=9, color='#555555', ha='center')

# --- CAMPO INTERACTIVO (Captura los clics) ---
# Aquí mostramos el campo y guardamos las coordenadas de donde hagas clic
st.write("👇 **Haz clic en cualquier zona del campo para registrar un evento:**")
event_dict = st.pyplot(fig, on_click=None) # Captura básica de Streamlit

# Formulario simulado para añadir la coordenada exacta de manera limpia
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    x_input = st.number_input("Coordenada X (0 a 100)", min_value=0, max_value=100, value=50)
with col2:
    y_input = st.number_input("Coordenada Y (0 a 100)", min_value=0, max_value=100, value=50)
with col3:
    st.write("") # Espacio
    if st.button("➕ Registrar Acción"):
        new_event = pd.DataFrame({'x': [x_input], 'y': [y_input], 'Tipo': [event_type]})
        st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
        st.rerun()

# --- MOSTRAR TABLA DE EVENTOS Y DESCARGA ---
if not st.session_state.events.empty:
    st.subheader("📋 Acciones registradas en este partido")
    st.dataframe(st.session_state.events)
    
    # Guardar y permitir descarga de la imagen
    fig.savefig("mapa_partido.png", bbox_inches='tight', dpi=300, facecolor='#0e1117')
    with open("mapa_partido.png", "rb") as file:
        st.download_button(
            label="💾 Descargar Mapa del Partido en Alta Calidad",
            data=file,
            file_name=f"mapa_{player_name.lower().replace(' ', '_')}.png",
            mime="image/png"
        )
