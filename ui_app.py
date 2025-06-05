import streamlit as st
from lector_documentos import cargar_documento
from pln import responder_chat, responder_documento
from memoria import agregar_turno, obtener_contexto, conversacion
import pandas as pd
import os
from conexion import guardar_documento, buscar_documentos_relacionados
from utils import extraer_palabras_clave

st.set_page_config(page_title="Agente Inteligente", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>Agente Analizador y conversador</h1>
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


palabras_documentales = [
    "resume", "resumen", "de qué trata", "qué dice el documento",
    "según el documento", "basado en el documento", "el texto", "según zapata"
]


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
              st.text_area("Contenido cargado", st.session_state.documento_texto[:1500], height=200)
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
        es_documental = any(p in entrada.lower() for p in palabras_documentales)

        palabras_clave = extraer_palabras_clave(entrada)
        resumenes_relacionados = buscar_documentos_relacionados(palabras_clave)

        contexto_previos = ""
        if resumenes_relacionados:
            contexto_previos = "\n".join([f"- {r}" for r in resumenes_relacionados])
            contexto_previos = f"Basado en documentos previos:\n{contexto_previos}\n\n"

        if es_documental and documento_texto:
            if documento_texto.strip().startswith("Contenido del archivo:"):
                prompt = (
                    f"Este documento contiene una tabla de seguimiento de acciones en bolsa.\n"
                    f"{documento_texto[:2000]}\n\n"
                    f"Pregunta: {entrada}"
                )
            else:
                prompt = (
                    f"Tengo este documento:\n{documento_texto[:2000]}\n\n"
                    f"Pregunta: {entrada}"
                )
            respuesta = responder_documento(prompt)

            if "resume" in entrada.lower() or "resumen" in entrada.lower():
                nombre_archivo = archivo.name if archivo else "desconocido"
                tipo_doc = nombre_archivo.split(".")[-1] if "." in nombre_archivo else "desconocido"
                guardar_documento(nombre_archivo, documento_texto, respuesta, tipo_doc)

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
