import streamlit as st
from groq import Groq
import random
from midiutil import MIDIFile
import io

# 🔑 API KEY
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- CHAT ----------------
def responder(mensaje):
    try:
        respuesta = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA amigable que usa emojis."},
                {"role": "user", "content": mensaje}
            ]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ---------------- GENERADOR MIDI ----------------
def generar_midi(genero, modo):
    midi = MIDIFile(3)

    # 🎧 CONFIG BASE POR GÉNERO
    if genero == "trap":
        tempo = random.randint(130, 150)
        escala = [60, 63, 65, 67, 70]
        bajo = [36, 36, 38, 35]

    elif genero == "reggaeton":
        tempo = random.randint(85, 100)
        escala = [60, 62, 64, 67, 69]
        bajo = [36, 38, 40, 43]

    elif genero == "drill":
        tempo = random.randint(130, 145)
        escala = [60, 61, 63, 65, 67]
        bajo = [35, 36, 38]

    elif genero == "lofi":
        tempo = random.randint(60, 80)
        escala = [60, 62, 65, 67, 69]
        bajo = [36, 38]

    elif genero == "rock":
        tempo = random.randint(100, 130)
        escala = [60, 64, 67, 69]
        bajo = [36, 40, 43]

    else:  # electronic
        tempo = random.randint(110, 140)
        escala = [60, 62, 64, 65, 67]
        bajo = [36, 38, 40]

    # ⚡ MODOS
    if modo == "fast":
        tempo += 20
    elif modo == "slow":
        tempo -= 20
    elif modo == "dark":
        escala = [n - 2 for n in escala]
    elif modo == "happy":
        escala = [n + 2 for n in escala]

    # 🎵 TEMPO
    for track in range(3):
        midi.addTempo(track, 0, tempo)

    duracion = 48

    # 🎹 MELODÍA
    time = 0
    for i in range(duracion):
        nota = random.choice(escala)
        dur = random.choice([0.5, 1, 1.5])
        midi.addNote(0, 0, nota, time, dur, 100)
        time += dur

    # 🎸 BAJO
    time = 0
    for i in range(duracion):
        nota = random.choice(bajo)
        midi.addNote(1, 1, nota, time, 1, 90)
        time += 1

    # 🥁 BATERÍA
    time = 0
    for i in range(duracion):
        midi.addNote(2, 9, 36, time, 0.5, 100)

        if genero in ["trap", "drill"]:
            midi.addNote(2, 9, 38, time + 0.75, 0.5, 100)
        else:
            midi.addNote(2, 9, 38, time + 0.5, 0.5, 100)

        if genero in ["trap", "drill"]:
            midi.addNote(2, 9, 42, time + 0.25, 0.25, 80)
            midi.addNote(2, 9, 42, time + 0.5, 0.25, 80)

        time += 1

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)
    return buffer

# ---------------- INPUT ----------------
mensaje = st.text_input("💬 Escribe tu mensaje o usa /dj")

if st.button("Enviar 🚀") and mensaje:

    # 🎧 MODO DJ
    if mensaje.lower().startswith("/dj"):

        partes = mensaje.lower().split()

        generos_validos = ["trap", "reggaeton", "drill", "lofi", "rock", "electronic"]

        genero = None
        for g in generos_validos:
            if g in partes:
                genero = g

        if genero is None:
            genero = random.choice(generos_validos)

        modo = "normal"
        if "fast" in partes:
            modo = "fast"
        elif "slow" in partes:
            modo = "slow"
        elif "dark" in partes:
            modo = "dark"
        elif "happy" in partes:
            modo = "happy"

        st.markdown(f"🎧 **DJ Cortana: {genero.upper()} | modo {modo}** 🔥")

        midi_file = generar_midi(genero, modo)

        st.success("🎼 Beat generado!")

        st.download_button(
            "⬇️ Descargar MIDI (usar en BandLab 🎧)",
            data=midi_file,
            file_name=f"cortana_{genero}_{modo}.mid",
            mime="audio/midi"
        )

    else:
        # 👑 MENSAJE DANTHE
        if "danthe" in mensaje.lower():
            st.markdown("👑 *Danthe es mi creador. Fue quien me dio vida.*")

        respuesta = responder(mensaje)

        st.session_state.historial.append(("Tú", mensaje))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- CHAT ----------------
for autor, texto in st.session_state.historial:
    if autor == "Tú":
        st.markdown(f"🧑 **Tú:** {texto}")
    else:
        st.markdown(f"🤖 **Cortana:** {texto}")
