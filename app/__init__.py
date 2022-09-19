# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
import yaml
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

from flask_cors import CORS
from app.models import Chorus


def create_app(extra_config_settings={}):
    """Create a Flask application.
    """
    # Instantiate Flask
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    read_config(app, extra_config_settings)

    # Setup Flask-SQLAlchemy
    db.init_app(app)
    ma.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # flask_restx
    # api.init_app(app)

    return app

def read_config(app, extra_config_settings={}):
    try:
        with open('config/config.yml') as yamlfile:
            config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    except:
        config_data = {}

        # Load common settings
    app.config.from_object('app.settings')
    # Load extra settings from extra_config_settings param
    app.config.update(config_data)
    app.config.update(extra_config_settings)

    if (app.config['DEBUG'] == True):
        app.config['SQLALCHEMY_ECHO'] = False

    if (app.config['TESTING'] != True):
        config_db = app.config['database']
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + config_db["DB_USER"] + ":" + config_db[
            'DB_PASSWORD'] + "@" \
                                                + config_db["DB_HOST"] + ":" + config_db["DB_PORT"] + "/" + config_db[
                                                    'DB_NAME']

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False