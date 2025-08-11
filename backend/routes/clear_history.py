from flask import Blueprint, jsonify
from storage import HISTORY_FILE, reset_history, read_history, ensure_history

bp_clear_history = Blueprint("clear_history", __name__)

@bp_clear_history.post("/api/clear-history")
def api_clear_history():
    ensure_history(HISTORY_FILE)
    reset_history(HISTORY_FILE)
    return jsonify({"ok": True, "history": read_history(HISTORY_FILE)})
