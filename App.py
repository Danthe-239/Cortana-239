import streamlit as st
import os
import json
import hashlib
from groq import Groq

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Startup Mode")

# ---------------- API ----------------
API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY) if API_KEY else None

# ---------------- DB ----------------
DB_FILE = "database.json"

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

# ---------------- SEGURIDAD ----------------
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- SESION ----------------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ---------------- LOGIN ----------------
def login_ui():
    st.sidebar.title("🔐 Login Profesional")

    opcion = st.sidebar.radio("Acceso", ["Iniciar sesión", "Registrarse"])

    usuario = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if opcion == "Registrarse":
        if st.sidebar.button("Crear cuenta"):
            if usuario in db:
                st.sidebar.error("Ese usuario ya existe")
            elif usuario == "" or password == "":
                st.sidebar.warning("Completa campos")
            else:
                db[usuario] = {
                    "password": hash_pass(password),
                    "historial": []
                }
                guardar_db(db)
                st.sidebar.success("Cuenta creada. Ahora inicia sesión.")

    if opcion == "Iniciar sesión":
        if st.sidebar.button("Entrar"):
            if usuario in db and db[usuario]["password"] == hash_pass(password):
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.sidebar.error("Usuario o contraseña incorrectos")

# ---------------- SI NO LOGUEADO ----------------
if st.session_state.usuario is None:
    login_ui()
    st.warning("🔒 Inicia sesión para continuar")
    st.stop()

# ---------------- PANEL USUARIO ----------------
usuario = st.session_state.usuario

st.sidebar.success(f"✅ Sesión iniciada: {usuario}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()

# ---------------- HISTORIAL ----------------
if usuario not in db:
    db[usuario] = {"password": "", "historial": []}

historial = db[usuario]["historial"]

# ---------------- IA ----------------
def responder(msg):
    if client is None:
        return "⚠️ Configura tu API Key."

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Cortana, inteligente, útil y clara."},
                {"role": "user", "content": msg}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# ---------------- CHAT ----------------
st.subheader("💬 Chat")

msg = st.text_input("Escribe algo")

if st.button("Enviar") and msg:
    resp = responder(msg)

    historial.append({
        "user": msg,
        "bot": resp
    })

    db[usuario]["historial"] = historial
    guardar_db(db)

# ---------------- MOSTRAR CHAT ----------------
for chat in historial[::-1]:
    st.write("🧑", chat["user"])
    st.write("🤖", chat["bot"])
    st.divider()
