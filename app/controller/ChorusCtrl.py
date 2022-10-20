import logging
import os

from flask import jsonify, current_app
from flask_restx import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

api = Namespace(name="chorus", path='/chorus',
                description='Api de délenchements des taks chorus')

parser = reqparse.RequestParser()
parser.add_argument('fichier', type=FileStorage, help="fichier à importer", location='files', required=True)

ALLOWED_EXTENSIONS = {'csv'}


@api.route('/import/ae')
class ChorusImport(Resource):

    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        file_chorus = args['fichier']
        from app.tasks.import_chorus_tasks import import_file_ae_chorus

        if file_chorus.filename == '':
            logging.info('Pas de fichier')
            return {"statut": 'Aucun fichier importé'}, 400

        if file_chorus and allowed_file(file_chorus.filename):
            filename = secure_filename(file_chorus.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file_chorus.save(save_path)
            logging.info(f'[IMPORT CHORUS] Récupération du fichier {filename}')
            task =  import_file_ae_chorus.delay( str(save_path))
            return jsonify({"statut": f'Fichier récupéré. Demande d`import de donnée chorus AE en cours (taches asynchrone id = {task.id}'})
        else:
            logging.error(f'[IMPORT CHORUS] Fichier refusé {file_chorus.filename}')
            return {"statut": 'le fichier n\'est pas un csv'}, 400



parser_line = reqparse.RequestParser()
parser_line.add_argument('json', type=str, help="ligne chorus à importer en json", required=True)
@api.route('/import/line')
class LineImport(Resource):

    @api.expect(parser_line)
    def post(self):
        args = parser_line.parse_args()
        json_line = args['json']
        from app.tasks.import_chorus_tasks import import_line_chorus_ae
        task = import_line_chorus_ae.delay(str(json_line),-1)
        return jsonify({
            "statut": f'Ligne récupéré. Demande d`import d\'une ligne chorus AE en cours (taches asynchrone id = {task.id}'})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS