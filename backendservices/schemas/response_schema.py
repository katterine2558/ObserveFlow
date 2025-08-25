from pydantic import BaseModel, Field
from typing import List
from typing import Optional

class ParagraphResult(BaseModel):
    pagina: int
    texto: str
    etiqueta: str
    especialidad: Optional[str]
    excel_file: str
    observacion_agregada: bool

class PDFResponse(BaseModel):
    resultados: List[ParagraphResult]