from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource

from app.controller.Decorators import check_permission
from app.controller.financial_data import check_param_source_annee_import, parser_import, check_file_import
from app.models.enums.AccountRole import AccountRole
from app.services.authentication.connected_user import ConnectedUser
from app.services.financial_data import import_cp

api = Namespace(name="Crédit de paiement", path='/',
                description='Api de  gestion des CP des données financières de l\'état')

auth = current_app.extensions['auth']

@api.route('/cp')
class FinancialCpImport(Resource):

    @api.expect(parser_import)
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission([AccountRole.ADMIN, AccountRole.COMPTABLE])
    @check_param_source_annee_import()
    @check_file_import()
    @api.doc(security="Bearer")
    def post(self):
        """
        Charge un fichier issue de CHorus pour enregistrer les crédits de paiements
        Les lignes sont insérés de manière asynchrone
        """
        user = ConnectedUser.from_current_token_identity()

        data = request.form
        file_cp = request.files['fichier']

        source_region = user.current_region
        task = import_cp(file_cp,source_region,int(data['annee']), user.username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import des engaments des données fiancières de l\'état en cours (taches asynchrone id = {task.id}'})
