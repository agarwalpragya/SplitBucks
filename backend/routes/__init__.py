from .state import bp_state
from .next import bp_next
from .run import bp_run
from .reset_balances import bp_reset_balances
from .clear_history import bp_clear_history
from .set_price import bp_set_price
from .remove_person import bp_remove_person

def register_blueprints(app):
    app.register_blueprint(bp_state)
    app.register_blueprint(bp_next)
    app.register_blueprint(bp_run)
    app.register_blueprint(bp_reset_balances)
    app.register_blueprint(bp_clear_history)
    app.register_blueprint(bp_set_price)
    app.register_blueprint(bp_remove_person)
