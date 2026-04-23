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
       def generar_midi():
    midi = MIDIFile(2)  # 2 pistas: acordes + bajo

    tempo = 95
    midi.addTempo(0, 0, tempo)
    midi.addTempo(1, 0, tempo)

    # ---------------- ACORDES ----------------
    # Notas MIDI:
    # Am = A C E → 57 60 64
    # F  = F A C → 53 57 60
    # G  = G B D → 55 59 62
    # Em = E G B → 52 55 59

    acordes = [
        [57, 60, 64],  # Am
        [53, 57, 60],  # F
        [55, 59, 62],  # G
        [52, 55, 59]   # Em
    ]

    time = 0

    for i in range(4):  # 4 compases
        acorde = acordes[i % len(acordes)]

        # tocar acorde completo (3 notas)
        for nota in acorde:
            midi.addNote(0, 0, nota, time, 4, 80)

        time += 4

    # ---------------- BAJO ----------------
    # toca la raíz del acorde (más grave)
    time = 0

    roots = [57, 53, 55, 52]

    for i in range(4):
        root = roots[i % len(roots)]

        # patrón tipo reggaeton (dem bow básico)
        midi.addNote(1, 0, root, time, 1, 100)
        midi.addNote(1, 0, root, time + 1.5, 0.5, 90)
        midi.addNote(1, 0, root, time + 2, 1, 100)
        midi.addNote(1, 0, root, time + 3, 1, 100)

        time += 4

    # ---------------- EXPORTAR ----------------
    import io
    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)

    return buffer
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
