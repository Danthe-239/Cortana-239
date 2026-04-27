import streamlit as st
import os
import json
import hashlib
import io
import random
import numpy as np
from scipy.io.wavfile import write
from PIL import Image
from pypdf import PdfReader
from groq import Groq

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Full Startup")

DB_FILE = "database.json"

# ==================================================
# API KEY
# ==================================================
API_KEY = ""

try:
    API_KEY = st.secrets.get("GROQ_API_KEY", "")
except:
    API_KEY = ""

client = Groq(api_key=API_KEY) if API_KEY else None

# ==================================================
# DATABASE
# ==================================================
def cargar_db():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if txt == "":
                return {}
            return json.loads(txt)
    except:
        return {}

def guardar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

db = cargar_db()

# ==================================================
# SEGURIDAD
# ==================================================
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================================================
# SESION
# ==================================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ==================================================
# LOGIN PROFESIONAL
# ==================================================
def pantalla_login():
    st.sidebar.title("🔐 Login")

    modo = st.sidebar.radio(
        "Acceso",
        ["Iniciar sesión", "Registrarse"]
    )

    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if modo == "Registrarse":
        if st.sidebar.button("Crear cuenta"):
            if usuario == "" or password == "":
                st.sidebar.warning("Completa los campos")
            elif usuario in db:
                st.sidebar.error("Ese usuario ya existe")
            else:
                db[usuario] = {
                    "password": hash_pass(password),
                    "historial": []
                }
                guardar_db(db)
                st.sidebar.success("Cuenta creada")

    if modo == "Iniciar sesión":
        if st.sidebar.button("Entrar"):
            if usuario in db:
                if db[usuario]["password"] == hash_pass(password):
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.sidebar.error("Contraseña incorrecta")
            else:
                st.sidebar.error("Usuario no existe")

# ==================================================
# SI NO ESTA LOGUEADO
# ==================================================
if st.session_state.usuario is None:
    pantalla_login()
    st.warning("🔒 Inicia sesión para continuar")
    st.stop()

# ==================================================
# PANEL USUARIO
# ==================================================
usuario = st.session_state.usuario

st.sidebar.success(f"✅ Sesión iniciada: {usuario}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()

# ==================================================
# ASEGURAR USUARIO EN DB
# ==================================================
if usuario not in db:
    db[usuario] = {
        "password": "",
        "historial": []
    }

historial = db[usuario]["historial"]

# ==================================================
# DJ CORTANA
# ==================================================
def generar_beat():
    sr = 44100
    duracion = 8

    t = np.linspace(0, duracion, sr * duracion)

    freq = random.choice([220, 330, 440, 550])

    onda = (
        np.sin(2 * np.pi * freq * t) * 0.35 +
        np.sin(2 * np.pi * (freq * 0.5) * t) * 0.25 +
        np.sin(2 * np.pi * (freq * 2) * t) * 0.15
    )

    beat = np.zeros_like(t)

    for i in range(0, len(t), sr // 2):
        beat[i:i+1500] += np.hanning(1500) * 0.8

    audio = onda + beat
    audio = audio / np.max(np.abs(audio))

    buf = io.BytesIO()
    write(buf, sr, (audio * 32767).astype(np.int16))
    buf.seek(0)

    return buf

# ==================================================
# IA CHAT
# ==================================================
def responder(msg, contexto=None):
    if client is None:
        return "⚠️ Agrega tu GROQ_API_KEY"

    try:
        prompt = msg

        if contexto:
            prompt = f"Archivo o contexto:\n{contexto}\n\nPregunta:\n{msg}"

        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
Eres Cortana:
- Inteligente
- Clara
- Útil
- Analizas archivos
- Respondes bien comandos DJ
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return r.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {e}"

# ==================================================
# SUBIR ARCHIVOS
# ==================================================
st.subheader("📂 Analizar archivo")

archivo = st.file_uploader(
    "Sube un archivo",
    type=["txt", "pdf", "png", "jpg", "jpeg"]
)

contenido_archivo = None

if archivo:

    carpeta = f"files/{usuario}"
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, archivo.name)

    with open(ruta, "wb") as f:
        f.write(archivo.getbuffer())

    if archivo.type == "text/plain":
        contenido_archivo = archivo.read().decode("utf-8")

    elif archivo.type == "application/pdf":
        reader = PdfReader(archivo)
        texto = ""

        for pagina in reader.pages:
            texto += (pagina.extract_text() or "") + "\n"

        contenido_archivo = texto[:6000]

    elif "image" in archivo.type:
        img = Image.open(archivo)
        st.image(img, caption="🖼️ Imagen cargada")
        contenido_archivo = "El usuario subió una imagen. Describe y analiza visualmente según su petición."

# ==================================================
# CHAT
# ==================================================
st.subheader("💬 Escribe o usa /dj")

msg = st.text_input("Mensaje")

if st.button("Enviar 🚀") and msg:

    # ----------------------------------
    # MODO DJ
    # ----------------------------------
    if msg.lower().startswith("/dj"):

        st.success("🎧 DJ Cortana activado")

        audio = generar_beat()

        st.audio(audio)

        st.download_button(
            "⬇️ Descargar beat",
            audio,
            file_name="beat.wav",
            mime="audio/wav"
        )

        respuesta = "🎵 Beat generado correctamente."

    # ----------------------------------
    # CHAT NORMAL
    # ----------------------------------
    else:
        respuesta = responder(msg, contenido_archivo)

    historial.append({
        "user": msg,
        "bot": respuesta
    })

    db[usuario]["historial"] = historial
    guardar_db(db)

# ==================================================
# HISTORIAL
# ==================================================
st.subheader("📜 Historial")

for chat in historial[::-1]:
    st.markdown(f"🧑 **Tú:** {chat['user']}")
    st.markdown(f"🤖 **Cortana:** {chat['bot']}")
    st.divider()
