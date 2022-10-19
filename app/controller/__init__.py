from flask_restx import Api
from app.controller.ChorusCtrl import api as chorusApi
from app.controller.TaskCtrl import api as taskApi

api = Api(version="1.0", title="API Data transform",
          description="API de déclenchement des actions asynchrone data-transform",
          prefix="/api/v1", doc='/doc/')

api.add_namespace(chorusApi)
api.add_namespace(taskApi)