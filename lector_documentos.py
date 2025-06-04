import fitz  # PyMuPDF
import docx
import pandas as pd
import os

def leer_pdf(path: str) -> str:
    texto = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            texto += page.get_text()
        return texto.strip()
    except Exception as e:
        return f"Error al leer PDF: {e}"

def leer_docx(path: str) -> str:
    texto = ""
    try:
        doc = docx.Document(path)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
        return texto.strip()
    except Exception as e:
        return f"Error al leer DOCX: {e}"

def leer_excel(path: str) -> str:
    try:
        df = pd.read_excel(path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error al leer Excel: {e}"

def cargar_documento(path: str) -> str:
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".pdf":
        return leer_pdf(path)
    elif ext in [".docx"]:
        return leer_docx(path)
    elif ext in [".xls", ".xlsx"]:
        return leer_excel(path)
    else:
        return "Formato no soportado. Usa PDF, DOCX o XLS."
