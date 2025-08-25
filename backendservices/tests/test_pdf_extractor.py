import os
from app.services.pdf_extractor import extract_paragraphs

pdf_path = "docs/ejemplo.pdf"

if not os.path.exists(pdf_path):
    print(f"ERROR: No se encontró el archivo en {pdf_path}")
else:
    results = extract_paragraphs(pdf_path)
    if results is None:
        print("ERROR: extract_paragraphs devolvió None")
    elif len(results) == 0:
        print("La función retornó una lista vacía")
    else:
        for item in results:
            print(f"Página: {item['pagina']}")
            print(f"Párrafo:\n{item['texto']}")
            print("-" * 40)
