# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
import logging

import yaml
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy

from app import celeryapp
from app.controller import api_v1
from app.proxy_nocodb import proxy_bp

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

from flask_cors import CORS
from app.models import Chorus


def create_app(extra_config_settings={}):
    """Create a Flask application.
    """

    logging.basicConfig(format='%(asctime)s.%(msecs)03d : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S', )
    logging.getLogger().setLevel(logging.INFO)

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

    # Celery
    celery = celeryapp.create_celery_app(app)
    celeryapp.celery = celery

    # flask_restx
    app.register_blueprint(api_v1, url_prefix='/')
    app.register_blueprint(proxy_bp, url_prefix='/proxy')

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

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False