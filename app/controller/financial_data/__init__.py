from flask import Blueprint
from flask_restx import Api

from app.controller.financial_data.ChorusCtrl import api as chorusApi
from app.controller.utils.Error import ErrorController
from app.exceptions.exceptions import DataRegatException

api_financial = Blueprint('financial_data', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}


api = Api(api_financial, doc='/doc', prefix="/api/v1", description="API de gestion des données financière", title="API Data transform",
          authorizations=authorizations)
api.add_namespace(chorusApi)

@api_financial.errorhandler(DataRegatException)
def handle_exception(e):
    return ErrorController(e.message).to_json(), 400