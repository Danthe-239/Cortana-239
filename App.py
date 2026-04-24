import streamlit as st
from groq import Groq
import random
from midiutil import MIDIFile
import io
import numpy as np
from scipy.io.wavfile import write

# 🔐 API
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- CHAT ----------------
def responder(mensaje):
    if client is None:
        return "❌ API Key no configurada"

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, IA avanzada, creativa y útil."},
                {"role": "user", "content": mensaje}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error IA: {str(e)}"

# ---------------- AUDIO REAL (WAV) ----------------
def nota_a_freq(nota):
    return 440 * (2 ** ((nota - 69) / 12))

def generar_audio(progresion, duracion=8, sample_rate=44100):

    t = np.linspace(0, duracion, int(sample_rate * duracion))
    audio = np.zeros_like(t)

    tiempo_por_acorde = duracion / len(progresion)

    for i, acorde in enumerate(progresion):
        inicio = int(i * tiempo_por_acorde * sample_rate)
        fin = int((i+1) * tiempo_por_acorde * sample_rate)

        for nota in acorde:
            freq = nota_a_freq(nota)
            onda = np.sin(2 * np.pi * freq * t[inicio:fin])
            audio[inicio:fin] += onda * 0.3

    audio = audio / np.max(np.abs(audio))

    buffer = io.BytesIO()
    write(buffer, sample_rate, (audio * 32767).astype(np.int16))
    buffer.seek(0)

    return buffer

# ---------------- GENERADOR MUSICAL PRO ----------------
def generar_musica(genero, modo):

    # 🎬 Cinemática
    if genero == "cinematica":
        escala = [48, 50, 52, 55, 57]
    else:
        escala = [60, 62, 64, 67, 69]

    if modo == "dark":
        escala = [n - 2 for n in escala]

    # 🎼 PROGRESIÓN ÉPICA
    progresion = [
        [escala[0], escala[2], escala[4]],
        [escala[1], escala[3], escala[4]],
        [escala[0], escala[2], escala[3]],
        [escala[0], escala[2], escala[4]]
    ]

    # 🎧 generar audio real
    audio = generar_audio(progresion, duracion=10)

    return audio

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
            genero = next((g for g in generos if g in partes), "cinematica")

            modo = "normal"
            for m in ["fast", "slow", "dark", "happy"]:
                if m in partes:
                    modo = m

            st.markdown(f"🎧 DJ Cortana: {genero} | {modo}")

            audio = generar_musica(genero, modo)

            st.success("🎼 Beat generado")

            # ▶️ REPRODUCTOR REAL
            st.audio(audio, format="audio/wav")

            st.download_button(
                "⬇️ Descargar audio",
                data=audio,
                file_name="cortana.wav",
                mime="audio/wav"
            )

    # 🤖 CHAT
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
