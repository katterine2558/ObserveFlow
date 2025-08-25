import traceback
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import glob
from werkzeug.utils import secure_filename
import shutil
from datetime import datetime

from app.utils.file_utils import is_pdf_file, is_excel_file , norm_esp, _norm, first_chunk_before_underscore
from app.services.pdf_extractor import extract_paragraphs
from app.services.text_cleaner import TextCleaner
from app.services.classifier import TextClassifier
from app.schemas.response_schema import PDFResponse, ParagraphResult
from app.services.especialidad_extractor import extraer_especialidades
from app.services.especialidad_matcher import asignar_especialidad
from app.services.observation_checker import excel_observation_cheker

pdf_blueprint = Blueprint('pdf', __name__)
cleaner = TextCleaner()
classifier = TextClassifier()

@pdf_blueprint.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True, "msg": "pong"})

@pdf_blueprint.route('/upload', methods=['POST'])
def upload_pdf():
    
    # Log: Iniciar el proceso
    print("--------------------------------------------------")
    print(f"[{datetime.now()}] INFO: Iniciando el proceso de subida de PDF y Excel.")

    # === PDF ===
    if 'file' not in request.files:
        print(f"[{datetime.now()}] WARNING: Fallo en la subida. No se encontró 'file' en la solicitud.")
        return jsonify({'error': 'No file part in request (PDF)'}), 400
    
    file = request.files['file']

    if file.filename == '':
        print(f"[{datetime.now()}] WARNING: Fallo en la subida. No se seleccionó ningún archivo.")
        return jsonify({'error': 'No selected file'}), 400
    
    if not is_pdf_file(file.filename):
        print(f"[{datetime.now()}] WARNING: Fallo en la subida. Archivo no es PDF: {file.filename}")
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    print(f"[{datetime.now()}] INFO: Archivo PDF recibido: {file.filename}")
    
    # === EXCELS ===
    excel_files = request.files.getlist('excels')

    if not excel_files or all(f.filename.strip() == '' for f in excel_files):
        print(f"[{datetime.now()}] WARNING: Fallo en la subida. No se proporcionaron archivos Excel.")
        return jsonify({'error': 'At least one Excel must be provided in form field "excels"'}), 400

    for xf in excel_files:
        if not is_excel_file(xf.filename):
            print(f"[{datetime.now()}] WARNING: Fallo en la subida. Archivo Excel inválido: {xf.filename}")
            return jsonify({'error': f'Invalid Excel file: {xf.filename}'}), 400
    
    print(f"[{datetime.now()}] INFO: Se recibieron {len(excel_files)} archivos Excel.")

    # Crear carpeta de exportación, si no existe.
    export_folder = current_app.config.get(
        'EXPORT_FOLDER',
        os.path.join(os.path.expanduser("~"), "Documents", "PLN-ODINSA", "Matrices")
    )
    os.makedirs(export_folder, exist_ok=True)
    print(f"[{datetime.now()}] INFO: Carpeta de exportación: {export_folder}")

    try:

        # Guardar el archivo PDF temporalmente
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)
        print(f"[{datetime.now()}] INFO: PDF guardado temporalmente en: {file_path}")



        # Guardar los Excel temporalmente e indexa por especialidad
        excel_index_path = {}  

        for xf in excel_files:
            original_raw = os.path.basename(xf.filename)        # <<-- crudo (con espacios)
            esp_key = norm_esp(first_chunk_before_underscore(original_raw))

            safe_name = secure_filename(original_raw)           # <<-- recién aquí lo saneas
            xunique = f"{uuid.uuid4()}_{safe_name}"
            xpath = os.path.join(current_app.config['UPLOAD_FOLDER'], xunique)
            xf.save(xpath)
            print(f"[{datetime.now()}] INFO: Excel '{original_raw}' (clave: {esp_key}) guardado en: {xpath}")

            # Conserva el primer Excel encontrado por especialidad
            if esp_key and esp_key not in excel_index_path:
                excel_index_path[esp_key] = xpath
                print(f"[{datetime.now()}] DEBUG: Excel asignado a la especialidad '{esp_key}'.")

        # Extraer texto OCR
        print(f"[{datetime.now()}] INFO: Iniciando extracción de párrafos...")
        raw_paragraphs = extract_paragraphs(file_path)
        print(f"[{datetime.now()}] INFO: Extracción completada. Se encontraron {len(raw_paragraphs)} párrafos.")

        # Clean text
        cleaned_paragraphs = [
            {**p, 'texto': cleaner.clean_text(p['texto'])}
            for p in raw_paragraphs
        ]
        print(f"[{datetime.now()}] INFO: Limpieza de texto completada.")

        # Clasificacion
        print(f"[{datetime.now()}] INFO: Iniciando clasificación de párrafos.")
        results = [
            {
                **p,
                'etiqueta': classifier.predict(p['texto']),
                "especialidad": None,
                "observacion_agregada": False  
            }
            for p in cleaned_paragraphs
        ]
        print(f"[{datetime.now()}] INFO: Clasificación finalizada.")

        # Extraer especialidades
        print(f"[{datetime.now()}] INFO: Iniciando extracción y asignación de especialidades.")
        especialidades = extraer_especialidades(file_path)
        for p in results:
            if p["etiqueta"].lower() == "observacion":
                p["especialidad"] = asignar_especialidad(p["pagina"], especialidades)
                # O si se desea el sublabel:
                # esp = asignar_especialidad_ext(p["pagina"], especialidades)
                # p["especialidad"] = esp["principal"]
                # p["subespecialidad"] = esp["sublabel"]
        print(f"[{datetime.now()}] INFO: Asignación de especialidades completada.")        
            
        # Mapea el texto según la especialidad y le asigna el excel correspondiente
        for p in results:
            esp = p.get("especialidad")
            if (
                p.get("etiqueta", "").lower() == "observacion"
                and esp is not None
                and esp.upper() != "DESCONOCIDA"
            ):
                esp_norm = norm_esp(esp)
                p["excel_file"] = excel_index_path.get(esp_norm, "")
            else:
                # Si no tiene especialidad o es desconocida, asigna ruta vacía
                p["excel_file"] = ""
        print(f"[{datetime.now()}] INFO: Mapeo de observaciones a archivos Excel completado.")


        #Saca los valores unicos de especialidad siempre y cuando sea observacion
        unique_especialidades = set()  
        for p in results:   
            if p.get("especialidad") and p.get("especialidad") != "DESCONOCIDA" and p.get("etiqueta", "").lower() == "observacion":
                unique_especialidades.add(p.get("especialidad"))
        print(f"[{datetime.now()}] INFO: Especialidades únicas encontradas: {unique_especialidades}")
        
        # Itera por las especialidades y agrega las observaciones
        for esp in unique_especialidades:
            print(f"[{datetime.now()}] INFO: Procesando especialidad: {esp}")
            # Filtra una sola vez los ítems de esta especialidad que sean observaciones
            items = [
                p for p in results
                if p.get("especialidad") == esp and p.get("etiqueta", "").lower() == "observacion"
            ]

            # Obtiene los textos
            textos = [p["texto"] for p in items]

            # Toma el primer excel_file NO vacío si existe; si no, usa ""
            excel_path = next((p.get("excel_file") for p in items if p.get("excel_file")), "")

            # Si no hay excel_path (cadena vacía o None), no se llama excel_observation_cheker
            if not excel_path or not textos:
                agregados_norm = set()  # vacío → nada quedó agregado
                print(f"[{datetime.now()}] INFO: Sin Excel o textos para '{esp}'. No se agregan observaciones.")
            else:
                print(f"[{datetime.now()}] INFO: Verificando {len(textos)} observaciones en Excel de '{esp}'.")
                agregados_norm = { _norm(t) for t in excel_observation_cheker(excel_path, textos) }

            # Marca si cada observación quedó agregada
            for p in items:
                p["observacion_agregada"] = _norm(p["texto"]) in agregados_norm

        print(f"[{datetime.now()}] INFO: Verificación de observaciones en Excel finalizada.")


        # Copiar los Excels temporales a Documentos 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for esp_norm_key, tmp_path in excel_index_path.items():
            if not tmp_path or not os.path.exists(tmp_path):
                print(f"[{datetime.now()}] WARNING: No se encontró el archivo temporal para la especialidad '{esp_norm_key}'.")
                continue

            # Nombre destino: <ESPECIALIDAD>_<timestamp>.xlsx
            dest_name = f"{esp_norm_key}_{timestamp}.xlsx"
            dest_path = os.path.join(export_folder, dest_name)

            # Evitar colisiones si ya existe
            if os.path.exists(dest_path):
                dest_name = f"{esp_norm_key}_{timestamp}_{uuid.uuid4().hex[:6]}.xlsx"
                dest_path = os.path.join(export_folder, dest_name)
                print(f"[{datetime.now()}] WARNING: El archivo '{dest_path}' ya existe. Se renombró a: {dest_name}")

            # Copia preservando metadata básica
            shutil.copy2(tmp_path, dest_path)
            print(f"[{datetime.now()}] INFO: Archivo Excel '{esp_norm_key}' copiado a: {dest_path}")
        print(f"[{datetime.now()}] INFO: Copia de archivos Excel a la carpeta de exportación finalizada.")

        response = PDFResponse(resultados=[
            ParagraphResult(**item) for item in results
        ])


        print(f"[{datetime.now()}] INFO: Proceso completado exitosamente. Enviando respuesta.")
        print("--------------------------------------------------")

        return response.model_dump_json(), 200
    
    except Exception as e:
        print(f"[{datetime.now()}] EXCEPTION: Ocurrió un error inesperado durante el procesamiento del PDF.")
        print(traceback.format_exc()) # Imprime el traceback completo del error
        return jsonify({'error': str(e)}), 500

    finally:
        print(f"[{datetime.now()}] INFO: Iniciando limpieza de archivos temporales.")

        # Eliminar el archivo PDF temporal
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            print(f"[{datetime.now()}] INFO: Archivo PDF temporal eliminado: {file_path}")
        
        # Eliminar los archivos Excel temporales
        if 'excel_index_path' in locals():
            for tmp_path in excel_index_path.values():
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    print(f"[{datetime.now()}] INFO: Archivo Excel temporal eliminado: {tmp_path}")
        
        print(f"[{datetime.now()}] INFO: Limpieza de archivos temporales completada.")
        print("--------------------------------------------------")

    

    
