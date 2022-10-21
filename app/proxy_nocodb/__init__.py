from flask import Blueprint
from flask_restx import Api

from app.proxy_nocodb.NococbCtrl import api as nsApi


def mount_blueprint(project):
    proxy_bp = Blueprint(project, __name__)
    proxy_api = Api(proxy_bp, doc='/doc', description="API proxy nocodb", title="API proxy nocodb")
    proxy_api.add_namespace(nsApi)
    proxy_api.description = f'API passe plats nocodb pour le projet {project}'
    return proxy_bp