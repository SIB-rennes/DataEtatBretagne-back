import json
import logging

from flask import request
from flask_restx import Namespace, fields, Resource, abort
from flask_restx._http import HTTPStatus
from keycloak import KeycloakAuthenticationError

from app.clients.keycloack.factory import make_or_get_keycloack_openid, KeycloakConfigurationException

api = Namespace(name="Auth Controller", path='/auth',
                description="API de récupération de jeton d'authentification")



login_fields = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})
@api.route('/login')
class Login(Resource):
    @api.response(200, 'Success')
    @api.expect(login_fields,validate=True)
    def post(self):
        body = request.data

        param = json.loads(body)
        logging.info(f"[LOGIN] Login user {param['email']}")
        try:
            client = make_or_get_keycloack_openid()
            token =  client.token(param['email'],param['password'])
            return f"{token['token_type']} {token['access_token']}", 200
        except KeycloakConfigurationException as admin_exception:
            return abort(message=admin_exception.message, code=HTTPStatus.INTERNAL_SERVER_ERROR)
        except KeycloakAuthenticationError as auth_error:
            return abort(message=auth_error.__str__(), code=HTTPStatus.FORBIDDEN)
