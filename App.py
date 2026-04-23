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

# ---------------- DETECTAR GENERO ----------------
def detectar_genero(texto):
    t = texto.lower()

    if "trap" in t:
        return "trap"
    elif "lofi" in t or "lo-fi" in t:
        return "lofi"
    elif "rock" in t:
        return "rock"
    else:
        return "reggaeton"

# ---------------- MIDI INTELIGENTE ----------------
def generar_midi(genero):
    midi = MIDIFile(4)

    # -------- CONFIG POR GENERO --------
    if genero == "trap":
        tempo = 70
        acordes = [[57,60,64],[55,59,62],[53,57,60],[52,55,59]]
    elif genero == "lofi":
        tempo = 80
        acordes = [[57,60,64],[53,57,60],[52,55,59],[55,59,62]]
    elif genero == "rock":
        tempo = 110
        acordes = [[57,60,64],[55,59,62],[53,57,60],[52,55,59]]
    else:  # reggaeton
        tempo = 95
        acordes = [[57,60,64],[53,57,60],[55,59,62],[52,55,59]]

    for track in range(4):
        midi.addTempo(track, 0, tempo)

    # -------- ACORDES --------
    time = 0
    for acorde in acordes:
        for nota in acorde:
            midi.addNote(0, 0, nota, time, 4, 80)
        time += 4

    # -------- BAJO --------
    roots = [a[0] for a in acordes]
    time = 0

    for root in roots:
        midi.addNote(1, 0, root, time, 1, 100)
        midi.addNote(1, 0, root, time+1.5, 0.5, 90)
        midi.addNote(1, 0, root, time+2, 1, 100)
        midi.addNote(1, 0, root, time+3, 1, 100)
        time += 4

    # -------- BATERÍA --------
    time = 0
    for _ in range(4):

        if genero == "trap":
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time+2, 1, 110)

            # hi-hats rápidos
            for i in range(8):
                midi.addNote(2, 9, 42, time + i*0.5, 0.25, 70)

        elif genero == "rock":
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time+2, 1, 110)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i, 0.5, 80)

        elif genero == "lofi":
            midi.addNote(2, 9, 36, time, 1, 80)
            midi.addNote(2, 9, 38, time+2, 1, 70)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i, 0.5, 50)

        else:  # reggaeton
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time+1, 1, 110)
            midi.addNote(2, 9, 36, time+2, 1, 110)
            midi.addNote(2, 9, 38, time+3, 1, 110)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i + 0.5, 0.5, 80)

        time += 4

    # -------- GUITARRA --------
    time = 0
    for acorde in acordes:
        for beat in range(4):
            for nota in acorde:
                midi.addNote(3, 0, nota+12, time+beat, 0.5, 70)
        time += 4

    # -------- EXPORTAR --------
    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)

    return buffer

# ---------------- CHAT ----------------
for msg in st.session_state.chat:
    st.chat_message(msg["role"]).write(msg["content"])

mensaje = st.chat_input("Escribe algo...")

if mensaje:
    st.chat_message("user").write(mensaje)
    st.session_state.chat.append({"role": "user", "content": mensaje})

    if mensaje.lower().startswith("/dj"):

        genero = detectar_genero(mensaje)

        prompt = f"""
Eres DJ Cortana 🎧
Género detectado: {genero}

Genera:
- Nombre
- Estilo
- Descripción del beat
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

        midi_file = generar_midi(genero)

        st.download_button(
            "⬇️ Descargar Beat MIDI",
            data=midi_file,
            file_name=f"beat_{genero}.mid",
            mime="audio/midi"
        )

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
