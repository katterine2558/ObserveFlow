import os 
import re

ALLOWED_EXTENSIONS = {'pdf'}

def is_pdf_file(filename: str) -> bool:
    """
    Check if the uploaded file has a PDF extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_directory_if_not_exists(directory: str):
    """
    Create a directory if it doesn't exist.
    Useful for ensuring the UPLOAD_FOLDER is ready.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_excel_file(filename: str) -> bool:
    """
    Check if the uploaded file has an Excel extension.
    """
    allowed_extensions = {'xls', 'xlsx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def primer_token(nombre: str) -> str:
        """
        Obtiene la especialidad del nombre del archivo.
        """
        base = os.path.basename(nombre)
        return base.split("_")[0].strip() if "_" in base else os.path.splitext(base)[0].strip()

def norm_esp(s: str) -> str:
    # Normaliza: mayúsculas, espacios únicos, sin guiones bajos
    s = (s or "").strip()
    s = s.replace("_", " ")
    s = re.sub(r"[\s\-]+", " ", s)
    return s.upper()

def first_chunk_before_underscore(name: str) -> str:
    base = os.path.basename(name)            # nombre crudo que envía el cliente
    chunk = base.split("_", 1)[0]            # antes del primer "_"
    return chunk

#Encuentra la primera fila vacía en una columna específica
def _first_empty_row(ws, col=7, start=13):
    mr = ws.max_row
    if mr < start:
        return start
    # desde el final hacia arriba hasta encontrar la última no vacía
    r = mr
    while r >= start:
        v = ws.cell(row=r, column=col).value
        if v is not None and str(v).strip() != "":
            return r + 1
        r -= 1
    return start


def _norm(s: str) -> str:
    return (s or "").strip()