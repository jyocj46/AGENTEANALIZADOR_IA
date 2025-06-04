from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    BartTokenizer, BartForConditionalGeneration,
    MarianMTModel, MarianTokenizer
)
import torch

# ==== MODELO DE CONVERSACIÓN (DialoGPT + traducción) ====
tokenizer_chat = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
modelo_chat = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
chat_history_ids = None

tokenizer_es_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")
modelo_es_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-en")

tokenizer_en_es = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
modelo_en_es = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es")

# ==== MODELO DE ANÁLISIS DE DOCUMENTOS (BART) ====
tokenizer_doc = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
modelo_doc = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")


# ==== FUNCIONES DE TRADUCCIÓN ====
def traducir_es_a_en(texto: str) -> str:
    tokens = tokenizer_es_en(texto, return_tensors="pt", truncation=True)
    traducido = modelo_es_en.generate(**tokens)
    return tokenizer_es_en.decode(traducido[0], skip_special_tokens=True)

def traducir_en_a_es(texto: str) -> str:
    tokens = tokenizer_en_es(texto, return_tensors="pt", truncation=True)
    traducido = modelo_en_es.generate(**tokens)
    return tokenizer_en_es.decode(traducido[0], skip_special_tokens=True)


# ==== RESPUESTA DEL AGENTE (TRADUCIDO) ====
def responder_chat(prompt_es: str) -> str:
    global chat_history_ids
    prompt_en = traducir_es_a_en(prompt_es)

    input_ids = tokenizer_chat.encode(prompt_en + tokenizer_chat.eos_token, return_tensors="pt")
    input_ids = torch.cat([chat_history_ids, input_ids], dim=-1) if chat_history_ids is not None else input_ids

    salida_ids = modelo_chat.generate(
        input_ids,
        max_new_tokens=60,
        pad_token_id=tokenizer_chat.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95
    )

    respuesta_en = tokenizer_chat.decode(salida_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
    respuesta_es = traducir_en_a_es(respuesta_en)
    return respuesta_es.strip()


# ==== RESPUESTA A DOCUMENTOS ====
def responder_documento(prompt_es: str) -> str:
    prompt_en = traducir_es_a_en(prompt_es)

    entrada = tokenizer_doc(prompt_en, return_tensors="pt", max_length=1024, truncation=True)
    ids_salida = modelo_doc.generate(
        entrada["input_ids"],
        num_beams=4,
        max_length=150,
        early_stopping=True
    )
    salida_en = tokenizer_doc.decode(ids_salida[0], skip_special_tokens=True)

    respuesta_es = traducir_en_a_es(salida_en)
    return respuesta_es.strip()
    