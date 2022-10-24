from flask import Blueprint
from flask_restx import Api
from app.controller.ChorusCtrl import api as chorusApi
from app.controller.TaskCtrl import api as taskApi

api_v1 = Blueprint('data_transform', __name__)

api = Api(api_v1, doc='/doc', prefix="/api/v1", description="API de déclenchement des actions asynchrone data-transform", title="API Data transform")
api.add_namespace(chorusApi)
api.add_namespace(taskApi)