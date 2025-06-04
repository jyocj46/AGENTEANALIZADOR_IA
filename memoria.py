import json
from typing import List, Dict

conversacion: List[Dict[str, str]] = []

def agregar_turno(usuario: str, agente: str):
    conversacion.append({"usuario": usuario, "agente": agente})

def obtener_contexto() -> str:
    contexto = ""
    for turno in conversacion[-5:]:  # Solo últimos 5 intercambios
        contexto += f"Usuario: {turno['usuario']}\n"
        contexto += f"Agente: {turno['agente']}\n"
    return contexto

def guardar_en_json(archivo="conversacion.json"):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(conversacion[-50:], f, ensure_ascii=False, indent=2)

def cargar_de_json(archivo="conversacion.json"):
    global conversacion
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            conversacion = json.load(f)
    except FileNotFoundError:
        conversacion = []

# Cargar conversación automáticamente al iniciar
cargar_de_json()
