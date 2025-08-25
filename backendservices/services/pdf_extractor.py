import pdfplumber
import re
from typing import List, Dict

def extract_paragraphs(pdf_path: str) -> List[Dict[str, str]]:
    """
    Extract paragraphs from each page of the PDF.
    Each paragraph is associated with the page number it came from.

    :param pdf_path: Path to the PDF file
    :return: List of dictionaries with 'pagina' and 'texto'
    """
    paragraphs = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')
                current_paragraph = ""

                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    
                    if re.search(r'[.:!?]$', stripped):
                        current_paragraph += " " + stripped
                        paragraphs.append({
                            "pagina": page_number,
                            "texto": current_paragraph.strip()
                        })
                        current_paragraph = ""
                    else:
                        current_paragraph += " " + stripped
                
                if current_paragraph.strip():
                    paragraphs.append({
                        "pagina": page_number,
                        "texto": current_paragraph.strip()
                    })

        return paragraphs

    except Exception as e:
        print(f"ERROR leyendo el PDF: {e}")
        return []  
            
        