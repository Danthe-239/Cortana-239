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
    modelos = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile"
    ]

    for modelo in modelos:
        try:
            respuesta = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": "Eres Cortana, una IA amigable que usa emojis."},
                    {"role": "user", "content": mensaje}
                ]
            )
            return respuesta.choices[0].message.content
        except:
            continue

    return "❌ Error: ningún modelo disponible 😢"

# ---------------- GENERADOR NORMAL ----------------
def generar_midi_normal(genero, modo):
    midi = MIDIFile(3)

    if genero == "trap":
        tempo = random.randint(130, 150)
        escala = [60, 63, 65, 67, 70]
        bajo = [36, 38, 35]

    elif genero == "reggaeton":
        tempo = random.randint(85, 100)
        escala = [60, 62, 64, 67, 69]
        bajo = [36, 38, 40]

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

    else:
        genero = "electronic"
        tempo = random.randint(110, 140)
        escala = [60, 62, 64, 65, 67]
        bajo = [36, 38, 40]

    # 🎛️ MODOS
    if modo == "fast":
        tempo += 20
    elif modo == "slow":
        tempo -= 20
    elif modo == "dark":
        escala = [n - 2 for n in escala]
    elif modo == "happy":
        escala = [n + 2 for n in escala]

    for track in range(3):
        midi.addTempo(track, 0, tempo)

    duracion = 48

    # 🎹 MELODÍA
    t = 0
    for _ in range(duracion):
        nota = random.choice(escala)
        dur = random.choice([0.5, 1, 1.5])
        midi.addNote(0, 0, nota, t, dur, 100)
        t += dur

    # 🎸 BAJO
    t = 0
    for _ in range(duracion):
        midi.addNote(1, 1, random.choice(bajo), t, 1, 90)
        t += 1

    # 🥁 BATERÍA
    t = 0
    for _ in range(duracion):
        midi.addNote(2, 9, 36, t, 0.5, 100)

        if genero in ["trap", "drill"]:
            midi.addNote(2, 9, 38, t + 0.75, 0.5, 100)
            midi.addNote(2, 9, 42, t + 0.25, 0.25, 80)
            midi.addNote(2, 9, 42, t + 0.5, 0.25, 80)
        else:
            midi.addNote(2, 9, 38, t + 0.5, 0.5, 100)

        t += 1

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)
    return buffer

# ---------------- GENERADOR AVANZADO ----------------
def generar_midi(genero, modo):

    if genero == "cinematic":
        midi = MIDIFile(3)
        tempo = random.randint(60, 80)

        acordes = [
            [60, 64, 67],  # C
            [57, 60, 64],  # Am
            [53, 57, 60],  # F
            [55, 59, 62]   # G
        ]

        for t in range(3):
            midi.addTempo(t, 0, tempo)

        # 🎹 ACORDES LARGOS (PAD)
        time = 0
        for _ in range(16):
            acorde = random.choice(acordes)
            for nota in acorde:
                midi.addNote(0, 0, nota, time, 4, 80)
            time += 4

        # 🎼 MELODÍA ATMOSFÉRICA
        escala = [60, 62, 64, 67, 69]
        time = 0
        for _ in range(32):
            nota = random.choice(escala)
            midi.addNote(1, 0, nota + 12, time, 1, 70)
            time += 1

        # 🥁 PERCUSIÓN SUAVE
        time = 0
        for _ in range(32):
            midi.addNote(2, 9, 36, time, 0.5, 60)
            time += 1

        buffer = io.BytesIO()
        midi.writeFile(buffer)
        buffer.seek(0)
        return buffer

    else:
        return generar_midi_normal(genero, modo)

# ---------------- INPUT ----------------
mensaje = st.text_input("💬 Escribe tu mensaje o usa /dj")

if st.button("Enviar 🚀") and mensaje:

    if mensaje.lower().startswith("/dj"):

        partes = mensaje.lower().split()

        if len(partes) == 1:
            st.markdown("""
### 🎧 Comandos DJ

**🎵 Géneros**
- /dj trap
- /dj reggaeton
- /dj drill
- /dj lofi
- /dj rock
- /dj electronic
- /dj cinematic 🎬 (nuevo)

**⚡ Modos**
- fast
- slow
- dark
- happy

Ejemplo:
`/dj cinematic`
`/dj trap fast`
            """)
        else:
            generos = ["trap", "reggaeton", "drill", "lofi", "rock", "electronic", "cinematic"]

            genero = next((g for g in generos if g in partes), None)
            if genero is None:
                genero = random.choice(generos)

            modo = "normal"
            for m in ["fast", "slow", "dark", "happy"]:
                if m in partes:
                    modo = m

            st.markdown(f"🎧 **DJ Cortana: {genero.upper()} | modo {modo}** 🔥")

            midi_file = generar_midi(genero, modo)

            st.success("🎼 Beat generado!")

            st.download_button(
                "⬇️ Descargar MIDI",
                data=midi_file,
                file_name=f"cortana_{genero}_{modo}.mid",
                mime="audio/midi"
            )

    else:
        if "danthe" in mensaje.lower():
            st.markdown("👑 *Danthe es mi creador.*")

        respuesta = responder(mensaje)

        st.session_state.historial.append(("Tú", mensaje))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- HISTORIAL ----------------
for autor, texto in st.session_state.historial:
    if autor == "Tú":
        st.markdown(f"🧑 **Tú:** {texto}")
    else:
        st.markdown(f"🤖 **Cortana:** {texto}")
