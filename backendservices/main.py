from flask import Flask
from flask_cors import CORS
from app.routes.pdf_routes import pdf_blueprint
from app.core.logger import configure_logger
from app.core.config import configure_app

def create_app():
    app = Flask(__name__)
    configure_app(app)
    configure_logger(app)
    CORS(app)
    app.register_blueprint(pdf_blueprint)
    return app