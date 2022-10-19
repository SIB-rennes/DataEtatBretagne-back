from flask_restx import Namespace, Resource

from app import celeryapp

api = Namespace(name="task", path='/',
                description='Donne le status de la tâche')


@api.route('/<task_id>')
class TasksStatus(Resource):
    @api.response(200, 'Success')
    def get(self, task_id):
        res = celeryapp.celery.AsyncResult(task_id)
        return res.state, 200