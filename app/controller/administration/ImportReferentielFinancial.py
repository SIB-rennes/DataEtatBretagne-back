"""
Controller permettant de mettre à jours certains référentiels des données Chorus à partir d'un fichier 'calculette

"""
from flask import current_app, request, jsonify, g
from flask_restx import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage

from app.controller.Decorators import check_permission
from app.exceptions.exceptions import FileNotAllowedException
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.services.import_refs import import_ref_calculette

api = Namespace(name="Referentiel", path='/referentiels',
                description='API de de mise à jours des référentiels issue de Chorus')

oidc = current_app.extensions['oidc']

parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, help="Fichier calculette", location='files', required=True)

@api.route('/')
class TaskRunImportRef(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    @api.expect(parser)
    def post(self):
        file_ref = request.files['file']

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''
        try:
            import_ref_calculette(file_ref,username)
            return jsonify(
                {"status": 'Fichier récupéré. Demande d`import du referentiel en cours'})
        except FileNotAllowedException as e:
            return {"status": e.message}, 400