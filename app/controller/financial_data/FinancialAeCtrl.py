from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource

from app.controller.Decorators import check_permission
from app.controller.financial_data import check_param_import, parser_import
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.services.financial_data import import_ae

api = Namespace(name="Engagement", path='/',
                description='Api de  gestion des AE des données financières de l\'état')

oidc = current_app.extensions['oidc']


@api.route('/ae')
class FinancialAeImport(Resource):

    @api.expect(parser_import)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    @check_param_import()
    @api.doc(security="Bearer")
    def post(self):
        data = request.form

        file_ae = request.files['fichier']
        force_update = False
        if 'force_update' in data and data['force_update'] == 'true':
            force_update = True

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''
        task = import_ae(file_ae,data['code_region'],int(data['annee']), force_update, username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import des engaments des données fiancières de l\'état en cours (taches asynchrone id = {task.id}'})


