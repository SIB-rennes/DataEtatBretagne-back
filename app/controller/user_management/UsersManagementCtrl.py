import logging

from flask import make_response
from flask_restx._http import HTTPStatus
from keycloak import KeycloakAdmin

from app import oidc
from flask_restx import Namespace, Resource, reqparse, abort

from app.clients.keycloack.admin_client import build_admin_client, KeycloakAdminException
from app.controller.Decorator import check_permission
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.enums.ConnectionProfile import ConnectionProfile

api = Namespace(name="users", path='/users',
                description='API for managing users')
pagination_parser = get_pagination_parser()

@api.route('/')
class UsersManagement(Resource):
    """
    Resource for managing users.
    """
    @api.response(200, 'List of users and pagination information')
    @api.doc(security="Bearer")
    @api.expect(pagination_parser)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    def get(self):
        """
        Get a list of users.
        """
        p_args = pagination_parser.parse_args()
        page_number = p_args.get("pageNumber")
        limit = p_args.get("limit")
        if (page_number < 0 ) :
            page_number = 0
        if limit < 0:
            limit = 1

        logging.debug(f'[USERS] Call users get with limit {limit}, page {page_number}')
        try:
            keycloak_admin = build_admin_client()
            count_users = keycloak_admin.users_count()
            users = keycloak_admin.get_users({'briefRepresentation': True, 'max': limit, 'first': (page_number-1) * limit})
            return { 'users' : users , 'pageInfo': Pagination(count_users, page_number, users.__len__()).to_json()}, 200
        except KeycloakAdminException as admin_exception:
            return admin_exception.message, 400

@api.route('/disable/<uuid>')
class UsersDisable(Resource):
    """
    Resource for disabling users.
    """
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    def patch(self, uuid):
        """
        Disable a user.
        """
        logging.debug(f'[USERS] Call disable users {uuid}')
        try:
            _update_enable_user(build_admin_client(), uuid, False)
            return make_response("", 200)
        except KeycloakAdminException as admin_exception:
            return abort(message= admin_exception.message, code=HTTPStatus.BAD_REQUEST)
@api.route('/enable/<uuid>')
class UsersEnable(Resource):
    """
    Resource for enabling users.
    """
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    def patch(self, uuid):
        """
        Enable a user.
        """
        logging.debug(f'[USERS] Call enable users {uuid}')
        try:
            _update_enable_user(build_admin_client(), uuid,True)
            return make_response("", 200)
        except KeycloakAdminException as admin_exception:
            return abort(message= admin_exception.message, code=HTTPStatus.BAD_REQUEST)

def _update_enable_user(keycloak_admin: KeycloakAdmin, user_uuid: str, enable: bool):
    """
    Update the enabled status of a user.
    """
    response = keycloak_admin.update_user(user_id=user_uuid,
                                              payload={'enabled': enable})
    return response
