import streamlit as st
import os
import json
import hashlib
import io
import random
import unicodedata
import numpy as np

from scipy.io.wavfile import write
from PIL import Image
from pypdf import PdfReader
from groq import Groq

# ==================================================
# CONFIGURACIÓN
# ==================================================

st.set_page_config(
    page_title="Cortana IA",
    page_icon="🤖",
    layout="wide"
)

# ==================================================
# ESTILOS
# ==================================================

st.markdown("""
<style>

.stApp{
    background-color:#0d1117;
    color:white;
}

[data-testid="stSidebar"]{
    background-color:#161b22;
}

.stTextInput input{
    background-color:#1f2937;
    color:white;
    border-radius:10px;
}

.stButton button{
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    border:none;
    border-radius:10px;
    padding:10px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

st.title("🤖 Cortana IA - Web")

# ==================================================
# DATABASE
# ==================================================

DB_FILE = "database.json"

# ==================================================
# API KEY
# ==================================================

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

client = Groq(api_key=API_KEY) if API_KEY else None

# ==================================================
# NORMALIZAR TEXTO
# ==================================================

def normalizar(texto):

    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = texto.encode("ascii", "ignore").decode("utf-8")

    return texto

# ==================================================
# CIFRADO CESAR
# ==================================================

def cifrado_cesar(texto, desplazamiento):

    resultado = ""

    for char in texto:

        if char.isalpha():

            ascii_base = ord('A') if char.isupper() else ord('a')

            nuevo = (
                (ord(char) - ascii_base - desplazamiento) % 26
            ) + ascii_base

            resultado += chr(nuevo)

        else:
            resultado += char

    return resultado

def detectar_cesar(texto):

    resultados = []

    for d in range(1, 26):

        intento = cifrado_cesar(texto, d)

        resultados.append(
            f"🔑 Desplazamiento {d}:\n{intento}"
        )

    return "\n\n".join(resultados)

# ==================================================
# DATABASE
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
# HASH PASSWORD
# ==================================================

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==================================================
# SESSION
# ==================================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ==================================================
# LOGIN
# ==================================================

def login():

    st.sidebar.title("🔐 Login / Register")

    modo = st.sidebar.radio(
        "Acceso",
        ["Iniciar sesión", "Registrarse"]
    )

    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    # ==================================================
    # REGISTRO
    # ==================================================

    if modo == "Registrarse":

        if st.sidebar.button("Crear cuenta"):

            if usuario == "" or password == "":
                st.sidebar.warning("Completa todos los campos")

            elif usuario in db:
                st.sidebar.error("Ese usuario ya existe")

            else:

                db[usuario] = {
                    "password": hash_pass(password),
                    "historial": [],
                    "dmg_activado": False
                }

                guardar_db(db)

                st.sidebar.success("Cuenta creada")

    # ==================================================
    # LOGIN
    # ==================================================

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
# SIN SESIÓN
# ==================================================

if st.session_state.usuario is None:

    login()

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
# ASEGURAR USUARIO
# ==================================================

if usuario not in db:

    db[usuario] = {
        "password": "",
        "historial": [],
        "dmg_activado": False
    }

if "dmg_activado" not in db[usuario]:
    db[usuario]["dmg_activado"] = False

historial = db[usuario]["historial"]

historial = historial[-50:]

# ==================================================
# DJ
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

    write(
        buffer,
        sr,
        (audio * 32767).astype(np.int16)
    )

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

Pregunta:
{msg}
"""

    mensajes = [
        {
            "role": "system",
            "content": """
Eres Cortana:
- Inteligente
- Profesional
- Clara
- Analizas archivos
- Respondes detalladamente
"""
        }
    ]

    for chat in historial[-6:]:

        mensajes.append({
            "role": "user",
            "content": chat["user"]
        })

        mensajes.append({
            "role": "assistant",
            "content": chat["bot"]
        })

    mensajes.append({
        "role": "user",
        "content": prompt
    })

    try:

        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes
        )

        return respuesta.choices[0].message.content

    except Exception as e:

        return f"❌ Error: {e}"

# ==================================================
# ARCHIVOS
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

    # TXT

    if archivo.type == "text/plain":

        contenido_archivo = archivo.read().decode("utf-8")

    # PDF

    elif archivo.type == "application/pdf":

        lector = PdfReader(archivo)

        texto_pdf = ""

        for pagina in lector.pages:
            texto_pdf += (pagina.extract_text() or "") + "\n"

        contenido_archivo = texto_pdf[:6000]

    # IMAGEN

    elif "image" in archivo.type:

        imagen = Image.open(archivo)

        st.image(imagen, caption="🖼️ Imagen cargada")

        contenido_archivo = "El usuario subió una imagen."

# ==================================================
# CHAT
# ==================================================

st.subheader("💬 Escribe un mensaje, usa /cesar o /dj")

msg = st.text_input("Mensaje")

if st.button("Enviar 🚀") and msg:

    texto = normalizar(msg)

    # ==================================================
    # D.M.G
    # ==================================================

    if "d.m.g" in texto:

        db[usuario]["dmg_activado"] = True

        guardar_db(db)

        respuesta = """
Dmw ycm mzma jcmvw mv twa lmbittma g amkzmbwa.
uq kwlqow ma dqli g Kwzbivi ma uq kwlqow.
Mv uq kwlqow, am mvkcmvbzi cvi kizbi.
Ma bc lmjmz mvkwvbizti.
Bc lmjmz vw ma zmdqaiz mt kwlqow.
makzqjqztm i Kwzbivi dizqia kwvdqvikqwvma.
Ucmzbm g zmaczzmkkqóv.
Jcmvi acmzbm!
L.U.O.
"""

    # ==================================================
    # MUERTE Y RESURRECCION
    # ==================================================

    elif (
        "muerte y resurreccion" in texto
        and db[usuario]["dmg_activado"]
    ):

        respuesta = """
Mabw ma cv qvnqmzvw. Um aqmvbw bwzbczilw. Twa uivqycíma um qvdilmv, xmzw vw um igcliv, mt uwvabzcw mabi tqjzm. G ma mt iaqovilw i bwzbczizum. Tia ttiuia kzmkmv g mabwg ibzixilw. Mabm qvnqmzvw ma ucg ozivlm g ma awtw xizi uí. vilqm um igclw kcivlw tw xmlí, twa ozqbwa vw aqzdqmzwv, xcma vilqm twa makckpw, tia amñia g amñitma awtw um lmjqtqbizwv. Vw aé aq itocqmv tmi mabw, xmzw aq ma iaí xwz nidwz igúlmvum. Mt uwvabzcw um kwvwkm g um pikm liñw, uq aivozm ma dqvw xizi ét. uqa ttivbwa vw am wgmv. mabwg ibzixilw mv cv jizzivkw, ucg pwvlw. ti wakczqlil mvbzi mv uí, twa uivqycíma um piv ijivlwvilw. kzmw ycm biujqév um bwzbcziv. uckpw bqmuxw pi xiailw g uq acnzquqmvbw awtw kzmkm. mttwa awtw um caiv, vw um kwvwkmv, itow mv mttwa mabá uit w maw kzmíi ipwzi mt maxmrw mabá zwbw, g uq qvbmzqwz zmntmrilw biujqév, cvi pmzqli ncm ijqmzbi wbzi dmh. mabwg awtw, w xcmlw kwvnqiz mv vilqm, tmiv mabw, lmakínzmvtw g ycéumvtw. lérmvum uwzqz iycí. it nqvit gw kicam mabw. gw tw oivm, awg uq xzwxqw uwvabzcw. Um aqmvbw ucg uit, vw xcmlw. Vw ycqmzw acnzqz, mabm qvnqmzvw um pi bwzbczilw xwz uckpw g um kwzzwuxqó. Lmjw acnzqz, vw ycqmzw, xmzw ma uq wjtqoikqóv. Um pm bzivanwzuilw mv cv uwvabzcw. Bwlw lm uí. Vw aé ycqév awg vq kcávbw liñw kicaw g pm kicailw. Vw lmjw mfqabqz. Mabw vw ma cv acqkqlqw. Mabi ma cvi kizbi lm UCMZBM G ZMACZZMKKQÓV. Vw ma kctxi acgi, ma uíi. Kzmw mv Lqwa, aé ycm Ét ma xmznmkbw g gw cvi makwzqi.
"""

    # ==================================================
    # DESCIFRAR CESAR
    # ==================================================

    elif texto.startswith("/cesar"):

        contenido = msg.replace("/cesar", "").strip()

        if contenido == "":

            respuesta = (
                "⚠️ Usa:\n"
                "/cesar texto_cifrado"
            )

        else:

            respuesta = detectar_cesar(contenido)

    # ==================================================
    # CREADOR
    # ==================================================

    elif (
        "danthe" in texto
        or "quien es tu creador" in texto
        or "quien te creo" in texto
        or "who is your creator" in texto
    ):

        respuesta = "👑 Mi creador es Danthe."

    # ==================================================
    # DJ
    # ==================================================

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

        respuesta = "🎵 Beat generado."

    # ==================================================
    # HELP
    # ==================================================

    elif texto.startswith("/help"):

        respuesta = """
📌 COMANDOS

/dj → Generar música
/clear → Borrar historial
/help → Ver comandos
/cesar → Resolver cifrado César
"""

    # ==================================================
    # CLEAR
    # ==================================================

    elif texto.startswith("/clear"):

        historial.clear()

        db[usuario]["historial"] = historial

        guardar_db(db)

        st.success("🧹 Historial eliminado")

        st.rerun()

    # ==================================================
    # CHAT NORMAL
    # ==================================================

    else:

        respuesta = responder(msg, contenido_archivo)

    # ==================================================
    # GUARDAR HISTORIAL
    # ==================================================

    historial.append({
        "user": msg,
        "bot": respuesta
    })

    historial = historial[-50:]

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
