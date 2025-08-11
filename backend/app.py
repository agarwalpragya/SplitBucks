"""
Application Entry Point – Flask Server & Static Frontend

This module defines the Flask application factory used to:
    • Register all API blueprints.
    • Serve the built frontend (Vite/React/Vue/etc.) from /frontend/dist.
    • Configure CORS for cross-origin API access.
    • Initialize required data files with defaults before request handling.

Execution Modes:
    - When imported: Only defines `create_app()` for use in WSGI servers (e.g., gunicorn).
    - When run directly: Runs the Flask development server with config‑defined host/port/debug.

Environment:
    HOST / PORT / DEBUG are imported from `config.py`.
    Default data seeding uses `_ensure_defaults()` from the storage layer.
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes import register_blueprints
from config import HOST, PORT, DEBUG
from storage import _ensure_defaults

# ---------------------------------------------------------------------
# Paths for serving the frontend build
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
FRONTEND_BUILD_DIR = os.path.join(BASE_DIR, "..", "frontend", "dist")

def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    Behavior:
        - Sets the static folder to the built frontend dist path.
        - Configures CORS for all /api/* routes (open to all origins in dev).
        - Registers all API blueprints from the routes module.
        - Adds routes for serving the SPA index.html and static assets.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder=FRONTEND_BUILD_DIR,
        static_url_path="/"
    )

    # Allow cross-origin requests for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register all API blueprints
    register_blueprints(app)

    # -----------------------------------------------------------------
    # SPA index.html route (root)
    # -----------------------------------------------------------------
    @app.get("/")
    def serve_index():
        """
        Serve the frontend SPA's index.html if built; otherwise show a setup message.
        """
        idx = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        if os.path.exists(idx):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        return (
            "Frontend not built yet. Run `npm install && npm run build` to generate static files.",
            200
        )

    # -----------------------------------------------------------------
    # Catch-all route for SPA subpages and static files
    # -----------------------------------------------------------------
    @app.get("/<path:path>")
    def serve_static(path):
        """
        Serve frontend static assets or fallback to index.html for SPA routing.
        """
        full = os.path.join(FRONTEND_BUILD_DIR, path)

        # Serve actual file if present
        if os.path.exists(full) and os.path.isfile(full):
            return send_from_directory(FRONTEND_BUILD_DIR, path)

        # Fallback to SPA index.html for client‑side routing
        idx = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        if os.path.exists(idx):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")

        return "Not found", 404

    return app

# ---------------------------------------------------------------------
# Development server entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure backend/data exists and all defaults are initialized before starting dev server
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    _ensure_defaults()

    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
