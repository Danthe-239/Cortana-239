import streamlit as st
import os
import json
from groq import Groq
import random
import io
import numpy as np
from scipy.io.wavfile import write
import pandas as pd
from PIL import Image
from pypdf import PdfReader

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA Startup", page_icon="🤖")
st.title("🤖 Cortana IA - Startup Mode")

# ---------------- API ----------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# ---------------- DB ----------------
DB_FILE = "database.json"

def cargar_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = cargar_db()

# ---------------- LOGIN ----------------
st.sidebar.title("👤 Usuario")
usuario = st.sidebar.text_input("Nombre de usuario")

if not usuario:
    st.warning("⚠️ Ingresa un usuario para continuar")
    st.stop()

if usuario not in db:
    db[usuario] = {"historial": []}

historial = db[usuario]["historial"]

# ---------------- ARCHIVOS ----------------
st.subheader("📂 Subir archivo")

archivo = st.file_uploader(
    "Sube archivo",
    type=["txt","csv","json","png","jpg","jpeg","wav","pdf"]
)

contenido_archivo = None

if archivo:
    folder = f"files/{usuario}"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, archivo.name)

    with open(file_path, "wb") as f:
        f.write(archivo.getbuffer())

    try:
        if archivo.type == "text/plain":
            contenido_archivo = archivo.read().decode("utf-8")

        elif archivo.type == "text/csv":
            df = pd.read_csv(archivo)
            st.dataframe(df.head())
            contenido_archivo = df.to_string()

        elif archivo.type == "application/json":
            contenido_archivo = json.dumps(json.load(archivo), indent=2)

        elif archivo.type == "application/pdf":
            reader = PdfReader(archivo)
            texto = ""
            for p in reader.pages:
                texto += (p.extract_text() or "") + "\n"
            contenido_archivo = texto[:5000]

        elif "image" in archivo.type:
            img = Image.open(archivo)
            st.image(img)
            contenido_archivo = "El usuario subió una imagen. Pídele que la describa."

        elif "audio" in archivo.type:
            st.audio(archivo)
            contenido_archivo = "Analiza este audio"

    except Exception as e:
        st.error(f"Error leyendo archivo: {e}")

# ---------------- IA ----------------
def responder(msg, contexto=None):
    if client is None:
        return "❌ API Key no configurada"

    try:
        prompt = f"Archivo:\n{contexto}\n\nUsuario:\n{msg}" if contexto else msg

        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, una IA útil y clara."},
                {"role": "user", "content": prompt}
            ]
        )

        return r.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------- MUSICA ----------------
def generar_audio():
    sr = 44100
    t = np.linspace(0, 10, sr*10)
    audio = np.sin(2*np.pi*440*t) * 0.3

    buf = io.BytesIO()
    write(buf, sr, (audio*32767).astype(np.int16))
    buf.seek(0)
    return buf

# ---------------- UI ----------------
msg = st.text_input("💬 Escribe o usa /dj")

if st.button("Enviar 🚀") and msg:

    if msg.lower().startswith("/dj"):
        st.markdown("🎧 DJ Cortana activo")
        audio = generar_audio()
        st.audio(audio)
        st.download_button("⬇️ Descargar", audio, "beat.wav")

    else:
        if "danthe" in msg.lower():
            st.markdown("👑 Danthe es mi creador.")

        respuesta = responder(msg, contenido_archivo)

        historial.append({"user": msg, "bot": respuesta})
        guardar_db(db)

# ---------------- HISTORIAL ----------------
st.subheader("💬 Historial")

for chat in historial:
    st.markdown(f"🧑 {chat['user']}")
    st.markdown(f"🤖 {chat['bot']}")
