"""
Pytest Fixtures – Flask Application Test Client

This module configures and exposes a reusable Flask test client fixture
for integration and endpoint tests.

Responsibilities:
    • Adjust Python path to ensure the backend application code is importable.
    • Create a Flask app instance using the application factory.
    • Provide a configured Flask test client for use in Pytest test functions.
"""

import os
import sys
import pytest

# ---------------------------------------------------------------------
# Path setup to include the backend package
# ---------------------------------------------------------------------
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ---------------------------------------------------------------------
# Application import
# ---------------------------------------------------------------------
from app import create_app

# ---------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def client():
    """
    Flask test client fixture.

    Behavior:
        - Instantiates the application using the factory method (`create_app()`).
        - Sets `app.testing = True` to enable better error reporting and disable error catching.
        - Provides the Flask test client object to test functions.

    Yields:
        flask.testing.FlaskClient: Configured test client for sending HTTP requests.
    """
    app = create_app()
    app.testing = True
    return app.test_client()
