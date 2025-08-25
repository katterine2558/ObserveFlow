from datetime import datetime
import os
import requests
import json

API_URL = "http://localhost:5000/upload" 
PDF_PATH = "docs/ejemplo.pdf"
EXCEL_PATHS = ["docs/BIM_20250508_EDMAX_BIM_ANI_Matriz_de_observaciones.xlsx", 
               "docs/ELECTRICA_20250508_EDMAX_ELE_ANI_Matriz_de_observaciones.xlsx",
               "docs/GEOL Y ESTRUCT_20250508_EDMAX_EST Y GEOL_ANI_Matriz_de_observaciones.xlsx",
               "docs/GEOMETRICO_20250327_EDMAX_ANI_Matriz_de_observaciones_Geometrico.xlsx",
               "docs/PAVIMENTOS_20250705_EDMAX_ANI_Matriz_de_observaciones.xlsx",
               "docs/SEG VIAL_20250327_EDMAX_ANI_Matriz_de_observaciones_SGV.xlsx",
               "docs/TOPOGRAFIA _20250327_EDMAX_ANI_Matriz_de_observaciones.xlsx",
               "docs/TRANSITO_20250507_EDMAX_TRAN_ANI_Matriz_de_observaciones.xlsx"
               ]

OUTPUT_JSON = "docs/output.json"

def test_upload_pdf():
    # --- Inicio del proceso
    print("--------------------------------------------------")
    print(f"[{datetime.now()}] INFO: Iniciando test de subida de PDF.")

    # --- Verificación de archivos
    if not os.path.exists(PDF_PATH):
        print(f"[{datetime.now()}] ❌ ERROR: Archivo PDF no encontrado en: {PDF_PATH}")
        return
    
    if not EXCEL_PATHS or any(not os.path.exists(xp) for xp in EXCEL_PATHS):
        print(f"[{datetime.now()}] ❌ ERROR: Uno o más archivos Excel no existen. Revisa EXCEL_PATHS.")
        return
    
    file_handles = []
    try:
        files = []

        # Preparar archivos para la solicitud
        print(f"[{datetime.now()}] INFO: Preparando archivos para enviar...")
        
        # PDF (campo 'file')
        f_pdf = open(PDF_PATH, "rb")
        file_handles.append(f_pdf)
        files.append(('file', (os.path.basename(PDF_PATH), f_pdf, 'application/pdf')))

        # Excels (campo 'excels' repetido)
        for xp in EXCEL_PATHS:
            fe = open(xp, "rb")
            file_handles.append(fe)
            files.append(('excels', (os.path.basename(xp), fe, 'application/vnd.ms-excel')))

        print(f"[{datetime.now()}] INFO: 📤 Enviando PDF: {PDF_PATH}")
        print(f"[{datetime.now()}] INFO: 📎 Enviando {len(EXCEL_PATHS)} Excel(s).")

        # --- Realizar la solicitud POST
        print(f"[{datetime.now()}] INFO: Conectando a la API en: {API_URL}")
        response = requests.post(API_URL, files=files)
        
        print(f"[{datetime.now()}] INFO: Solicitud enviada. Esperando respuesta...")
    except Exception as e:
        # Imprimir el error completo para debug
        print(f"[{datetime.now()}] ❌ EXCEPCIÓN: Ocurrió un error inesperado al enviar la solicitud.")
        print(f"[{datetime.now()}] Detalles del error: {e}")
        return
    finally:
        # --- Cerrar handles
        print(f"[{datetime.now()}] INFO: Cerrando handles de archivos...")
        for fh in file_handles:
            try:
                fh.close()
            except Exception:
                pass
        print(f"[{datetime.now()}] INFO: Handles cerrados.")
    
    # --- Procesar la respuesta
    if response.status_code == 200:
        print(f"[{datetime.now()}] ✅ ÉXITO: Respuesta recibida correctamente (Código: 200).")
        try:
            data = response.json()
            # print(f"[{datetime.now()}] DEBUG: Datos recibidos (primeros 500 caracteres): {str(data)[:500]}")

            with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"[{datetime.now()}] ✅ ÉXITO: Resultado guardado en: {OUTPUT_JSON}")
        except json.JSONDecodeError:
            print(f"[{datetime.now()}] ❌ ERROR: La respuesta no es un JSON válido. Contenido de la respuesta: {response.text}")

    else:
        print(f"[{datetime.now()}] ❌ ERROR: La API respondió con un error. Código: {response.status_code}")
        print(f"[{datetime.now()}] Mensaje de la API: {response.text}")
    
    print(f"[{datetime.now()}] INFO: Test finalizado.")
    print("--------------------------------------------------")
    
if __name__ == "__main__":
    test_upload_pdf()