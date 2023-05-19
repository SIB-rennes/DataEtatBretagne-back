import functools
import json

from celery import states
from flask import request, current_app, jsonify, g, abort
from flask_restx import Namespace, Resource, reqparse, inputs
from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import select, desc
from werkzeug.datastructures import FileStorage

from app import celeryapp
from . import TaskResultTraceSchema, TaskResultSchema
from app.models.common.Pagination import Pagination
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.controller.Decorators import check_permission
from app.services import ReferentielNotFound, FileNotAllowedException, import_refs

from celery.backends.database.models import TaskExtended

api = Namespace(name="task", path='/',
                description='Gestion des task asynchrone')
oidc = current_app.extensions['oidc']



@api.route('/task/<task_id>')
class TaskSingle(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def get(self, task_id):
        result = _get_session_celery().query(TaskExtended).filter(TaskExtended.task_id == task_id).one()
        schema = TaskResultTraceSchema()
        json = schema.dump(result)
        return json, 200


@api.route('/task/failed')
class TaskFailed(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def get(self):
        stmt = select(TaskExtended).where(TaskExtended.status == states.FAILURE).order_by(desc(TaskExtended.date_done))

        page_result = SelectPagination(
            select=stmt,
            session=_get_session_celery(),
            page=1,
            per_page=100,
            count=True,
        )
        schema = TaskResultSchema(many=True)
        return {'items': schema.dump(page_result.items),
                    'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200


@api.route('/task/run/<task_id>')
class TaskRun(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self, task_id):
        task = _get_session_celery().query(TaskExtended).filter(TaskExtended.task_id == task_id).one()
        if task is None:
            abort(404)

        args_decode = task.args.decode("utf-8")

        celeryapp.celery.send_task(task.name, args=json.loads(args_decode))
        return 200





parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, help="Fichier à joindre à la tâche", location='files', required=True)
parser.add_argument('class_name', type=str, help="Classe de referentiel", location='files', required=True)
parser.add_argument('columns', type=str, location='files', required =True, action="split")
parser.add_argument('is_csv', type=inputs.boolean, location='files', default=True)
parser.add_argument('other', type=str, help="parametre technique format json", location='files', required=False)


@api.route('/run/import-ref')
class TaskRunImportRef(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    @api.expect(parser)
    def post(self):
        data = request.form
        file_ref = request.files['file']

        if 'class_name' not in data or 'columns' not in data:
            return {"status":"Le modèle n'existe pas ou les colonnes sont manquantes"}, 400

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''
        try :
            task = import_refs(file_ref, data, username)
            return jsonify(
                {"status": f'Fichier récupéré. Demande d`import du referentiel (taches asynchrone id = {task.id}'})
        except ReferentielNotFound:
            return  {"status": "Referentiel n'existe pas"}, 400
        except FileNotAllowedException as e:
            return {"status": e.message}, 400

@api.route('/run/update-siret')
class SiretRef(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self):
        from app.tasks.siret import update_all_siret_task

        task = update_all_siret_task.delay()
        return jsonify({
            'status': f"Demande de mise à jour des siret faite. (Tâche asynchrone id {task.id})"
        })
@functools.cache
def _get_session_celery():
    return celeryapp.celery.backend.ResultSession()
