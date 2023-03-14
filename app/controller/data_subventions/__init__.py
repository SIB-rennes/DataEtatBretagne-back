from flask import Blueprint
from flask_restx import Api

from app.controller.data_subventions.DataSubventionsCtrl import api as dsApi
api_ds = Blueprint('api_ds', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ds, doc='/doc', description='API proxy de data subventions',
          authorizations=authorizations)

api.add_namespace(dsApi)