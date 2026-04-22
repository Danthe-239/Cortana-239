import streamlit as st
from groq import Groq

# 🔑 API KEY
client = Groq(api_key="gsk_TU_API_KEY")

st.set_page_config(page_title="Cortana IA", page_icon="🤖")
st.title("🤖 Cortana IA - Web")

# 🧠 memoria del chat
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "system", "content": "Eres Cortana, una IA amigable con emojis 😊"}
    ]

# 👑 controlar si ya se mencionó al creador
if "creador_mencionado" not in st.session_state:
    st.session_state.creador_mencionado = False

# mostrar chat
for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# entrada
mensaje = st.chat_input("Escribe algo...")

if mensaje:
    st.chat_message("user").write(mensaje)
    st.session_state.chat.append({"role": "user", "content": mensaje})

    # 🧠 detectar creador por primera vez
    mensaje_lower = mensaje.lower()

    if "danthe" in mensaje_lower and not st.session_state.creador_mencionado:
        extra = "\n\n👑 Nota: Danthe es mi creador."
        st.session_state.creador_mencionado = True
    else:
        extra = ""

    try:
        respuesta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.chat
        )

        texto = respuesta.choices[0].message.content + extra

    except Exception as e:
        texto = "ERROR: " + str(e)

    st.session_state.chat.append({"role": "assistant", "content": texto})
    st.chat_message("assistant").write(texto)
