import streamlit as st
from groq import Groq
import random
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
                {"role": "system", "content": "Eres Cortana, una IA creativa, útil y amigable."},
                {"role": "user", "content": mensaje}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error IA: {str(e)}"

# ---------------- UTIL ----------------
def nota_a_freq(nota):
    return 440 * (2 ** ((nota - 69) / 12))

# ---------------- MELODÍA REAL ----------------
def generar_melodia(escala, longitud=40):
    melodia = []
    nota_actual = random.choice(escala)

    for _ in range(longitud):

        movimiento = random.choice([-3, -2, -1, 0, 1, 2, 3])

        idx = escala.index(nota_actual)
        nuevo_idx = max(0, min(len(escala) - 1, idx + movimiento))
        nota_actual = escala[nuevo_idx]

        duracion = random.choice([0.5, 1, 1.5, 2])

        melodia.append((nota_actual, duracion))

    return melodia

# ---------------- AUDIO ENGINE ----------------
def generar_audio(progresion, escala, duracion_total=10, sample_rate=44100):

    t_total = np.linspace(0, duracion_total, int(sample_rate * duracion_total))
    audio = np.zeros_like(t_total)

    tipo_onda = random.choice(["sine", "square", "saw"])

    def onda(freq, t):
        if tipo_onda == "sine":
            return np.sin(2 * np.pi * freq * t)
        elif tipo_onda == "square":
            return np.sign(np.sin(2 * np.pi * freq * t))
        elif tipo_onda == "saw":
            return 2 * (t * freq - np.floor(0.5 + t * freq))

    # 🎼 melodía principal
    melodia = generar_melodia(escala)

    tiempo = 0
    for nota, dur in melodia:

        inicio = int(tiempo * sample_rate)
        fin = int((tiempo + dur) * sample_rate)

        if fin > len(t_total):
            break

        freq = nota_a_freq(nota)
        t_seg = t_total[inicio:fin]

        audio[inicio:fin] += onda(freq, t_seg) * random.uniform(0.2, 0.5)

        tiempo += dur

    # 🎬 acordes fondo
    tiempo_por_acorde = duracion_total / len(progresion)

    for i, acorde in enumerate(progresion):
        inicio = int(i * tiempo_por_acorde * sample_rate)
        fin = int((i + 1) * tiempo_por_acorde * sample_rate)

        for nota in acorde:
            freq = nota_a_freq(nota)
            t_seg = t_total[inicio:fin]

            audio[inicio:fin] += np.sin(2 * np.pi * freq * t_seg) * 0.15

    # normalizar
    audio = audio / np.max(np.abs(audio))

    buffer = io.BytesIO()
    write(buffer, sample_rate, (audio * 32767).astype(np.int16))
    buffer.seek(0)

    return buffer

# ---------------- GENERADOR MUSICAL ----------------
def generar_musica(genero, modo):

    escalas = {
        "cinematica": [48, 50, 52, 55, 57],
        "trap": [60, 63, 65, 67, 70],
        "lofi": [60, 62, 63, 67, 69],
        "rock": [52, 55, 57, 59, 62],
        "electronic": [60, 64, 67, 71],
    }

    escala = escalas.get(genero, [60, 62, 64, 67, 69])

    if modo == "dark":
        escala = [n - 2 for n in escala]
    elif modo == "happy":
        escala = [n + 2 for n in escala]

    progresiones = [
        [
            [escala[0], escala[2], escala[4]],
            [escala[1], escala[3], escala[4]],
            [escala[0], escala[2], escala[3]],
            [escala[0], escala[2], escala[4]]
        ],
        [
            [escala[0], escala[2], escala[3]],
            [escala[1], escala[3], escala[4]],
            [escala[2], escala[4], escala[1]],
            [escala[0], escala[2], escala[4]]
        ],
        [
            [escala[0], escala[2], escala[4]],
            [escala[3], escala[1], escala[4]],
            [escala[2], escala[0], escala[3]],
            [escala[1], escala[3], escala[4]]
        ]
    ]

    progresion = random.choice(progresiones)
    duracion = random.choice([8, 10, 12])

    return generar_audio(progresion, escala, duracion)

# ---------------- UI ----------------
mensaje = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and mensaje:

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

            st.audio(audio, format="audio/wav")

            st.download_button(
                "⬇️ Descargar audio",
                data=audio,
                file_name="cortana.wav",
                mime="audio/wav"
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
