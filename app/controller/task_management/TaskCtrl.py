import json
import logging
import os

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, reqparse, fields, inputs
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import celeryapp, oidc
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.controller.Decorators import check_permission
from app.services.import_refs import _get_instance_model_by_name, ReferentielNotFound

api = Namespace(name="task", path='/',
                description='Gestion des task asynchrone')

@api.route('/status/<task_id>')
class TaskStatus(Resource):
    @api.response(200, 'Success')
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def get(self, task_id):
        res = celeryapp.celery.AsyncResult(task_id)
        return res.state, 200



ALLOWED_EXTENSIONS = {'csv','ods','xls','xlsx'}

parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, help="Fichier à joindre à la tâche", location='files', required=True)
parser.add_argument('class_name', type=str, help="Classe de referentiel", location='files', required=True)
parser.add_argument('columns', type=str, location='files', required =True, action="split")
parser.add_argument('is_csv', type=inputs.boolean, location='files', default=True)
parser.add_argument('other', type=str, help="parametre technique format json", location='files', required=False)


@api.route('/run/import_ref')
class TaskRunImportRef(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    @api.expect(parser)
    def post(self):
        data = request.form
        file = request.files['file']

        if 'class_name' not in data or 'columns' not in data:
            return "Le modèle n'existe pas ou les colonnes sont manquantes", 400

        try :
            _get_instance_model_by_name(data['class_name'])
        except ReferentielNotFound:
            return "Referentiel n'existe pas", 400
        class_name = data['class_name']
        columns = data['columns'].split(',')
        is_csv = True
        if 'is_csv' in data and data['is_csv'] == 'false':
            is_csv = False
        other_args = json.loads(data['other']) if 'other' in data else {}

        if file and allowed_file(file.filename):
            # save du fichier
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            logging.info(f'[IMPORT REF] Maj referentiel {class_name}, columns {columns}, is_csv {is_csv}, kwargs {other_args}, fichier {filename}')

            from app.services.import_refs import import_refs
            task = import_refs.delay(str(save_path), class_name, columns, is_csv, **other_args)
            return jsonify({"status": f'Fichier récupéré. Demande d`import du referentiel (taches asynchrone id = {task.id}'})
        else:
            logging.error(f'[IMPORT REF] Fichier refusé {file.filename}')
            return {"status": 'le fichier n\'est pas un fichier lissible'}, 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS