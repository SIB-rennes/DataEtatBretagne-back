# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
import logging

import yaml
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_oidc import OpenIDConnect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy

from app import celeryapp
from app.proxy_nocodb import mount_blueprint

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
oidc = OpenIDConnect()

from flask_cors import CORS
from app.models import Chorus


def create_app(extra_config_settings={}, oidcEnable=True):
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

    # init oidc
    if oidcEnable:
        app.config.update({
            'OIDC_CLIENT_SECRETS': 'config/keycloak.json',
            'OIDC_ID_TOKEN_COOKIE_SECURE': False,
            'OIDC_REQUIRE_VERIFIED_EMAIL': False,
            'OIDC_USER_INFO_ENABLED': True,
            'OIDC_OPENID_REALM': 'nocode',
            'OIDC_SCOPES': ['openid', 'email', 'profile'],
            'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
        })
        oidc.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Celery
    celery = celeryapp.create_celery_app(app)
    celeryapp.celery = celery

    # flask_restx
    from app.controller import api_v1 # pour éviter les import circulaire avec oidc
    app.register_blueprint(api_v1, url_prefix='/')
    mount_proxy_endpoint_nocodb(app)

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

def mount_proxy_endpoint_nocodb(app):
    for project in app.config['NOCODB_PROJECT']:
        app.register_blueprint(mount_blueprint(project), url_prefix=f"/nocodb/{project}")
