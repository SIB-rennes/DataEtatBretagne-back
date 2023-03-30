import logging
from flask import Blueprint
from flask_restx import Api

logger = logging.getLogger(__name__)

from app.controller.apis_externes.ApisExternesCtrl import api as externalApi

api_apis_externes = Blueprint('api_apis_externes', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_apis_externes, doc='/doc', description='API proxy de data subventions',
          authorizations=authorizations)

from . import errorhandlers

api.add_namespace(externalApi)
