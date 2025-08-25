import os
from dotenv import load_dotenv

def configure_app(app):
    load_dotenv()
    app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 10 MB