import streamlit as st
from groq import Groq
import random
from midiutil import MIDIFile
import io

# 🔐 API segura
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- CHAT IA ----------------
def responder(mensaje):
    if client is None:
        return "❌ API Key no configurada"

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA amigable, creativa y útil."},
                {"role": "user", "content": mensaje}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error IA: {str(e)}"

# ---------------- GENERADOR MUSICAL PRO ----------------
def generar_midi(genero, modo):

    midi = MIDIFile(4)

    # 🎸 Instrumentos
    midi.addProgramChange(0, 0, 0, 30)  # guitarra
    midi.addProgramChange(1, 0, 0, 32)  # bajo
    midi.addProgramChange(2, 0, 0, 0)   # piano
    midi.addProgramChange(3, 9, 0, 0)   # batería

    # 🎬 Cinemática
    if genero == "cinematica":
        escala = [48, 50, 52, 55, 57]
        tempo = random.randint(60, 90)
    else:
        escala = [60, 62, 64, 67, 69]
        tempo = random.randint(80, 140)

    # ⚡ modos
    if modo == "fast":
        tempo += 20
    elif modo == "slow":
        tempo -= 20
    elif modo == "dark":
        escala = [n - 2 for n in escala]
        if genero == "cinematica":
            escala = [n - 3 for n in escala]
    elif modo == "happy":
        escala = [n + 2 for n in escala]

    for t in range(4):
        midi.addTempo(t, 0, tempo)

    # 🎵 motivo musical
    motivo = random.sample(escala, 3)

    # 🎼 duración
    duracion = 64 if genero == "cinematica" else 32

    # 🎹 MELODÍA
    time = 0
    for i in range(duracion):

        if i % 4 == 0:
            motivo = random.sample(escala, 3)

        nota = motivo[i % len(motivo)]
        variacion = random.choice([0, 12, -12])

        midi.addNote(2, 0, nota + variacion, time, 1, 100)
        time += 1

    # 🎸 GUITARRA
    time = 0
    for i in range(duracion):
        nota = random.choice(motivo)
        midi.addNote(0, 0, nota, time, 2, 80)
        time += 2

    # 🎸 BAJO
    time = 0
    for i in range(duracion):
        nota = motivo[0] - 24
        midi.addNote(1, 0, nota, time, 1, 100)
        time += 1

    # 🥁 DRUMS
    time = 0
    for i in range(duracion):

        midi.addNote(3, 9, 36, time, 0.5, 100)

        if i % 2 == 1:
            midi.addNote(3, 9, 38, time, 0.5, 100)

        if random.random() > 0.4:
            midi.addNote(3, 9, 42, time + 0.25, 0.25, 80)

        time += 1

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)

    return buffer

# ---------------- UI ----------------
mensaje = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and mensaje:

    # 🎧 MODO DJ
    if mensaje.lower().startswith("/dj"):

        partes = mensaje.lower().split()

        if len(partes) == 1:
            st.markdown("""
### 🎧 Comandos DJ

🎵 Géneros:
/dj trap  
/dj reggaeton  
/dj drill  
/dj lofi  
/dj rock  
/dj electronic  
/dj cinematica  

⚡ Modos:
/dj fast  
/dj slow  
/dj dark  
/dj happy  
""")

        else:
            generos = ["trap", "reggaeton", "drill", "lofi", "rock", "electronic", "cinematica"]

            genero = next((g for g in generos if g in partes), random.choice(generos))

            modo = "normal"
            for m in ["fast", "slow", "dark", "happy"]:
                if m in partes:
                    modo = m

            st.markdown(f"🎧 DJ Cortana: {genero} | {modo}")

            midi_file = generar_midi(genero, modo)

            st.success("🎼 Beat generado")

            st.warning("⚠️ Vista previa MIDI limitada en navegadores")

            st.download_button(
                "⬇️ Descargar MIDI",
                data=midi_file,
                file_name=f"cortana_{genero}.mid",
                mime="audio/midi"
            )

    # 🤖 CHAT NORMAL
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
