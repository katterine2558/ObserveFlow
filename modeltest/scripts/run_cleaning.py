import sys
import os
import pandas as pd

# Ajustar PYTHONPATH para incluir el directorio src
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from cleaning_module import extract_pages, clean_pages, structure_blocks

def main():
    if len(sys.argv) < 2:
        print("Uso: run_cleaning.py <ruta_pdf> [<salida.xlsx>] [<ocr_thr>] [<min_len>] [<hdr_repeat>]")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project_root, 'data', 'processed', 'cleaned.xlsx')
    ocr_thr = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    min_len = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    hdr_rep = int(sys.argv[5]) if len(sys.argv) > 5 else 2

    pages = extract_pages(pdf, ocr_thr)
    cleaned = clean_pages(pages, hdr_rep)
    blocks = structure_blocks(cleaned, min_len)

    df = pd.DataFrame(blocks)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_excel(out, index=False)
    print(f"✅ Resultado guardado en {out}")

if __name__ == '__main__':
    main()

