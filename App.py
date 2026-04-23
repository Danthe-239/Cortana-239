import streamlit as st
from groq import Groq

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# 🔐 SEGURIDAD: API KEY desde Secrets
# Previene errores 401 por hardcodeo
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("❌ Falta la API KEY en Secrets (GROQ_API_KEY)")
    st.stop()

client = Groq(api_key=api_key)

# 🧠 memoria de sesión
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "system", "content": "Eres Cortana, una IA amigable con emojis 😊"}
    ]

# 👑 creador (solo una vez)
if "creador_mencionado" not in st.session_state:
    st.session_state.creador_mencionado = False

# ---------------- MOSTRAR CHAT ----------------
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# ---------------- INPUT ----------------
mensaje = st.chat_input("Escribe algo...")

if mensaje:
    st.chat_message("user").write(mensaje)
    st.session_state.chat.append({"role": "user", "content": mensaje})

    # 🎵 DETECTAR MODO DJ POR COMANDO
    if mensaje.lower().startswith("/dj"):

        prompt = f"""
Eres DJ Cortana 🎧
Genera:
- Nombre de la canción
- Estilo musical
- Acordes
- Idea de beat

Mensaje: {mensaje}
"""

        try:
            respuesta = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            texto = respuesta.choices[0].message.content

        except Exception as e:
            texto = f"ERROR: {str(e)}"

        st.chat_message("assistant").write(texto)
        st.session_state.chat.append({"role": "assistant", "content": texto})

        # 🎹 MIDI
        midi_file = generar_midi()

        st.download_button(
            label="⬇️ Descargar Beat MIDI",
            data=midi_file,
            file_name="dj_cortana.mid",
            mime="audio/midi"
        )

    # 💬 CHAT NORMAL (PRINCIPAL)
    else:
        try:
            respuesta = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.chat
            )

            texto = respuesta.choices[0].message.content

        except Exception as e:
            texto = f"ERROR: {str(e)}"

        st.chat_message("assistant").write(texto)
        st.session_state.chat.append({"role": "assistant", "content": texto})
