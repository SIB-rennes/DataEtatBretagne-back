import os
import pytest
from flask_oidc import OpenIDConnect
from app import create_app_base, db
file_path = os.path.abspath(os.getcwd())+"\database.db"

extra_config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///C:\\Users\\jolivetspresta\\Documents\\projects\\SIBSGAR\\data-transform\\tests\\database.db',
    'SECRET_KEY': "secret",
    'OIDC_CLIENT_SECRETS': "ser",
    'TESTING': True,
    "SERVER_NAME": "localhost"
}


test_app = create_app_base(extra_config_settings=extra_config, oidc=OpenIDConnect())

@pytest.fixture(scope="session")
def app():
    test_app.app_context().push()
    return test_app

@pytest.fixture(scope="session")
def test_client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def test_db(app, request):
    with app.app_context():
        db.create_all(bind_key=[None])
    def teardown():
        with app.app_context():
            # Supprimer toutes les tables après les tests
            db.drop_all(bind_key=[None])

    request.addfinalizer(teardown)
    return db



