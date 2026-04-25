import streamlit as st
from openai import OpenAI
import random
import io
import numpy as np
from scipy.io.wavfile import write
import pandas as pd
from PIL import Image
import json
from pypdf import PdfReader
import base64

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA PRO", page_icon="🤖")
st.title("🤖 Cortana IA PRO (Modo Definitivo)")

# ---------------- API ----------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# ---------------- MEMORIA ----------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ---------------- ARCHIVOS ----------------
st.subheader("📂 Subir archivo")

archivo = st.file_uploader(
    "Sube archivo",
    type=["txt","csv","json","png","jpg","jpeg","wav","pdf"]
)

contenido_archivo = None
imagen_base64 = None

if archivo:

    if "image" in archivo.type:
        img = Image.open(archivo)
        st.image(img)

        imagen_bytes = archivo.read()
        imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

        contenido_archivo = "imagen"

    elif archivo.type == "application/pdf":
        reader = PdfReader(archivo)
        texto = ""
        for p in reader.pages:
            texto += (p.extract_text() or "") + "\n"

        contenido_archivo = texto[:8000]
        st.success("📄 PDF cargado completo")

    elif archivo.type == "text/csv":
        df = pd.read_csv(archivo)
        st.dataframe(df.head())
        contenido_archivo = df.to_string()

    elif archivo.type == "text/plain":
        contenido_archivo = archivo.read().decode("utf-8")

    elif archivo.type == "application/json":
        contenido_archivo = json.dumps(json.load(archivo), indent=2)

    elif "audio" in archivo.type:
        st.audio(archivo)
        contenido_archivo = "audio"

# ---------------- IA ----------------
def responder(msg):

    if client is None:
        return "❌ API no configurada"

    try:

        # -------- IMAGEN REAL --------
        if contenido_archivo == "imagen" and imagen_base64:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": msg},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{imagen_base64}"
                            }
                        }
                    ]
                }]
            )

            return response.choices[0].message.content

        # -------- TEXTO / PDF --------
        else:

            prompt = f"""
Archivo:
{contenido_archivo}

Pregunta:
{msg}
""" if contenido_archivo else msg

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres Cortana, una IA avanzada multimodal."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

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

    if msg.startswith("/dj"):
        audio = generar_audio()
        st.audio(audio)
        st.download_button("Descargar", audio, "beat.wav")

    else:
        respuesta = responder(msg)
        st.session_state.historial.append(("Tú", msg))
        st.session_state.historial.append(("Cortana", respuesta))

# ---------------- HISTORIAL ----------------
for a,t in st.session_state.historial:
    st.markdown(f"{'🧑' if a=='Tú' else '🤖'} {t}")
