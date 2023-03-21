from flask import Blueprint
from flask_restx import Api

from app.controller.ref_controller.RefCrte import api as crte_api
from app.controller.ref_controller.RefCentreCouts import api as centre_couts_api
api_ref = Blueprint('api_ref', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ref, doc='/doc', prefix="/api/v1", description="API de récupérations des référentiels", title="Référentiel",
          authorizations=authorizations)
api.add_namespace(crte_api)
api.add_namespace(centre_couts_api)
