from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource

from app.controller.Decorators import check_permission
from app.controller.financial_data import check_param_import, parser_import
from app.models.enums.ConnectionProfile import ConnectionProfile

api = Namespace(name="Crédit de paiement", path='/',
                description='Api de  gestion des CP des données financières de l\'état')

oidc = current_app.extensions['oidc']

@api.route('/cp')
class FinancialCpImport(Resource):

    @api.expect(parser_import)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    @check_param_import()
    @api.doc(security="Bearer")
    def post(self):
        data = request.form
        file_cp = request.files['fichier']
        force_update = False
        if 'force_update' in data and data['force_update'] == 'true':
            force_update = True

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''

        #task = import_ae(file_cp,data['code_region'],int(data['annee']), force_update, username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import des engaments des données fiancières de l\'état en cours (taches asynchrone id = '})


