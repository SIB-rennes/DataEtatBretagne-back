import logging
import os

import requests

from flask import jsonify, current_app
from flask_restx import Namespace, Resource, reqparse, inputs
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import oidc
from app.controller.Decorators import check_permission
from app.models.enums.ConnectionProfile import ConnectionProfile

api = Namespace(name="chorus", path='/chorus',
                description='Api de délenchements des taks chorus')

parser = reqparse.RequestParser()
parser.add_argument('fichier', type=FileStorage, help="fichier à importer", location='files', required=True)
parser.add_argument('code_region', type=str, help="Code INSEE de la région émettrice du fichier chorus", required=True)
parser.add_argument('annee', type=int, help="Année d'engagement du fichier Chorus", required=True)
parser.add_argument('force_update', type=inputs.boolean, required=False, default=False, help="Force la mise à jours si la ligne existe déjà")

ALLOWED_EXTENSIONS = {'csv'}


@api.route('/update/commune')
class CommuneRef(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self):
        from app.tasks import maj_all_communes_tasks
        task = maj_all_communes_tasks.delay()
        return jsonify({
                           "statut": f'Demande de mise à jours des communes faites (taches asynchrone id = {task.id}'})

@api.route('/import/ae')
class ChorusImport(Resource):

    @api.expect(parser)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self):
        args = parser.parse_args()
        file_chorus = args['fichier']
        code_source_region = args['code_region']
        annee = args['annee']
        force_update = args['force_update']
        from app.tasks.import_chorus_tasks import import_file_ae_chorus

        if file_chorus.filename == '':
            logging.info('Pas de fichier')
            return {"statut": 'Aucun fichier importé'}, 400

        if file_chorus and allowed_file(file_chorus.filename):
            filename = secure_filename(file_chorus.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file_chorus.save(save_path)
            logging.info(f'[IMPORT CHORUS] Récupération du fichier {filename}')
            task =  import_file_ae_chorus.delay( str(save_path), code_source_region, annee, force_update)
            return jsonify({"status": f'Fichier récupéré. Demande d`import de donnée chorus AE en cours (taches asynchrone id = {task.id}'})
        else:
            logging.error(f'[IMPORT CHORUS] Fichier refusé {file_chorus.filename}')
            return {"status": 'le fichier n\'est pas un csv'}, 400



parser_line = reqparse.RequestParser()
parser_line.add_argument('json', type=str, help="ligne chorus à importer en json", required=True)
@api.route('/import/line')
class LineImport(Resource):

    @api.expect(parser_line)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self):
        args = parser_line.parse_args()
        json_line = args['json']
        from app.tasks.import_chorus_tasks import import_line_chorus_ae
        task = import_line_chorus_ae.delay(str(json_line),-1)
        return jsonify({
            "statut": f'Ligne récupéré. Demande d`import d\'une ligne chorus AE en cours (taches asynchrone id = {task.id}'})


@api.route('/siret/<siret>')
class TestSiret(Resource):
    @api.response(200, 'Success')
    def get(self, siret):
        resp = requests.get(url=current_app.config['api_siren'] + siret)
        return resp.json()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS