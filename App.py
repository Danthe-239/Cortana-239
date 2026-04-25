import streamlit as st
from groq import Groq
import random
import io
import numpy as np
from scipy.io.wavfile import write
import pandas as pd
from PIL import Image
import json
from pypdf import PdfReader

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

# ---------------- ARCHIVOS ----------------
st.subheader("📂 Analizar archivo")

archivo = st.file_uploader(
    "Sube un archivo",
    type=["txt","csv","json","png","jpg","jpeg","wav","pdf"]
)

contenido_archivo = None

if archivo is not None:
    try:
        # -------- TXT --------
        if archivo.type == "text/plain":
            contenido_archivo = archivo.read().decode("utf-8")
            st.success("📄 Texto cargado")

        # -------- CSV --------
        elif archivo.type == "text/csv":
            df = pd.read_csv(archivo)
            contenido_archivo = df.to_string()
            st.success("📊 CSV cargado")
            st.dataframe(df.head())

        # -------- JSON --------
        elif archivo.type == "application/json":
            data = json.load(archivo)
            contenido_archivo = json.dumps(data, indent=2)
            st.success("🧠 JSON cargado")
            st.json(data)

        # -------- PDF --------
        elif archivo.type == "application/pdf":
            reader = PdfReader(archivo)
            texto = ""

            for page in reader.pages:
                texto += (page.extract_text() or "") + "\n"

            chunks = [texto[i:i+1500] for i in range(0, len(texto), 1500)]
            contenido_archivo = chunks

            st.success(f"📄 PDF cargado ({len(reader.pages)} páginas)")

        # -------- IMAGEN (INTELIGENTE) --------
        elif "image" in archivo.type:
            img = Image.open(archivo)
            st.image(img, caption="🖼️ Imagen cargada")

            contenido_archivo = (
                "El usuario ha subido una imagen, pero no puedes verla directamente. "
                "Debes pedirle una descripción clara (objetos, personas, colores, entorno) "
                "y luego ayudarle a analizarla."
            )

            st.warning("⚠️ No puedo ver imágenes directamente.")
            st.info("💡 Escríbeme qué hay en la imagen y la analizo contigo.")

        # -------- AUDIO --------
        elif "audio" in archivo.type:
            st.audio(archivo)
            contenido_archivo = "El usuario subió un audio. Analízalo según lo que pida."

        else:
            st.warning("⚠️ Tipo de archivo no soportado")

    except Exception as e:
        st.error(f"Error leyendo archivo: {e}")

# ---------------- RESPUESTA IA ----------------
def responder(msg, contexto=None):

    if client is None:
        return "❌ API Key no configurada"

    try:

        # PDF (chunks)
        if isinstance(contexto, list):
            texto_usado = ""
            for chunk in contexto[:3]:
                texto_usado += chunk + "\n"

            prompt = f"""
Documento:
{texto_usado}

Pregunta:
{msg}
"""

        # Otros archivos
        elif contexto:
            prompt = f"""
{contexto}

Usuario dice:
{msg}

Responde de forma útil.
Si es una imagen, no inventes: pide detalles.
"""

        else:
            prompt = msg

        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA útil, clara y honesta."},
                {"role": "user", "content": prompt}
            ]
        )

        return r.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------- AUDIO ----------------
def nota_a_freq(n):
    return 440 * (2 ** ((n - 69) / 12))

def onda(tipo, freq, t):
    if tipo == "sine":
        return np.sin(2*np.pi*freq*t)
    elif tipo == "square":
        return np.sign(np.sin(2*np.pi*freq*t))
    else:
        return 2*(t*freq - np.floor(0.5+t*freq))

# ---------------- MUSICA ----------------
def crear_motivo(escala):
    return [(random.choice(escala), random.choice([0.5,1,1.5])) for _ in range(random.randint(4,6))]

def transformar_motivo(m):
    tipo = random.choice(["invertir","retro","expandir","saltar","variar"])
    nuevo = []

    if tipo == "invertir":
        base = m[0][0]
        for n,d in m:
            nuevo.append((base-(n-base), d))
    elif tipo == "retro":
        nuevo = list(reversed(m))
    elif tipo == "expandir":
        for n,d in m:
            nuevo.append((n,d*2))
    elif tipo == "saltar":
        for n,d in m:
            nuevo.append((n+random.choice([-5,5,7]), d))
    else:
        for n,d in m:
            nuevo.append((n+random.choice([-2,-1,1,2]), d))

    return nuevo

def generar_melodia(escala):
    m1 = crear_motivo(escala)
    m2 = crear_motivo(escala)
    return m1 + transformar_motivo(m1) + m2 + transformar_motivo(m2)

def agregar_bajo(audio, escala, sr, dur):
    t = np.linspace(0, dur, int(sr*dur))
    freq = nota_a_freq(random.choice(escala[:2]) - 12)
    audio += np.sin(2*np.pi*freq*t) * 0.2
    return audio

def agregar_bateria(audio, sr, dur):
    t = np.linspace(0, dur, int(sr*dur))
    kick = (np.sin(2*np.pi*60*t)*(np.sin(2*np.pi*2*t)>0))*0.3
    snare = (np.random.randn(len(t))*(np.sin(2*np.pi*1*t)>0))*0.1
    audio += kick + snare
    return audio

def agregar_acordes(audio, prog, sr, dur):
    t = np.linspace(0, dur, int(sr*dur))
    step = dur/len(prog)

    for i,acorde in enumerate(prog):
        ini = int(i*step*sr)
        fin = int((i+1)*step*sr)

        for n in acorde:
            audio[ini:fin] += np.sin(2*np.pi*nota_a_freq(n)*t[ini:fin])*0.1

    return audio

def generar_track(escala, prog, dur=18, sr=44100):
    t = np.linspace(0, dur, int(sr*dur))
    audio = np.zeros_like(t)

    tipo = random.choice(["sine","square","saw"])
    melodia = generar_melodia(escala)

    tiempo = 0
    for n,d in melodia:
        ini = int(tiempo*sr)
        fin = int((tiempo+d)*sr)
        if fin > len(audio): break

        audio[ini:fin] += onda(tipo, nota_a_freq(n), t[ini:fin])*random.uniform(0.2,0.4)
        tiempo += d

    audio = agregar_acordes(audio, prog, sr, dur)
    audio = agregar_bajo(audio, escala, sr, dur)
    audio = agregar_bateria(audio, sr, dur)

    audio /= np.max(np.abs(audio))

    buf = io.BytesIO()
    write(buf, sr, (audio*32767).astype(np.int16))
    buf.seek(0)
    return buf

def generar_musica(genero, modo):
    escalas = {
        "cinematica":[48,50,52,55,57],
        "trap":[60,63,65,67,70],
        "lofi":[60,62,63,67,69],
        "rock":[52,55,57,59,62],
        "electronic":[60,64,67,71]
    }

    escala = escalas.get(genero, [60,62,64,67,69])

    if modo == "dark":
        escala = [n-2 for n in escala]
    elif modo == "happy":
        escala = [n+2 for n in escala]

    prog = [
        [escala[0],escala[2],escala[4]],
        [escala[1],escala[3],escala[4]],
        [escala[2],escala[4],escala[1]],
        [escala[0],escala[2],escala[4]]
    ]

    return generar_track(escala, prog)

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

        st.audio(audio, format="audio/wav")
        st.download_button("⬇️ Descargar", audio, "cortana_pro.wav")

    else:

        if "danthe" in msg.lower():
            st.markdown("👑 Danthe es mi creador.")

        respuesta = responder(msg, contenido_archivo)

        st.session_state.historial.append(("Tú", msg))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- HISTORIAL ----------------
for autor, texto in st.session_state.historial:
    st.markdown(f"{'🧑' if autor=='Tú' else '🤖'} {texto}")
