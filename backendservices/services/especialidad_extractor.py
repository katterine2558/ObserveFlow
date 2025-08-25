import re
from typing import List, Dict
import pdfplumber
from app.utils.normalizer import normalize_especialidad

_HEADING = re.compile(r"^\s*(?:\d+(?:\.\d+)*\s+)?ESPECIALIDAD\s+(.+?)\s*$", re. IGNORECASE)


def extraer_especialidades(pdf_path: str) -> List[Dict[str, str]]:

    """
    Extract all heading occurrences '... ESPECIALIDAD <NAME> ...'
    Keeps every occurrence; attaches standardized name & optional sublabel.
    """
    occurences = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text:
                continue
            
            for raw_line in text.split("\n"):
                line = raw_line.strip()
                if not line:
                    continue
                
                m = _HEADING.match(line) or re.search(r"ESPECIALIDAD\s+(.+)", line, flags=re.IGNORECASE)
                if not m:
                    continue
                
                raw_name = m.group(1).strip()
                principal_std, sublabel_std, original_clean = normalize_especialidad(raw_name)

                if occurences and occurences[-1]["pagina"] == page_num and occurences[-1]["especialidad_std"] == principal_std and occurences[-1]["sublabel_std"] == sublabel_std:
                    continue
                
                occurences.append({
                    "pagina": page_num,
                    "especialidad_raw": original_clean,     # e.g., 'Eléctrica (Lado Aire)'
                    "especialidad_std": principal_std,       # e.g., 'ELECTRICA'
                    "sublabel_std": sublabel_std,            # e.g., 'LADO AIRE' or None
                })
    occurences.sort(key=lambda x: x["pagina"])
    return occurences