import os
import pytest
from flask_oidc import OpenIDConnect
from app import create_app_base, db
file_path = os.path.abspath(os.getcwd())+"\database.db"
settings_path = os.path.abspath(os.getcwd())+"\settings.db"
audit_path = os.path.abspath(os.getcwd())+"\meta_audit.db"

extra_config = {
    'SQLALCHEMY_BINDS': {
        'settings':  'sqlite:///'+settings_path,
        'audit':  'sqlite:///'+audit_path,
    },
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///'+file_path,
    'SQLALCHEMY_BINDS'
    'SECRET_KEY': "secret",
    'OIDC_CLIENT_SECRETS': "ser",
    'TESTING': True,
    "SERVER_NAME": "localhost"
}


test_app = create_app_base(extra_config_settings=extra_config, oidc=OpenIDConnect())
test_app.app_context().push()
@pytest.fixture(scope="session")
def app():
    return test_app

@pytest.fixture(scope="session")
def test_client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def test_db(app, request):
    with app.app_context():
        db.create_all()
    def teardown():
        with app.app_context():
            # Supprimer toutes les tables après les tests
            db.drop_all()

    request.addfinalizer(teardown)
    return db



