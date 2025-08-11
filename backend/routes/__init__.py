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

from .state import bp_state
from .next import bp_next
from .run import bp_run
from .reset_balances import bp_reset_balances
from .clear_history import bp_clear_history
from .set_price import bp_set_price
from .remove_person import bp_remove_person

def register_blueprints(app):
    """
    Register all API blueprints with the given Flask application instance.

    Args:
        app (Flask): The Flask application object.

    Behavior:
        - Attaches all imported blueprints to the app instance.
        - Each blueprint defines a URL prefix according to its feature scope.
    """
    app.register_blueprint(bp_state)           # /api/state
    app.register_blueprint(bp_next)            # /api/next
    app.register_blueprint(bp_run)             # /api/run
    app.register_blueprint(bp_reset_balances)  # /api/reset-balances
    app.register_blueprint(bp_clear_history)   # /api/clear-history
    app.register_blueprint(bp_set_price)       # /api/set-price
    app.register_blueprint(bp_remove_person)   # /api/remove-person
