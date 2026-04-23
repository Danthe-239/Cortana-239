import streamlit as st
from groq import Groq
import os
from midiutil import MIDIFile
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA")

# ---------------- API KEY ----------------
api_key = os.getenv("GROQ_API_KEY")

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

# ---------------- MIDI PRO ----------------
def generar_midi():
    midi = MIDIFile(4)  # 4 pistas

    tempo = 95
    for track in range(4):
        midi.addTempo(track, 0, tempo)

    # ---------------- ACORDES ----------------
    acordes = [
        [57, 60, 64],  # Am
        [53, 57, 60],  # F
        [55, 59, 62],  # G
        [52, 55, 59]   # Em
    ]

    time = 0
    for i in range(4):
        acorde = acordes[i]
        for nota in acorde:
            midi.addNote(0, 0, nota, time, 4, 80)
        time += 4

    # ---------------- BAJO ----------------
    roots = [57, 53, 55, 52]
    time = 0

    for i in range(4):
        root = roots[i]

        midi.addNote(1, 0, root, time, 1, 100)
        midi.addNote(1, 0, root, time + 1.5, 0.5, 90)
        midi.addNote(1, 0, root, time + 2, 1, 100)
        midi.addNote(1, 0, root, time + 3, 1, 100)

        time += 4

    # ---------------- BATERÍA (canal 9) ----------------
    time = 0
    for bar in range(4):
        # Kick (36), Snare (38), Hi-hat (42)

        midi.addNote(2, 9, 36, time, 1, 110)        # kick
        midi.addNote(2, 9, 42, time + 0.5, 0.5, 80) # hat
        midi.addNote(2, 9, 38, time + 1, 1, 110)    # snare
        midi.addNote(2, 9, 42, time + 1.5, 0.5, 80)

        midi.addNote(2, 9, 36, time + 2, 1, 110)
        midi.addNote(2, 9, 42, time + 2.5, 0.5, 80)
        midi.addNote(2, 9, 38, time + 3, 1, 110)
        midi.addNote(2, 9, 42, time + 3.5, 0.5, 80)

        time += 4

    # ---------------- GUITARRA ELÉCTRICA ----------------
    time = 0
    for i in range(4):
        acorde = acordes[i]

        for beat in range(4):
            for nota in acorde:
                midi.addNote(3, 0, nota + 12, time + beat, 0.5, 70)

        time += 4

    # ---------------- EXPORTAR ----------------
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

    # 🎧 MODO DJ
    if mensaje.lower().startswith("/dj"):

        prompt = f"""
Eres DJ Cortana 🎧
Crea un beat profesional.

Incluye:
- Nombre
- Estilo
- Acordes
- Idea musical

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

        # 🎵 MIDI
        midi_file = generar_midi()

        st.download_button(
            "⬇️ Descargar Beat MIDI",
            data=midi_file,
            file_name="dj_cortana_pro.mid",
            mime="audio/midi"
        )

    # 💬 CHAT NORMAL
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
