import json
from celery.backends.database import TaskExtended
from flask import Blueprint
from flask_restx import Api
from app import ma
from marshmallow import fields

__all__ = ('TaskResultSchema','TaskResultTraceSchema',)
class TaskResultSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TaskExtended
        exclude = ('id','queue','worker','traceback','kwargs')

    args = fields.Method("decode_args", deserialize="decode")

    def decode_args(self, obj):
        return json.loads(obj.args)

    def decode(self, value):
        return value.decode("utf-8")

class TaskResultTraceSchema(TaskResultSchema):
    class Meta:
        model = TaskExtended
        exclude = ('id','queue','worker')


from app.controller.task_management.TaskCtrl import api as taskApi

api_task = Blueprint('task_api', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_task, doc='/doc', prefix="/api/v1", description="API technique pour lancer/gérer des task", title="API task",
          authorizations=authorizations)
api.add_namespace(taskApi)