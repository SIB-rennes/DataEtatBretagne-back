import logging

from flask import make_response
from flask_restx._http import HTTPStatus
from keycloak import KeycloakAdmin
from flask import g


from app import oidc
from flask_restx import Namespace, Resource, abort, inputs, reqparse

from app.clients.keycloack.admin_client import build_admin_client, KeycloakAdminException
from app.controller.Decorator import check_permission
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.enums.ConnectionProfile import ConnectionProfile

api = Namespace(name="users", path='/users',
                description='API for managing users')
parser_get = get_pagination_parser()
parser_get.add_argument("only_disable", type=inputs.boolean, required=False, default=False, help="Only disable user or not")


parser_search =  reqparse.RequestParser()
parser_search.add_argument("username", type=str, required=True, help="Username")

@api.route('')
class UsersManagement(Resource):
    """
    Resource for managing users.
    """
    @api.response(200, 'List of users and pagination information')
    @api.doc(security="Bearer")
    @api.expect(parser_get)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    def get(self):
        """
        Get a list of users.
        """
        p_args = parser_get.parse_args()
        page_number = p_args.get("pageNumber")
        limit = p_args.get("limit")
        if (page_number < 1 ) :
            page_number = 1
        if limit < 0:
            limit = 1

        only_disable = p_args.get("only_disable")

        logging.debug(f'[USERS] Call users get with limit {limit}, page {page_number}, only_disable {only_disable}')
        try:
            keycloak_admin = build_admin_client()
            query = {'briefRepresentation': True, 'max': limit, 'first': (page_number-1) * limit}
            if only_disable :
                query['enabled'] = False
            count_users = keycloak_admin.users_count(query)
            users = keycloak_admin.get_users(query)
            return { 'users' : users , 'pageInfo': Pagination(count_users, page_number, users.__len__()).to_json()}, 200
        except KeycloakAdminException as admin_exception:
            return admin_exception.message, 400


@api.route('/search')
class UsersSearch(Resource):

    @api.response(200, 'Search user by email/username')
    @api.doc(security="Bearer")
    @api.expect(parser_search)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def get(self):
        """
        Search users by userName
        """
        p_args = parser_search.parse_args()
        search_username = p_args.get("username")

        if search_username is None or len(search_username)  < 4:
            return {'users': []}, 200
        try:
            keycloak_admin = build_admin_client()
            query = {'briefRepresentation': True, 'enabled':True, 'search': search_username}
            users = keycloak_admin.get_users(query)
            return {'users': users}, 200
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

        if 'sub' in g.oidc_token_info and g.oidc_token_info['sub'] == uuid:
             return abort(message= "Vous ne pouvez désactiver votre utilisateur", code=HTTPStatus.BAD_REQUEST)
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
