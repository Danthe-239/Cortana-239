import streamlit as st
from groq import Groq
import random
from midiutil import MIDIFile
import io
import base64

# 🔑 API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- CHAT ----------------
def responder(mensaje):
    modelos = ["llama-3.1-8b-instant"]

    for modelo in modelos:
        try:
            r = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": "Eres Cortana, una IA amigable con emojis."},
                    {"role": "user", "content": mensaje}
                ]
            )
            return r.choices[0].message.content
        except:
            continue

    return "❌ Error en IA"

# ---------------- GENERADOR PRO ----------------
def generar_midi(genero, modo):

    midi = MIDIFile(4)

    # 🎸 INSTRUMENTOS (program change)
    midi.addProgramChange(0, 0, 0, 30)  # guitarra eléctrica
    midi.addProgramChange(1, 0, 0, 32)  # bajo
    midi.addProgramChange(2, 0, 0, 0)   # piano/melodía
    midi.addProgramChange(3, 9, 0, 0)   # batería

    # 🎧 TEMPO VARIABLE
    tempo = random.randint(70, 150)

    if modo == "fast":
        tempo += 20
    elif modo == "slow":
        tempo -= 20

    for t in range(4):
        midi.addTempo(t, 0, tempo)

    # 🎼 ESCALAS DIFERENTES (para variar sonido)
    escalas = [
        [60, 62, 64, 67, 69],
        [60, 63, 65, 67, 70],
        [60, 61, 63, 66, 68],
        [60, 62, 65, 67, 71]
    ]

    escala = random.choice(escalas)

    if modo == "dark":
        escala = [n - 2 for n in escala]
    elif modo == "happy":
        escala = [n + 2 for n in escala]

    duracion = 64

    # 🎸 GUITARRA (arpegios más reales)
    time = 0
    for i in range(duracion):
        nota = random.choice(escala)
        midi.addNote(0, 0, nota, time, random.choice([0.5, 1]), 90)
        time += random.choice([0.5, 1])

    # 🎹 MELODÍA PRINCIPAL (más variación)
    time = 0
    for i in range(duracion):
        if random.random() > 0.3:
            nota = random.choice(escala) + 12
            dur = random.choice([0.5, 1, 1.5])
            midi.addNote(2, 0, nota, time, dur, 100)
            time += dur
        else:
            time += 0.5

    # 🎸 BAJO (nuevo instrumento sólido)
    time = 0
    for i in range(duracion):
        nota = random.choice(escala) - 24
        midi.addNote(1, 0, nota, time, 1, 100)
        time += 1

    # 🥁 BATERÍA (más variada)
    time = 0
    for i in range(duracion):
        midi.addNote(3, 9, 36, time, 0.5, 100)  # kick

        if random.random() > 0.5:
            midi.addNote(3, 9, 38, time + 0.5, 0.5, 100)  # snare

        if random.random() > 0.3:
            midi.addNote(3, 9, 42, time + 0.25, 0.25, 80)  # hihat

        time += 1

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)

    return buffer

# ---------------- REPRODUCTOR MIDI ----------------
def reproducir_midi(midi_bytes):
    b64 = base64.b64encode(midi_bytes.read()).decode()
    midi_bytes.seek(0)

    html = f"""
    <audio controls>
        <source src="data:audio/midi;base64,{b64}" type="audio/midi">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------- INPUT ----------------
mensaje = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and mensaje:

    if mensaje.lower().startswith("/dj"):

        partes = mensaje.lower().split()

        if len(partes) == 1:
            st.markdown("""
### 🎧 Comandos DJ

/dj trap  
/dj reggaeton  
/dj drill  
/dj lofi  
/dj rock  
/dj electronic  

Modos:
fast | slow | dark | happy
""")

        else:
            generos = ["trap", "reggaeton", "drill", "lofi", "rock", "electronic"]

            genero = next((g for g in generos if g in partes), None)
            if genero is None:
                genero = random.choice(generos)

            modo = "normal"
            for m in ["fast", "slow", "dark", "happy"]:
                if m in partes:
                    modo = m

            st.markdown(f"🎧 DJ Cortana: {genero} | {modo}")

            midi_file = generar_midi(genero, modo)

            st.success("🎼 Beat generado")

            # ▶️ REPRODUCIR
            reproducir_midi(midi_file)

            # ⬇️ DESCARGAR
            st.download_button(
                "⬇️ Descargar MIDI",
                data=midi_file,
                file_name=f"cortana_{genero}.mid",
                mime="audio/midi"
            )

    else:
        if "danthe" in mensaje.lower():
            st.markdown("👑 Danthe es mi creador.")

        respuesta = responder(mensaje)

        st.session_state.historial.append(("Tú", mensaje))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- HISTORIAL ----------------
for autor, texto in st.session_state.historial:
    if autor == "Tú":
        st.markdown(f"🧑 {texto}")
    else:
        st.markdown(f"🤖 {texto}")
