
from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, reqparse, inputs
from werkzeug.datastructures import FileStorage

from app import celeryapp
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.controller.Decorators import check_permission
from app.services import ReferentielNotFound, FileNotAllowedException, import_refs

api = Namespace(name="task", path='/',
                description='Gestion des task asynchrone')
oidc = current_app.extensions['oidc']


@api.route('/status/<task_id>')
class TaskStatus(Resource):
    @api.response(200, 'Success')
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def get(self, task_id):
        res = celeryapp.celery.AsyncResult(task_id)
        return res.state, 200





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
            task = import_refs(file, data)
            return jsonify(
                {"status": f'Fichier récupéré. Demande d`import du referentiel (taches asynchrone id = {task.id}'})
        except ReferentielNotFound:
            return "Referentiel n'existe pas", 400
        except FileNotAllowedException:
            return {"status": 'le fichier n\'est pas un fichier lissible'}, 400

