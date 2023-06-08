from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource

from app.controller.Decorators import check_permission
from app.controller.financial_data import check_file_import, parser_import
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.services.financial_data import import_ademe

api = Namespace(name="Ademe", path='/',
                description='Api de gestion des données ADEME')

oidc = current_app.extensions['oidc']

@api.route('/ademe')
class AdemeImport(Resource):

    @api.expect(parser_import)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    @check_file_import()
    @api.doc(security="Bearer")
    def post(self):
        """
        Charge un fichier issue de l'ADEME
        Les lignes sont insérés de manière asynchrone
        """
        file_ademe = request.files['fichier']

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''

        task = import_ademe(file_ademe,username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import des  données ADEME en cours (taches asynchrone id = {task.id}'})
