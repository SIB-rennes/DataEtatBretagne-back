from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource

from app.controller import ErrorController
from app.controller.Decorators import check_permission
from app.controller.financial_data import check_param_source_annee_import, parser_import, check_file_import
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.models.financial.FinancialAe import FinancialAeSchema
from app.services.code_geo import BadCodeGeoException
from app.services.financial_data import import_ae, get_financial_data_ae

api = Namespace(name="Engagement", path='/',
                description='Api de  gestion des AE des données financières de l\'état')

oidc = current_app.extensions['oidc']


parser_get = get_pagination_parser(default_limit=5000)
parser_get.add_argument('code_programme', type=str, action="split", help="le code programme (BOP)")
parser_get.add_argument('code_geo', type=str, action="split", help="Le code d'une commune (5 chiffres), "
                                                                     "le numéro de département (2 caractères), "
                                                                     "le code epci (9 chiffres), "
                                                                     "le code d'arrondissement (3 ou 4 chiffres)"
                                                                     "ou le crte (préfixé par 'crte-')")
parser_get.add_argument('theme', type=str, action="split", help="Le libelle theme (si code_programme est renseigné, le theme est ignoré)")
parser_get.add_argument('siret_beneficiaire', type=str, action="split", help="Code siret d'un beneficiaire")
parser_get.add_argument('annee', type=int, action="split", help="L'année comptable")


@api.errorhandler(BadCodeGeoException)
def handle_error_input_parameter(e: BadCodeGeoException):
    return ErrorController(e.message).to_json(), 400

@api.route('/ae')
class FinancialAe(Resource):

    @api.expect(parser_import)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    @check_param_source_annee_import()
    @check_file_import()
    @api.doc(security="Bearer")
    def post(self):
        """
        Charge un fichier issue de Chorus pour enregistrer les lignes d'engagements
        Les lignes sont insérés de façon asynchrone
        """
        data = request.form

        file_ae = request.files['fichier']
        force_update = False
        if 'force_update' in data and data['force_update'] == 'true':
            force_update = True

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''
        task = import_ae(file_ae,data['code_region'],int(data['annee']), force_update, username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import des engaments des données fiancières de l\'état en cours (taches asynchrone id = {task.id}'})

    @api.expect(parser_get)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    def get(self):
        """
        Retourne les lignes d'engagements Chorus
        """
        params = parser_get.parse_args()
        page_result = get_financial_data_ae(**params)

        if page_result.items == []:
            return "", 204

        result = FinancialAeSchema(many=True).dump(page_result.items)

        return {'items': result,
                'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200


