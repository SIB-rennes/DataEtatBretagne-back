from flask import Blueprint
from flask_restx import Api

from app.controller.proxy_nocodb.NococbCtrl import api as nsApi


def mount_blueprint(project) -> Blueprint:
    proxy_bp = Blueprint(project, __name__)
    authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
    proxy_api = Api(proxy_bp, doc='/doc', description="API proxy nocodb", title="API proxy nocodb", authorizations=authorizations)
    proxy_api.add_namespace(nsApi)
    proxy_api.description = f'API passe plats nocodb pour le projet {project}'
    return proxy_bp