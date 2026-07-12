import pytest

from app import create_app
from app.core.config import Settings


@pytest.fixture
def app():
    application = create_app(Settings(flask_env="testing"))
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()
