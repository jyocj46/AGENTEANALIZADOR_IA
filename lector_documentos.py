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
        return f"[ERROR PDF] {e}"

def leer_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        texto = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        return texto.strip()
    except Exception as e:
        return f"[ERROR DOCX] {e}"

def leer_excel(path: str) -> str:
    try:
        df = pd.read_excel(path)
        if df.empty:
            return "El archivo Excel está vacío."
        texto = "Contenido del archivo:\n"
        texto += df.to_string(index=False)
        return texto.strip()
    except Exception as e:
        return f"[ERROR XLSX] {e}"

def cargar_documento(path: str) -> str:
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".pdf":
        return leer_pdf(path)
    elif ext == ".docx":
        return leer_docx(path)
    elif ext in [".xls", ".xlsx"]:
        return leer_excel(path)
    else:
        return "❌ Formato no soportado. Usa PDF, DOCX o XLSX."
