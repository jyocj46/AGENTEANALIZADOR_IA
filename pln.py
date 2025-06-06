from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    BartTokenizer, BartForConditionalGeneration,
    MarianMTModel, MarianTokenizer
)
import torch


tokenizer_chat = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
modelo_chat = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
chat_history_ids = None

tokenizer_es_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")
modelo_es_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-en")

tokenizer_en_es = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
modelo_en_es = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es")


tokenizer_doc = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
modelo_doc = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")



def traducir_es_a_en(texto: str) -> str:
    tokens = tokenizer_es_en(texto, return_tensors="pt", truncation=True)
    traducido = modelo_es_en.generate(**tokens)
    return tokenizer_es_en.decode(traducido[0], skip_special_tokens=True)

def traducir_en_a_es(texto: str) -> str:
    tokens = tokenizer_en_es(texto, return_tensors="pt", truncation=True)
    traducido = modelo_en_es.generate(**tokens)
    return tokenizer_en_es.decode(traducido[0], skip_special_tokens=True)



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
def responder_documento(texto_es: str) -> str:
    # Traducir texto completo a inglés
    texto_en = traducir_es_a_en(texto_es)

    # Fragmentar en bloques de 1024 tokens aproximadamente (~750 palabras)
    fragmentos = [texto_en[i:i+1500] for i in range(0, len(texto_en), 1500)]

    res_en_total = ""
    for i, frag in enumerate(fragmentos):
        entrada = tokenizer_doc(frag, return_tensors="pt", max_length=1024, truncation=True)
        ids_salida = modelo_doc.generate(
            entrada["input_ids"],
            num_beams=4,
            max_length=150,
            early_stopping=True
        )
        resumen_parcial = tokenizer_doc.decode(ids_salida[0], skip_special_tokens=True)
        res_en_total += f"{resumen_parcial} "

    # Traducir resumen final a español
    resumen_es = traducir_en_a_es(res_en_total)
    return resumen_es.strip()
