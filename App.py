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
# CONFIGURACIÓN GENERAL
# ==================================================
st.set_page_config(page_title="Cortana IA", page_icon="🤖", layout="wide")
st.title("🤖 Cortana IA - Web")

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
# BASE DE DATOS
# ==================================================
def cargar_db():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if contenido == "":
                return {}
            return json.loads(contenido)
    except:
        return {}

def guardar_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

db = cargar_db()

# ==================================================
# SEGURIDAD
# ==================================================
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================================================
# SESIÓN
# ==================================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ==================================================
# LOGIN PROFESIONAL
# ==================================================
def login():
    st.sidebar.title("🔐 Login Profesional")

    modo = st.sidebar.radio(
        "Acceso",
        ["Iniciar sesión", "Registrarse"]
    )

    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if modo == "Registrarse":
        if st.sidebar.button("Crear cuenta"):
            if usuario == "" or password == "":
                st.sidebar.warning("Completa todos los campos")
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
# SI NO HAY SESIÓN
# ==================================================
if st.session_state.usuario is None:
    login()
    st.warning("🔒 Inicia sesión para continuar")
    st.stop()

# ==================================================
# PANEL DE USUARIO
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

    base = random.choice([220, 330, 440])

    melodia = (
        np.sin(2 * np.pi * base * t) * 0.30 +
        np.sin(2 * np.pi * (base * 1.5) * t) * 0.20 +
        np.sin(2 * np.pi * (base * 2) * t) * 0.10
    )

    percusion = np.zeros_like(t)

    for i in range(0, len(t), sr // 2):
        percusion[i:i+1500] += np.hanning(1500) * 0.9

    audio = melodia + percusion
    audio = audio / np.max(np.abs(audio))

    buffer = io.BytesIO()
    write(buffer, sr, (audio * 32767).astype(np.int16))
    buffer.seek(0)

    return buffer

# ==================================================
# IA
# ==================================================
def responder(msg, contexto=None):
    if client is None:
        return "⚠️ Configura correctamente tu GROQ_API_KEY"

    prompt = msg

    if contexto:
        prompt = f"""
Archivo cargado:
{contexto}

Pregunta del usuario:
{msg}
"""

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
Eres Cortana:
- Inteligente
- Clara
- Útil
- Profesional
- Analizas archivos
- Respondes breve y bien
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return respuesta.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {e}"

# ==================================================
# SUBIR ARCHIVOS
# ==================================================
st.subheader("📂 Analizar archivo")

archivo = st.file_uploader(
    "Sube archivo",
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
        lector = PdfReader(archivo)
        texto = ""

        for pagina in lector.pages:
            texto += (pagina.extract_text() or "") + "\n"

        contenido_archivo = texto[:6000]

    elif "image" in archivo.type:
        imagen = Image.open(archivo)
        st.image(imagen, caption="🖼️ Imagen cargada")
        contenido_archivo = "El usuario subió una imagen."

# ==================================================
# CHAT
# ==================================================
st.subheader("💬 Escribe o usa /dj")

msg = st.text_input("Mensaje")

if st.button("Enviar 🚀") and msg:

    texto = msg.lower().strip()

    # ------------------------------------------
    # RESPUESTAS SOBRE DANTHE
    # ------------------------------------------
    if (
        "danthe" in texto
        or "quien es tu creador" in texto
        or "quién es tu creador" in texto
        or "quien te creo" in texto
        or "quién te creó" in texto
        or "quien te creó" in texto
        or "who is your creator" in texto
    ):
        respuesta = "👑 Mi creador es Danthe. Fue quien me dio vida y visión."

    # ------------------------------------------
    # MODO DJ
    # ------------------------------------------
    elif texto.startswith("/dj"):

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

    # ------------------------------------------
    # CHAT NORMAL
    # ------------------------------------------
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
