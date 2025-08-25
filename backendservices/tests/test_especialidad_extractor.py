import os
from app.services.especialidad_extractor import extraer_especialidades

PDF_PATH = "docs/ejemplo.pdf"

def test_extraer_especialidades():
    if not os.path.exists(PDF_PATH):
        print(f"❌ Archivo no encontrado: {PDF_PATH}")
        return
    
    especialidades = extraer_especialidades(PDF_PATH)

    if not especialidades:
        print("⚠️ No se encontraron especialidades en el PDF.")
    else:
        print(f"✅ Se encontraron {len(especialidades)} especialidades:\n")
        for esp in especialidades:
            print(f"📘 Página {esp['pagina']} → {esp['especialidad_raw']} → {esp['especialidad_std']} → {esp['sublabel_std']}")

if __name__ == "__main__":
    test_extraer_especialidades()