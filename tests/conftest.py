"""
Test configuration and fixtures.
"""
import pytest
from app import create_app
from app.extensions import db as _db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture(scope="session")
def app():
    flask_app = create_app(config_class=TestConfig)
    return flask_app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()