from flask import Blueprint
from flask_restx import Api
from app.controller.task_management.TaskCtrl import api as taskApi

api_task = Blueprint('task_api', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_task, doc='/doc', prefix="/api/v1", description="API technique pour lancer/gérer des task", title="API task",
          authorizations=authorizations)
api.add_namespace(taskApi)