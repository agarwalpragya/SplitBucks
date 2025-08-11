"""
Blueprint Registration Module.

This module centralizes the import and registration of all API blueprints
used by the Flask application.

Having a single point for blueprint registration:
    • Ensures consistent naming and URL namespace allocation.
    • Simplifies enabling/disabling entire feature sets.
    • Helps maintain a clear overview of exposed API endpoints.

Blueprints included:
    - State API
    - Next Payer API
    - Run Round API
    - Reset Balances API
    - Clear History API
    - Set Price API
    - Remove Person API
"""

from .state import state_bp
from .next import next_bp
from .run import run_round_bp
from .reset_balances import reset_balances_bp
from .clear_history import clear_history_bp
from .set_price import set_price_bp
from .remove_person import remove_person_bp

def register_blueprints(app):
    """
    Register all API blueprints with the given Flask application instance.

    Args:
        app (Flask): The Flask application object.

    Behavior:
        - Attaches all imported blueprints to the app instance.
        - Each blueprint defines a URL prefix according to its feature scope.
    """
    app.register_blueprint(state_bp)           # /api/state
    app.register_blueprint(next_bp)            # /api/next
    app.register_blueprint(run_round_bp)             # /api/run
    app.register_blueprint(reset_balances_bp)  # /api/reset-balances
    app.register_blueprint(clear_history_bp)   # /api/clear-history
    app.register_blueprint(set_price_bp)       # /api/set-price
    app.register_blueprint(remove_person_bp)   # /api/remove-person
