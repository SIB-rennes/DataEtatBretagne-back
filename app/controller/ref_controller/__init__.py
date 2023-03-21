from flask import Blueprint
from flask_restx import Api

from app.controller.ref_controller.RefCrte import api as crte_api
api_ref = Blueprint('api_ref', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ref, doc='/doc', prefix="/api/v1", description="API de récupérations des référentiels", title="Référentiel",
          authorizations=authorizations)
api.add_namespace(crte_api)
