import os

import pytest
from app import create_app_base, db
from sqlalchemy import create_engine, text

file_path = os.path.abspath(os.getcwd())+"\database.db"


test_app = create_app_base(oidcEnable=False, init_falsk_migrate=False,extra_config_settings=dict(SQLALCHEMY_DATABASE_URI='sqlite:///'+file_path))
@pytest.fixture(scope="session")
def app():
    return test_app

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def test_db(app, request):
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text("ATTACH DATABASE 'database.db' AS settings")) # nécessaire pour le schema settings
        db.create_all()
    def teardown():
        with app.app_context():
            # Supprimer toutes les tables après les tests
            db.drop_all()

    request.addfinalizer(teardown)
    return db



