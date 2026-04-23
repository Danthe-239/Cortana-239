import streamlit as st
from groq import Groq
from midiutil import MIDIFile
import io
import random
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA")

# ---------------- API KEY ----------------
api_key = None

# Para local (tu PC)
if "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]

# Para Streamlit Cloud
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

# ---------------- FUNCIÓN MIDI ----------------
def generar_midi():
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "DJ Cortana Beat")
    midi.addTempo(track, time, 95)  # ritmo más tipo reggaeton/lento

    # Escala simple
    notas = [60, 62, 64, 65, 67, 69, 71]

    # Melodía
    for i in range(16):
        nota = random.choice(notas)
        midi.addNote(track, 0, nota, i, 1, 100)

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
Creadora de beats.

Genera:
- Nombre de la canción
- Estilo musical
- Acordes
- Idea del beat

Mensaje del usuario: {mensaje}
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

        # 🎵 Generar MIDI
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
