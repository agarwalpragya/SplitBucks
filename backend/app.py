from flask import Flask
from flask_cors import CORS

from backend.routes import register_blueprints   # absolute import from backend package
from backend.config import HOST, PORT, DEBUG

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    register_blueprints(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
