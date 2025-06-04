import streamlit as st
from lector_documentos import cargar_documento
from pln import responder_chat, responder_documento
from memoria import agregar_turno, obtener_contexto, conversacion
import os

st.set_page_config(page_title="Agente Inteligente", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>🧠 Agente Conversacional + Documental</h1>
    <style>
        .stTextInput > div > div > input {
            font-size: 16px;
        }
        .chat-bubble {
            background-color: #e8f0fe;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 5px;
            color: #111 !important;
        }
        .stTextInput input {
            color: #000 !important;
            background-color: #fff !important;
        }
    </style>
""", unsafe_allow_html=True)

# Crear columnas
col_chat, col_doc = st.columns([2, 1])

# Inicializar variable de documento
if "documento_texto" not in st.session_state:
    st.session_state.documento_texto = ""

if "mensaje_enviado" not in st.session_state:
    st.session_state.mensaje_enviado = False


# --------------- COLUMNA DE DOCUMENTO ---------------
with col_doc:
    st.subheader("📂 Documento")
    archivo = st.file_uploader("Cargar archivo", type=["pdf", "docx", "xls", "xlsx"])
    if archivo:
        ruta_temp = f"temp/{archivo.name}"
        os.makedirs("temp", exist_ok=True)
        with open(ruta_temp, "wb") as f:
            f.write(archivo.read())
        st.session_state.documento_texto = cargar_documento(ruta_temp)
        st.success("✅ Documento cargado. Ahora puedes hacer preguntas en el chat.")

    if st.session_state.documento_texto:
        if len(st.session_state.documento_texto) < 1000:
            st.text_area("Contenido del documento", st.session_state.documento_texto, height=200)
        else:
            st.info("Documento muy largo para mostrar completo.")

# --------------- COLUMNA DE CHAT ---------------
with col_chat:
    st.subheader("💬 Conversación")

    # Mostrar historial de conversación
    for turno in conversacion[-10:]:
        st.markdown(f"<div class='chat-bubble'><b>Tú:</b> {turno['usuario']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble'><b>Agente:</b> {turno['agente']}</div>", unsafe_allow_html=True)

    # Entrada de usuario
    with st.form(key="form_chat", clear_on_submit=True):
        entrada = st.text_input("Escribe tu mensaje:", placeholder="Habla con el agente o haz preguntas sobre el documento...")
        enviar = st.form_submit_button("Enviar")

    if enviar and entrada and not st.session_state.mensaje_enviado:
        contexto = obtener_contexto()
        documento_texto = st.session_state.documento_texto

        if "resumen" in entrada.lower() and documento_texto:
            respuesta = responder_documento("Resume esto:\n" + documento_texto[:2000])
        elif documento_texto:
            prompt = f"Tengo este documento:\n{documento_texto[:2000]}\n\nPregunta: {entrada}"
            respuesta = responder_documento(prompt)
        else:
            respuesta = responder_chat(entrada)

        agregar_turno(entrada, respuesta)
        st.session_state.mensaje_enviado = True
        st.rerun()

    # Limpiar estado de envío en la siguiente ejecución
    if st.session_state.mensaje_enviado:
        st.session_state.mensaje_enviado = False

    if st.button("🗑️ Limpiar todo"):
        conversacion.clear()
        st.session_state.documento_texto = ""
        st.success("Conversación y documento eliminados.")
