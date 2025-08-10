import os
import sys
import pytest

# Add backend/ to sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app

@pytest.fixture
def client():
    """Flask test client."""
    app = create_app()
    app.testing = True
    return app.test_client()
