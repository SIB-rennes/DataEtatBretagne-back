from functools import wraps

from flask import Blueprint, request
from flask_restx import Api, reqparse, inputs
from werkzeug.datastructures import FileStorage

from app.controller.utils.Error import ErrorController
from app.exceptions.exceptions import DataRegatException, BadRequestDataRegateNum


parser_import = reqparse.RequestParser()
parser_import.add_argument('fichier', type=FileStorage, help="fichier à importer", location='files', required=True)
parser_import.add_argument('code_region', type=str, help="Code INSEE de la région émettrice du fichier",location='files', required=True)
parser_import.add_argument('annee', type=int, help="Année d'engagement du fichier Chorus",location='files', required=True)
parser_import.add_argument('force_update', type=inputs.boolean, required=False, default=False,location='files', help="Force la mise à jours si la ligne existe déjà")

def check_param_source_annee_import():
    """
    Vérifie sur la request contient les paramètres code_region et annee
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            data = request.form
            if 'code_region' not in data or 'annee' not in data:
                raise BadRequestDataRegateNum("Missing Argument code_region or annee")
            if not isinstance(int(data['annee']), int):
                raise BadRequestDataRegateNum("Missing Argument code_region or annee")
            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper

def check_file_import():
    """
    Vérifie sur la request contient un attribut fichier
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            if 'fichier' not in request.files:
                raise BadRequestDataRegateNum("Missing File")
            return func(*args, **kwargs)

        return inner_wrapper

    return wrapper


from app.controller.financial_data.FinancialAeCtrl import api as api_ae
from app.controller.financial_data.FinancialCpCtrl import api as api_cp
api_financial = Blueprint('financial_data', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_financial, doc='/doc', prefix="/api/v1", description="API de gestion des données financière", title="API Data transform",
          authorizations=authorizations)
api.add_namespace(api_ae)
api.add_namespace(api_cp)


@api_financial.errorhandler(DataRegatException)
def handle_exception(e):
    return ErrorController(e.message).to_json(), 400