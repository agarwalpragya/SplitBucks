"""
Blueprint Registration Module.

This module centralizes the import and registration of all API blueprints
used by the Flask application.

Single registrar-style approach:
    • Simplifies the app factory pattern by consolidating all route definitions.
    • Ensures consistent naming and URL namespaces.
    • Makes it easy to enable/disable feature sets.
    • Provides a clear overview of exposed endpoints.

Blueprints included:
    - State API              → GET  /api/state
    - Next Payer API         → GET  /api/next
    - Run Round API          → POST /api/run
    - Management API (unified under /api):
        • PUT    /api/users/<name>/price
        • DELETE /api/users/<name>
        • PUT    /api/balances
        • DELETE /api/history
"""

from flask import Flask

from .state import state_bp
from .next import next_bp
from .run import run_round_bp
from .mgmt import mgmt_bp  # unified management routes under /api

def register_blueprints(app: Flask) -> Flask:
    """
    Register all API blueprints with the given Flask application instance.

    Args:
        app (Flask): The Flask application object.

    Behavior:
        - Attaches all imported blueprints to the app instance.
        - Each blueprint defines a URL prefix or concrete routes as needed.
    """
    app.register_blueprint(state_bp)       # /api/state
    app.register_blueprint(next_bp)        # /api/next
    app.register_blueprint(run_round_bp)   # /api/run
    app.register_blueprint(mgmt_bp)        # /api/users/*, /api/balances, /api/history
    return app
