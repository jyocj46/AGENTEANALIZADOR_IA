import re
import spacy    
import random

# Cargar el modelo de spaCy en español
nlp_spacy = spacy.load("es_core_news_sm")

# Diccionario de sinónimos y errores comunes
sinonimos = {
    "compu": "computadora",
    "computardora": "computadora",
    "computadoratardoro": "computadora",
    "pc": "computadora",
    "ordenador": "computadora",
    "notebook": "computadora",
    "pantaya": "pantalla",
    "no jala": "no enciende",
    "no prende": "no enciende",
    "no arranca": "no enciende",
    "no junde": "no enciende",
    "no prende la compu": "no enciende computadora",
    "mira mi compu": "",
    "no se escucha": "sin sonido",
    "no hay red": "sin internet",
    "no funciona": "no enciende",
    "pantalla oscura": "pantalla negra",
    "pantalla apagada": "pantalla negra",
    "bsod": "pantalla azul",
    "kernel panic": "pantalla azul",
    "ralentizada": "lenta",
    "se traba": "lenta",
    "se congela": "lenta",
    "se apaga": "apagada",
    "bug": "error",
    "corrupto": "dañado"
}

respuestas_genericas = [
    "Hmm... eso suena interesante, pero no lo tengo registrado aún. ¿Podrías explicarlo de otra manera?",
    "¡Uy! Aún no tengo datos sobre eso, pero estoy aprendiendo. ¿Te refieres a un problema con la computadora?",
    "No reconozco ese problema... pero dime más detalles para ayudarte.",
    "Eso suena a otra dimensión... ¿es algo técnico o estás filosofando? 😅",
    "No lo sé con certeza, pero podría estar relacionado con algo fuera de mi conocimiento técnico actual."
]

saludos_extendidos = [
  "Como estas?", "¿cómo estás", "¿cómo te encuentras", "¿cómo va todo", "cómo estás", "cómo te encuentras", "cómo va todo", "qué tal estás", "como te encuentras?", "como estas?", "COmo estas?"
]

temas_tecnicos_generales = [
    "software", "hardware", "aplicación", "programa", "sistema", "archivo", "driver", "controlador",
    "sistema operativo", "ofimática", "office", "word", "excel", "powerpoint", "teclado", "pantalla"
]

# Lista simple de términos técnicos comunes
terminos_tecnicos = ["pantalla", "internet", "audio", "encender", "no enciende", "wifi", "error", "arranca", "prende", "lenta", "azul", "negra", "reinicia", "enciende", "apaga", "ventilador", "calienta", "bateria", "usb", "disco", "memoria", "procesador", "grafica"]

saludos = ["hola", "buenos días", "buenas", "qué tal", "hey"]
agradecimientos = ["gracias", "muchas gracias", "te agradezco", "muy amable", "mil gracias", "se agradece"]

frases_amables = [
    "mira", "tengo un problema", "necesito ayuda", "podrías ayudarme", "quisiera ayuda", "te comento", "te explico", "necesito soporte", "te consulto", "necesito asistencia", "necesito soporte técnico", "Necesito soporte", "Necesito ayuda"
]


def normalizar_texto(texto):
    texto = texto.lower()
    for original, reemplazo in sinonimos.items():
        texto = texto.replace(original, reemplazo)
    return texto

def extraer_palabras_clave(texto_usuario):
    texto_usuario = normalizar_texto(texto_usuario)
    doc = nlp_spacy(texto_usuario)
    palabras_clave = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return palabras_clave

def respuesta_aleatoria():
    return random.choice(respuestas_genericas)

def es_pregunta_tecnica(texto: str) -> bool:
    palabras_clave = [
        "computadora", "pc", "laptop", "no enciende", "pantalla negra", "no funciona",
        "problema técnico", "error", "se apaga", "bug", "reparar", "diagnóstico"
    ]
    texto = texto.lower()
    return any(palabra in texto for palabra in palabras_clave)
