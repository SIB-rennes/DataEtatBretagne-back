from flask import Blueprint
from flask_restx import Api

from app.controller.user_management.UsersManagementCtrl import api as userApi
from app.controller.user_management.PreferenceUsersCtrl import api as prefApi
api_management = Blueprint('api_management', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_management, doc='/doc', prefix="/api/v1", description="API de gestion des paramétrages et utilisateurs", title="Gestion des paramétrages/utilisateurs",
          authorizations=authorizations)
api.add_namespace(userApi)
api.add_namespace(prefApi)
