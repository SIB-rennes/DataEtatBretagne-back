from flask import Blueprint
from flask_restx import Api

from app.controller.ref_controller.RefCtrl import api as refApi
api_ref = Blueprint('api_ref', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ref, doc='/doc', description="API d'interrogation des référentiels", title="Référentiel",
          authorizations=authorizations)
api.add_namespace(refApi)
