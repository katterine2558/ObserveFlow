import io
import os
import re
import fitz        # PyMuPDF
from PIL import Image
import pytesseract
# Ruta al ejecutable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from collections import Counter

def extract_pages(pdf_path: str, ocr_threshold: int = 100) -> list[dict]:
    """
    Devuelve lista de dicts {'page': int, 'text': str}, 
    aplicando OCR si la extracción nativa es muy corta.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"El archivo no existe: '{pdf_path}'")
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        if len(txt) < ocr_threshold:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes()))
            txt = pytesseract.image_to_string(img, lang="spa")
        pages.append({"page": i+1, "text": txt})
    return pages

def clean_pages(pages: list[dict], header_repeat: int = 2) -> list[dict]:
    """
    Quita cabeceras/pies repetidos y normaliza espacios por página.
    """
    def remove_headers_footers(text: str) -> str:
        lines = text.split("\n")
        counts = Counter(lines)
        repeats = {l for l,c in counts.items() if c>=header_repeat and 0<len(l)<80}
        return "\n".join([l for l in lines if l not in repeats])

    def normalize(text: str) -> str:
        t = text.replace("\f", "\n")
        t = remove_headers_footers(t)
        lines = [re.sub(r"\s+"," ",l).strip() for l in t.split("\n")]
        return "\n".join([l for l in lines if l])

    cleaned = []
    for p in pages:
        cleaned.append({
            "page": p["page"],
            "text": normalize(p["text"])
        })
    return cleaned

def structure_blocks(pages: list[dict], min_paragraph_length: int = 0) -> list[dict]:
    """
    Segmenta en bloques 'Párrafo' y 'Lista', conserva 'page'.
    """
    blocks = []
    title_re = re.compile(r"^\d+(?:\.\d+)*\s+[A-ZÁÉÍÓÚÑ ]+$")
    list_re = re.compile(r"^(?:\s*[-*•]\s+|\s*\d+[\.)]\s+)")
    num_re  = re.compile(r"^[\d\s\.\,\-]+$")

    for p in pages:
        lines = p["text"].split("\n")
        page_num = p["page"]
        par = ""
        in_list = False
        buf = []

        def flush_par():
            nonlocal par
            txt = par.strip()
            txt = re.sub(r'^\d+\s+','',txt)
            if txt and not num_re.match(txt) and (not min_paragraph_length or len(txt)>=min_paragraph_length):
                blocks.append({"tipo":"Párrafo","contenido":txt,"page":page_num})
            par = ""

        def flush_list():
            nonlocal in_list, buf
            if in_list and buf:
                txt = "\n".join(b.strip() for b in buf)
                txt = re.sub(r'^\d+\s+','',txt)
                if not min_paragraph_length or len(txt)>=min_paragraph_length:
                    blocks.append({"tipo":"Lista","contenido":txt,"page":page_num})
            in_list=False
            buf=[]

        for ln in lines:
            if title_re.match(ln):
                if par: flush_par()
                flush_list()
                continue
            if list_re.match(ln):
                if not in_list:
                    if par: flush_par()
                    in_list=True
                buf.append(ln)
                continue
            if in_list:
                flush_list()
            par = (par+" "+ln).strip() if par else ln

        if par: flush_par()
        if in_list: flush_list()

    return blocks
