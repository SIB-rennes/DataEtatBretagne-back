# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.
import logging

import yaml
from flask import Flask
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ProviderMetadata, ClientMetadata
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy

from app import celeryapp, mailapp

from flask_cors import CORS


#TODO déplacer en extensions
db = SQLAlchemy()
ma = Marshmallow()
cache = Cache()

def create_app_migrate():
    import app.models

    app = create_app_base(oidc_enable=False, expose_endpoint=False)
    migrate = Migrate()

    migrate.init_app(app, db)
    return app

def create_app_api():
    return create_app_base()

def create_app_base(oidc_enable=True, expose_endpoint=True, init_celery=True, extra_config_settings=None, **kwargs) -> Flask:
    """Create a Flask application.
    """

    if extra_config_settings is None:
        extra_config_settings = {}

    logging.basicConfig(format='%(asctime)s.%(msecs)03d : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S', )
    logging.getLogger().setLevel(logging.INFO)

    # Instantiate Flask
    app = Flask(__name__)
    read_config(app,extra_config_settings)

    db.init_app(app)
    ma.init_app(app)

    # Celery
    if (init_celery) :
        celery = celeryapp.create_celery_app(app)
        celeryapp.celery = celery

        mail = mailapp.create_mail_app(app)
        mailapp.mail = mail

    # init oidc
    if oidc_enable:
        try:
            _load_oidc_config(app)
        except Exception:
            logging.exception("Impossible de charger la configuration OIDC. Merci de vérifier votre configuration.")
            raise

    # flask_restx
    app.config.update({ 'RESTX_INCLUDE_ALL_MODELS': True })
    if expose_endpoint:
        # TODO, à terme mettre un cache REDIS ou autre, utilisable pour les autres apis
        # Utiliser uniquement pour Demarche simplifie pour un POC
        cache.init_app(app,config={'CACHE_TYPE': 'SimpleCache','CACHE_DEFAULT_TIMEOUT': 300} )
        _expose_endpoint(app)
    return app

def read_config(app, extra_config_settings):
    try:
        with open('config/config.yml') as yamlfile:
            config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    except Exception:
        config_data = {}

    # Load common settings
    app.config.from_object('app.settings')
    # Load extra settings from extra_config_settings param
    app.config.update(config_data)
    # Load extra settings from extra_config_settings param
    app.config.update(extra_config_settings)

    if (app.config['DEBUG'] == True):
        app.config['SQLALCHEMY_ECHO'] = True
        logging.getLogger().setLevel(logging.DEBUG)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def _load_oidc_config(app):
    app.config.update(OIDC_REDIRECT_URI = "*")

    oidc_conf = _read_oidc_config()
    provider_name = next(iter(oidc_conf))

    client_metadata_kwargs = oidc_conf[provider_name]['client_metadata']
    provider_metadata_kwargs = oidc_conf[provider_name]['provider_metadata']

    client_metadata = ClientMetadata(**client_metadata_kwargs)
    provider_metadata = ProviderMetadata(**provider_metadata_kwargs)
    provider_config = ProviderConfiguration(
        provider_metadata=provider_metadata,
        client_metadata=client_metadata,
    )

    provider_configurations = {}
    provider_configurations[provider_name] = provider_config
    auth = OIDCAuthentication(provider_configurations, app)
    app.extensions["auth"] = auth

def _read_oidc_config() -> dict:
    with open('config/oidc.yml') as yamlfile:
        config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        return config_data
    
def _expose_endpoint(app: Flask):
    with app.app_context():
        app.wsgi_app = ProxyFix(app.wsgi_app)
        CORS(app, resources={r"*": {"origins": "*"}})

        from app.controller.financial_data import api_financial  # pour éviter les import circulaire avec oidc
        from app.controller.administration import api_administration
        from app.controller.ref_controller import api_ref
        from app.controller.apis_externes import api_apis_externes
        from app.controller.task_management import api_task
        from app.controller.proxy_nocodb import mount_blueprint  # pour éviter les import circulaire avec oidc

        app.register_blueprint(api_financial, url_prefix='/financial-data')
        app.register_blueprint(api_administration, url_prefix='/administration')
        app.register_blueprint(api_ref, url_prefix='/budget')
        app.register_blueprint(api_apis_externes, url_prefix='/apis-externes')
        app.register_blueprint(api_task, url_prefix='/task-management')

        if 'NOCODB_PROJECT' in app.config:
            for project in app.config['NOCODB_PROJECT'].items():
                app.register_blueprint(mount_blueprint(project[0]), url_prefix=f"/nocodb/{project[0]}")