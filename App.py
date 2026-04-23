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

# ---------------- GENERADOR MIDI PRO ----------------
def generar_midi(genero):
    midi = MIDIFile(4)

    # -------- CONFIG POR GENERO --------
    if genero == "trap":
        tempo = 70
    elif genero == "lofi":
        tempo = 80
    elif genero == "rock":
        tempo = 110
    else:
        tempo = 95

    for track in range(4):
        midi.addTempo(track, 0, tempo)

    # 🎸 INSTRUMENTOS
    midi.addProgramChange(0, 0, 0, 0)   # Piano
    midi.addProgramChange(1, 0, 0, 34)  # Bajo
    midi.addProgramChange(3, 0, 0, 29)  # Guitarra eléctrica

    # -------- ACORDES --------
    acordes = [
        [57, 60, 64],  # Am
        [53, 57, 60],  # F
        [55, 59, 62],  # G
        [52, 55, 59]   # Em
    ]

    progresion = acordes * 4  # 16 compases

    # 🎹 ACORDES
    time = 0
    for acorde in progresion:
        for nota in acorde:
            midi.addNote(0, 0, nota, time, 4, 70)
        time += 4

    # 🎸 BAJO
    time = 0
    for acorde in progresion:
        root = acorde[0]

        midi.addNote(1, 0, root, time, 1, 100)
        midi.addNote(1, 0, root, time + 1.5, 0.5, 90)
        midi.addNote(1, 0, root, time + 2, 1, 100)
        midi.addNote(1, 0, root, time + 3, 1, 100)

        time += 4

    # 🥁 BATERÍA
    time = 0
    for _ in range(16):

        if genero == "trap":
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time + 2, 1, 110)

            for i in range(8):
                midi.addNote(2, 9, 42, time + i * 0.5, 0.25, 70)

        elif genero == "rock":
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time + 2, 1, 110)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i, 0.5, 80)

        elif genero == "lofi":
            midi.addNote(2, 9, 36, time, 1, 80)
            midi.addNote(2, 9, 38, time + 2, 1, 70)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i, 0.5, 50)

        else:  # reggaeton
            midi.addNote(2, 9, 36, time, 1, 110)
            midi.addNote(2, 9, 38, time + 1, 1, 110)
            midi.addNote(2, 9, 36, time + 2, 1, 110)
            midi.addNote(2, 9, 38, time + 3, 1, 110)

            for i in range(4):
                midi.addNote(2, 9, 42, time + i + 0.5, 0.5, 80)

        time += 4

    # 🎸 GUITARRA (rasgueo realista)
    time = 0
    for acorde in progresion:
        for beat in range(4):
            delay = 0
            for nota in acorde:
                midi.addNote(3, 0, nota + 12, time + beat + delay, 0.6, 75)
                delay += 0.08
        time += 4

    # 🎼 MELODÍA
    time = 0
    escala = [60, 62, 64, 65, 67, 69, 71]

    for i in range(64):
        nota = escala[i % len(escala)]
        midi.addNote(0, 0, nota + 12, time, 0.5, 60)
        time += 0.5

    # EXPORTAR
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

    # 🎧 MODO DJ
    if mensaje.lower().startswith("/dj"):

        genero = detectar_genero(mensaje)

        prompt = f"""
Eres DJ Cortana 🎧
Género: {genero}

Genera:
- Nombre de canción
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
