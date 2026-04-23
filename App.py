import streamlit as st
from groq import Groq
import random
from midiutil import MIDIFile
import io
import os

# 🔑 API KEY (Streamlit Cloud usa secrets)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Cortana IA", page_icon="🤖")

st.title("🤖 Cortana IA - Web")

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- FUNCION CHAT ----------------
def responder(mensaje):
    try:
        respuesta = client.chat.completions.create(
            model="llama3-70b-8192",  # usa uno vigente en Groq
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA amigable con emojis."},
                {"role": "user", "content": mensaje}
            ]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ---------------- GENERAR MIDI PRO ----------------
def generar_midi(genero):
    midi = MIDIFile(3)
    tempo = random.randint(90, 140)

    for track in range(3):
        midi.addTempo(track, 0, tempo)

    duracion = 32  # más largo 🔥

    # 🎹 MELODÍA
    notas = [60, 62, 64, 65, 67, 69, 71]
    time = 0
    for i in range(duracion):
        nota = random.choice(notas)
        midi.addNote(0, 0, nota, time, 1, 100)
        time += 1

    # 🎸 BAJO
    time = 0
    for i in range(duracion):
        nota = random.choice([36, 38, 40, 43])
        midi.addNote(1, 1, nota, time, 1, 90)
        time += 1

    # 🥁 BATERÍA
    time = 0
    for i in range(duracion):
        midi.addNote(2, 9, 36, time, 0.5, 100)  # kick
        midi.addNote(2, 9, 38, time + 0.5, 0.5, 100)  # snare
        time += 1

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)
    return buffer

# ---------------- INPUT ----------------
mensaje = st.text_input("Escribe tu mensaje o usa /dj")

if st.button("Enviar 🚀") and mensaje:

    # 🎧 MODO DJ
    if mensaje.lower().startswith("/dj"):
        genero = random.choice(["trap", "reggaeton", "drill", "electronic"])

        st.markdown(f"🎧 **Modo DJ activado** ({genero}) 🔥")

        midi_file = generar_midi(genero)

        st.success("🎼 Beat generado!")

        # 💥 BOTÓN MEJORADO (BandLab)
        st.download_button(
            "⬇️ Descargar MIDI (usar en BandLab 🎧)",
            data=midi_file,
            file_name=f"beat_{genero}.mid",
            mime="audio/midi"
        )

    else:
        # 👑 MENSAJE ESPECIAL DANTHE
        if "danthe" in mensaje.lower():
            st.markdown("👑 *Danthe es mi creador. Fue la primera persona en darme propósito.*")

        respuesta = responder(mensaje)

        st.session_state.historial.append(("Tú", mensaje))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- MOSTRAR CHAT ----------------
for autor, texto in st.session_state.historial:
    if autor == "Tú":
        st.markdown(f"🧑 **Tú:** {texto}")
    else:
        st.markdown(f"🤖 **Cortana:** {texto}")
