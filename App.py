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
                {"role": "system", "content": "Eres Cortana, una IA creativa."},
                {"role": "user", "content": msg}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------- AUDIO BASE ----------------
def nota_a_freq(n):
    return 440 * (2 ** ((n - 69) / 12))

def onda(tipo, freq, t):
    if tipo == "sine":
        return np.sin(2*np.pi*freq*t)
    elif tipo == "square":
        return np.sign(np.sin(2*np.pi*freq*t))
    else:  # saw
        return 2*(t*freq - np.floor(0.5+t*freq))

# ---------------- GENERADORES ----------------

# 🎼 melodía por frases (MUY distinta)
def frase_melodica(escala, estilo):
    frase = []

    if estilo == "intro":
        ritmo = [2,1,2,1]
        for r in ritmo:
            nota = random.choice(escala[:3])
            frase.append((nota, r))

    elif estilo == "build":
        ritmo = [1,1,1,1,2]
        base = random.choice(escala[:2])
        for r in ritmo:
            base += random.choice([1,2])
            base = min(base, escala[-1])
            frase.append((base, r))

    elif estilo == "drop":
        ritmo = [0.5,0.5,1,0.5,0.5,1]
        for r in ritmo:
            nota = random.choice(escala)
            if random.random() > 0.6:
                nota += random.choice([5,7])
            frase.append((nota, r))

    else:  # outro
        ritmo = [2,2,1]
        for r in ritmo:
            nota = random.choice(escala[:3])
            frase.append((nota, r))

    return frase

# 🥁 batería básica real
def agregar_bateria(audio, sr, duracion):
    t = np.linspace(0, duracion, int(sr*duracion))

    kick = np.sin(2*np.pi*60*t) * (np.sin(2*np.pi*2*t) > 0)
    snare = np.random.randn(len(t)) * (np.sin(2*np.pi*1*t) > 0)

    audio += kick * 0.2
    audio += snare * 0.05

    return audio

# 🎸 bajo
def agregar_bajo(audio, escala, sr, duracion):
    t = np.linspace(0, duracion, int(sr*duracion))

    nota = random.choice(escala[:2])
    freq = nota_a_freq(nota - 12)

    bajo = np.sin(2*np.pi*freq*t) * 0.2
    audio += bajo

    return audio

# 🎬 acordes
def agregar_acordes(audio, progresion, sr, duracion):
    t = np.linspace(0, duracion, int(sr*duracion))
    tiempo_acorde = duracion / len(progresion)

    for i, acorde in enumerate(progresion):
        ini = int(i * tiempo_acorde * sr)
        fin = int((i+1) * tiempo_acorde * sr)

        for nota in acorde:
            freq = nota_a_freq(nota)
            audio[ini:fin] += np.sin(2*np.pi*freq*t[ini:fin]) * 0.1

    return audio

# 🎼 render completo
def generar_track(escala, progresion, duracion=15, sr=44100):

    t_total = np.linspace(0, duracion, int(sr*duracion))
    audio = np.zeros_like(t_total)

    tipo_onda = random.choice(["sine","square","saw"])

    # 🎬 secciones
    secciones = ["intro","build","drop","outro"]
    tiempo = 0

    for seccion in secciones:

        frase = frase_melodica(escala, seccion)

        for nota, dur in frase:

            ini = int(tiempo * sr)
            fin = int((tiempo + dur) * sr)

            if fin > len(audio):
                break

            freq = nota_a_freq(nota)
            t_seg = t_total[ini:fin]

            audio[ini:fin] += onda(tipo_onda, freq, t_seg) * random.uniform(0.2,0.4)

            tiempo += dur

    # capas
    audio = agregar_acordes(audio, progresion, sr, duracion)
    audio = agregar_bajo(audio, escala, sr, duracion)
    audio = agregar_bateria(audio, sr, duracion)

    # normalizar
    audio = audio / np.max(np.abs(audio))

    buffer = io.BytesIO()
    write(buffer, sr, (audio * 32767).astype(np.int16))
    buffer.seek(0)

    return buffer

# ---------------- GENERADOR PRINCIPAL ----------------
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

    progresion = [
        [escala[0],escala[2],escala[4]],
        [escala[1],escala[3],escala[4]],
        [escala[2],escala[4],escala[1]],
        [escala[0],escala[2],escala[4]]
    ]

    return generar_track(escala, progresion)

# ---------------- UI ----------------
msg = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and msg:

    if msg.lower().startswith("/dj"):

        partes = msg.lower().split()

        generos = ["trap","lofi","rock","electronic","cinematica"]
        genero = next((g for g in generos if g in partes), "cinematica")

        modo = "normal"
        for m in ["fast","slow","dark","happy"]:
            if m in partes:
                modo = m

        st.markdown(f"🎧 DJ Cortana: {genero} | {modo}")

        audio = generar_musica(genero, modo)

        st.success("🎼 Track generado (nivel productor)")

        st.audio(audio, format="audio/wav")

        st.download_button("⬇️ Descargar", audio, "cortana_pro.wav")

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
