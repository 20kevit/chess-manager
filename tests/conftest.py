# tests/conftest.py
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db as _db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    ctx = app.app_context()
    ctx.push()
    
    # Create tables
    _db.create_all()
    
    yield app
    
    # Teardown
    _db.session.remove()
    _db.drop_all()
    ctx.pop()

@pytest.fixture(scope='function')
def db(app):
    """Provide the database session."""
    return _db