from flask import Blueprint
from flask_restx import Api

from app.proxy_nocodb.NococbCtrl import api as nocodbApi

proxy_bp = Blueprint('proxy', __name__)
proxyApi = Api(proxy_bp, doc='/doc', description="API proxy nocodb", title="API proxy nocodb")
proxyApi.add_namespace(nocodbApi)