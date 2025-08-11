import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes import register_blueprints
from config import HOST, PORT, DEBUG
from storage import _ensure_defaults

# Paths for serving frontend build
BASE_DIR = os.path.dirname(__file__)
FRONTEND_BUILD_DIR = os.path.join(BASE_DIR, "..", "frontend", "dist")

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_BUILD_DIR, static_url_path="/")
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    register_blueprints(app)

    # Serve frontend
    @app.get("/")
    def serve_index():
        idx = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        if os.path.exists(idx):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        return "Frontend not built yet. Run `npm install && npm run build`.", 200

    @app.get("/<path:path>")
    def serve_static(path):
        full = os.path.join(FRONTEND_BUILD_DIR, path)
        if os.path.exists(full):
            return send_from_directory(FRONTEND_BUILD_DIR, path)
        if os.path.exists(os.path.join(FRONTEND_BUILD_DIR, "index.html")):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        return "Not found", 404

    return app

if __name__ == "__main__":
    # Make sure data dir exists and defaults are seeded BEFORE starting app
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    _ensure_defaults()

    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
