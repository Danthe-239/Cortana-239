import streamlit as st
from groq import Groq
import random
import io
import numpy as np
from scipy.io.wavfile import write

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# ---------------- API ----------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- CHAT ----------------
def responder(msg):
    if client is None:
        return "❌ API Key no configurada"

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA creativa, amigable y útil."},
                {"role": "user", "content": msg}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------- MUSICA ----------------
def nota_a_freq(n):
    return 440 * (2 ** ((n - 69) / 12))

# 🔥 NUEVO GENERADOR DE MELODÍAS
def generar_melodia(escala, genero):

    patrones_ritmo = [
        [1,1,2,1,1,2],
        [0.5,0.5,1,1,2,1],
        [2,1,1,2,1],
        [1,0.5,0.5,1,2,1],
        [1,1,1,1,2,2]
    ]

    tipos = ["ascendente", "descendente", "salto", "repetitiva", "mixta"]

    tipo = random.choice(tipos)
    ritmo = random.choice(patrones_ritmo)

    melodia = []

    if tipo == "ascendente":
        base = random.choice(escala[:2])
        for r in ritmo:
            base = min(base + random.choice([1,2]), escala[-1])
            melodia.append((base, r))

    elif tipo == "descendente":
        base = random.choice(escala[-2:])
        for r in ritmo:
            base = max(base - random.choice([1,2]), escala[0])
            melodia.append((base, r))

    elif tipo == "salto":
        for r in ritmo:
            nota = random.choice(escala)
            if random.random() > 0.5:
                nota += random.choice([5,7])
            melodia.append((nota, r))

    elif tipo == "repetitiva":
        nota = random.choice(escala)
        for r in ritmo:
            melodia.append((nota, r))

    else:
        for r in ritmo:
            nota = random.choice(escala)
            melodia.append((nota, r))

    return melodia

# 🔊 GENERADOR DE AUDIO
def generar_audio(progresion, escala, genero, duracion_total=10, sr=44100):

    t_total = np.linspace(0, duracion_total, int(sr * duracion_total))
    audio = np.zeros_like(t_total)

    tipo_onda = random.choice(["sine","square","saw"])

    def onda(freq, t):
        if tipo_onda == "sine":
            return np.sin(2*np.pi*freq*t)
        elif tipo_onda == "square":
            return np.sign(np.sin(2*np.pi*freq*t))
        else:
            return 2*(t*freq - np.floor(0.5+t*freq))

    melodia = generar_melodia(escala, genero)

    tiempo = 0
    for nota, dur in melodia:

        ini = int(tiempo * sr)
        fin = int((tiempo + dur) * sr)

        if fin > len(t_total):
            break

        freq = nota_a_freq(nota)
        t_seg = t_total[ini:fin]

        audio[ini:fin] += onda(freq, t_seg) * random.uniform(0.2,0.5)

        tiempo += dur

    # 🎬 acordes fondo
    t_acorde = duracion_total / len(progresion)

    for i, acorde in enumerate(progresion):

        ini = int(i * t_acorde * sr)
        fin = int((i+1) * t_acorde * sr)

        for nota in acorde:
            freq = nota_a_freq(nota)
            t_seg = t_total[ini:fin]

            audio[ini:fin] += np.sin(2*np.pi*freq*t_seg) * 0.15

    audio = audio / np.max(np.abs(audio))

    buffer = io.BytesIO()
    write(buffer, sr, (audio * 32767).astype(np.int16))
    buffer.seek(0)

    return buffer

# 🎼 GENERADOR GENERAL
def generar_musica(genero, modo):

    escalas = {
        "cinematica":[48,50,52,55,57],
        "trap":[60,63,65,67,70],
        "lofi":[60,62,63,67,69],
        "rock":[52,55,57,59,62],
        "electronic":[60,64,67,71],
    }

    escala = escalas.get(genero, [60,62,64,67,69])

    if modo == "dark":
        escala = [n-2 for n in escala]
    elif modo == "happy":
        escala = [n+2 for n in escala]

    progresiones = [
        [[escala[0],escala[2],escala[4]],
         [escala[1],escala[3],escala[4]],
         [escala[2],escala[4],escala[1]],
         [escala[0],escala[2],escala[4]]],

        [[escala[0],escala[2],escala[3]],
         [escala[1],escala[3],escala[4]],
         [escala[3],escala[1],escala[4]],
         [escala[0],escala[2],escala[4]]]
    ]

    return generar_audio(random.choice(progresiones), escala, genero)

# ---------------- UI ----------------
msg = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and msg:

    if msg.lower().startswith("/dj"):

        partes = msg.lower().split()

        generos = ["trap","reggaeton","drill","lofi","rock","electronic","cinematica"]
        genero = next((g for g in generos if g in partes), "cinematica")

        modo = "normal"
        for m in ["fast","slow","dark","happy"]:
            if m in partes:
                modo = m

        st.markdown(f"🎧 DJ Cortana: {genero} | {modo}")

        audio = generar_musica(genero, modo)

        st.success("🎼 Beat generado")

        st.audio(audio, format="audio/wav")

        st.download_button("⬇️ Descargar", audio, "cortana.wav")

    else:

        if "danthe" in msg.lower():
            st.markdown("👑 Danthe es mi creador.")

        resp = responder(msg)

        st.session_state.historial.append(("Tú", msg))
        st.session_state.historial.append(("Cortana", resp))

# historial
for a, t in st.session_state.historial:
    if a == "Tú":
        st.markdown(f"🧑 {t}")
    else:
        st.markdown(f"🤖 {t}")
