import logging

from flask import make_response, current_app
from flask_restx._http import HTTPStatus
from keycloak import KeycloakAdmin
from flask import g

from flask_restx import Namespace, Resource, abort, inputs

from app.clients.keycloack.factory import make_or_get_keycloack_admin, KeycloakConfigurationException
from app.controller import ErrorController
from app.controller.Decorators import check_permission
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.enums.AccountRole import AccountRole

api = Namespace(name="users", path='/users',
                description='API de gestion des utilisateurs')
parser_get = get_pagination_parser()
parser_get.add_argument("only_disable", type=inputs.boolean, required=False, default=False, help="Uniquement les utilisateurs non actif ou non")

auth = current_app.extensions['auth']

@api.route('')
class UsersManagement(Resource):
    """
    Resource for managing users.
    """
    @api.response(200, 'List of users and pagination information')
    @api.doc(security="Bearer")
    @api.expect(parser_get)
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission(AccountRole.ADMIN)
    def get(self):
        """
        Retourne la liste des utilisateurs
        """
        p_args = parser_get.parse_args()
        page_number = p_args.get("page_number")
        limit = p_args.get("limit")
        if (page_number < 1 ) :
            page_number = 1
        if limit < 0:
            limit = 1



        only_disable = p_args.get("only_disable")

        logging.debug(f'[USERS] Call users get with limit {limit}, page {page_number}, only_disable {only_disable}')
        source_region = '053' # TODO a récupérer du token
        try:
            groups_id = _fetch_groups(source_region)


            keycloak_admin = make_or_get_keycloack_admin()
            users = []
            for group_id in groups_id :
                #TODO filtrer que les enabled
                users.append(keycloak_admin.get_group_members(group_id, {'briefRepresentation': True}))

            debut_index = (page_number - 1) * limit
            fin_index = debut_index + limit
            users_to_return = users[debut_index:fin_index]

            return {'users': users_to_return, 'pageInfo': Pagination(users.__len__(), page_number, users_to_return.__len__()).to_json()}, 200
        except KeycloakConfigurationException as admin_exception:
            return abort(message=admin_exception.message, code=HTTPStatus.INTERNAL_SERVER_ERROR)




@api.route('/<uuid>')
class UserDelete(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Utilisateur est activé')
    @api.doc(security="Bearer")
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission(AccountRole.ADMIN)
    def delete(self, uuid):
        """
          Supprime l'utilisateur si il est désactivé
        """
        logging.debug(f'[USERS] Call enable users {uuid}')
        keycloak_admin = make_or_get_keycloack_admin()
        user = keycloak_admin.get_user(uuid)
        if (user['enabled'] == False):
            keycloak_admin.delete_user(user_id=uuid)
            return "Success", 200
        else :
            return ErrorController("User is enabled").to_json(), 400

@api.route('/<uuid>/disable')
class UsersDisable(Resource):

    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission(AccountRole.ADMIN)
    def patch(self, uuid):
        """
        Désactive un utilisateur
        """
        logging.debug(f'[USERS] Call disable users {uuid}')

        if 'sub' in g.current_token_identity and g.current_token_identity['sub'] == uuid:
             return abort(message= "Vous ne pouvez désactiver votre utilisateur", code=HTTPStatus.FORBIDDEN)
        try:
            _update_enable_user(make_or_get_keycloack_admin(), uuid, False)
            return make_response("", 200)
        except KeycloakConfigurationException as admin_exception:
            return abort(message= admin_exception.message, code=HTTPStatus.INTERNAL_SERVER_ERROR)
@api.route('/<uuid>/enable')
class UsersEnable(Resource):

    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission(AccountRole.ADMIN)
    def patch(self, uuid):
        """
        Active un compte utilisateur
        """
        logging.debug(f'[USERS] Call enable users {uuid}')
        try:
            _update_enable_user(make_or_get_keycloack_admin(), uuid,True)
            return make_response("", 200)
        except KeycloakConfigurationException as admin_exception:
            return abort(message= admin_exception.message, code=HTTPStatus.INTERNAL_SERVER_ERROR)

def _update_enable_user(keycloak_admin: KeycloakAdmin, user_uuid: str, enable: bool):
    """
    Update the enabled status of a user.
    """
    response = keycloak_admin.update_user(user_id=user_uuid,
                                              payload={'enabled': enable})
    return response


def _fetch_groups(source_region: str) -> list:
    '''
    Récupérer les groupes ids d'une région
    :param source_region:
    :return:
    '''
    keycloak_admin = make_or_get_keycloack_admin()
    logging.debug(f'[USERS] Get groups for region {source_region}')

    groups = keycloak_admin.get_groups({'briefRepresentation': False, 'q': f'region:{source_region}'})
    if groups is None:
        logging.warning(f'[USERS] Group for region {source_region} not found')
        return abort(message="admin_exception.message", code=HTTPStatus.BAD_REQUEST)
    groups_id = [groups[0]['id']]
    for subgroup in groups[0]['subGroups']:
        groups_id.append(subgroup['id'])
    return groups_id
