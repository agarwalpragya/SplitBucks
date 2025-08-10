from .state import state_bp
from .payments import payments_bp
from .admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(state_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
