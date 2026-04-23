import streamlit as st
from groq import Groq
import os
from midiutil import MIDIFile
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA")

# ---------------- API KEY ----------------
api_key = None

# Local (tu PC)
if "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]

# Streamlit Cloud
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        pass

if not api_key:
    st.error("❌ Falta la API KEY")
    st.stop()

client = Groq(api_key=api_key)

# ---------------- MEMORIA ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- FUNCIÓN MIDI PRO ----------------
def generar_midi():
    midi = MIDIFile(2)

    tempo = 95
    midi.addTempo(0, 0, tempo)
    midi.addTempo(1, 0, tempo)

    # Acordes (Am - F - G - Em)
    acordes = [
        [57, 60, 64],  # Am
        [53, 57, 60],  # F
        [55, 59, 62],  # G
        [52, 55, 59]   # Em
    ]

    time = 0

    # 🎹 Pista de acordes
    for i in range(4):
        acorde = acordes[i % 4]
        for nota in acorde:
            midi.addNote(0, 0, nota, time, 4, 80)
        time += 4

    # 🎸 Bajo (ritmo tipo reggaeton)
    roots = [57, 53, 55, 52]
    time = 0

    for i in range(4):
        root = roots[i % 4]

        midi.addNote(1, 0, root, time, 1, 100)
        midi.addNote(1, 0, root, time + 1.5, 0.5, 90)
        midi.addNote(1, 0, root, time + 2, 1, 100)
        midi.addNote(1, 0, root, time + 3, 1, 100)

        time += 4

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)

    return buffer

# ---------------- MOSTRAR CHAT ----------------
for msg in st.session_state.chat:
    st.chat_message(msg["role"]).write(msg["content"])

# ---------------- INPUT ----------------
mensaje = st.chat_input("Escribe algo...")

if mensaje:
    st.chat_message("user").write(mensaje)
    st.session_state.chat.append({"role": "user", "content": mensaje})

    # ---------------- MODO DJ ----------------
    if mensaje.lower().startswith("/dj"):

        prompt = f"""
Eres DJ Cortana 🎧

Genera:
- Nombre de la canción
- Estilo musical
- Acordes
- Idea del beat

Mensaje: {mensaje}
"""

        try:
            respuesta = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            texto = respuesta.choices[0].message.content

        except Exception as e:
            texto = f"ERROR: {str(e)}"

        st.chat_message("assistant").write(texto)
        st.session_state.chat.append({"role": "assistant", "content": texto})

        # 🎵 GENERAR MIDI
        try:
            midi_file = generar_midi()

            st.download_button(
                label="⬇️ Descargar Beat MIDI",
                data=midi_file,
                file_name="dj_cortana.mid",
                mime="audio/midi"
            )

        except Exception as e:
            st.error(f"Error generando MIDI: {str(e)}")

    # ---------------- CHAT NORMAL ----------------
    else:
        try:
            respuesta = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.chat
            )

            texto = respuesta.choices[0].message.content

        except Exception as e:
            texto = f"ERROR: {str(e)}"

        st.chat_message("assistant").write(texto)
        st.session_state.chat.append({"role": "assistant", "content": texto})
