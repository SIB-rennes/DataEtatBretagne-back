import logging

from flask import make_response, current_app
from flask_restx._http import HTTPStatus
from flask import g

from flask_restx import Namespace, Resource, abort, inputs

from app.clients.keycloack.factory import make_or_get_keycloack_admin, KeycloakConfigurationException
from app.controller import ErrorController
from app.controller.Decorators import check_permission
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.enums.AccountRole import AccountRole
from app.services.authentication.connected_user import ConnectedUser

api = Namespace(name="users", path='/users',
                description='API de gestion des utilisateurs')
parser_get = get_pagination_parser()
parser_get.add_argument("only_disable", type=inputs.boolean, required=False, default=False, help="Uniquement les utilisateurs non actif ou non")

auth = current_app.extensions['auth']

@api.errorhandler(KeycloakConfigurationException)
def handler_keycloak_exception(error):
    message = "Erreur keycloak"
    if hasattr(error, 'message'):
        message = error.message
    return ErrorController(message).to_json(), HTTPStatus.INTERNAL_SERVER_ERROR

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
        user = ConnectedUser.from_current_token_identity()

        p_args = parser_get.parse_args()
        page_number = p_args.get("page_number")
        limit = p_args.get("limit")
        if (page_number < 1 ) :
            page_number = 1
        if limit < 0:
            limit = 1
        only_disable = p_args.get("only_disable")

        logging.debug(f'[USERS] Call users get with limit {limit}, page {page_number}, only_disable {only_disable}')
        source_region = user.current_region
        groups_id = _fetch_groups(source_region)
        keycloak_admin = make_or_get_keycloack_admin()
        users = []
        for group_id in groups_id :
            users = users + keycloak_admin.get_group_members(group_id, {'briefRepresentation': True})

        if (only_disable):
            logging.debug('[USERS] get only disabled users')
            users = list(filter(lambda user: user['enabled'] == False, users))

        debut_index = (page_number - 1) * limit
        fin_index = debut_index + limit
        users_to_return = users[debut_index:fin_index]

        return {'users': users_to_return, 'pageInfo': Pagination(users.__len__(), page_number, users_to_return.__len__()).to_json()}, 200



@api.route('/<uuid>')
class UserDelete(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Utilisateur est activé')
    @api.doc(security="Bearer")
    @auth.token_auth('default', scopes_required=['openid'])
    @check_permission(AccountRole.ADMIN)
    def delete(self, uuid):
        """
          Supprime l'utilisateur si il est désactivé et appartient à la region de l'admin
        """
        user = ConnectedUser.from_current_token_identity()
        source_region = user.current_region
        logging.debug(f'[USERS] Call delete users {uuid}')
        keycloak_admin = make_or_get_keycloack_admin()
        # on récupère l'utilisateur
        user = keycloak_admin.get_user(uuid)

        # on check si l'utilisateur est bien désactivé
        if user['enabled'] == True:
            return ErrorController(
                "L'utilisateur est actif. Merci de le désactiver dans un premier temps").to_json(), HTTPStatus.BAD_REQUEST

        # on check si l'utilisateur est bien dans un groupes de la région
        if (not _user_belong_region(uuid, source_region)) :
            return ErrorController("L'utilisateur ne fait pas partie de la région").to_json(), HTTPStatus.BAD_REQUEST

        keycloak_admin.delete_user(user_id=uuid)
        return "Success", HTTPStatus.OK


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
        user = ConnectedUser.from_current_token_identity()

        logging.debug(f'[USERS] Call disable users {uuid}')
        source_region = user.current_region

        # on check si l'utilisateur est bien dans un groupes de la région
        if (not _user_belong_region(uuid, source_region)):
            return ErrorController("L'utilisateur ne fait pas partie de la région").to_json(), HTTPStatus.BAD_REQUEST

        if user.sub == uuid:
             return abort(message= "Vous ne pouvez désactiver votre utilisateur", code=HTTPStatus.FORBIDDEN)
        _update_enable_user(uuid, False)
        return make_response("", 200)

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
        user = ConnectedUser.from_current_token_identity()
        logging.debug(f'[USERS] Call enable users {uuid}')
        source_region = user.current_region
        # on check si l'utilisateur est bien dans un groupes de la région
        if (not _user_belong_region(uuid, source_region)):
            return ErrorController("L'utilisateur ne fait pas partie de la région").to_json(), HTTPStatus.BAD_REQUEST

        _update_enable_user(uuid, True)
        return make_response("", 200)


def _update_enable_user( user_uuid: str, enable: bool):
    """
    Update the enabled status of a user.
    """
    keycloak_admin = make_or_get_keycloack_admin()
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


def _user_belong_region(uuid, source_region: str) -> bool:
    '''
    Pour un uuid utilisateur, vérifie si il appartient à un groupe de la region
    :param uuid: uuid de l'utilisateur
    :param source_region:
    :return:
    '''
    keycloak_admin = make_or_get_keycloack_admin()
    # on récupères les groups de l'utilisateur
    groups_belong_user = keycloak_admin.get_user_groups(uuid)
    groups_id_belong_user = [g['id'] for g in groups_belong_user]
    # on récupère les groups de la region
    groups_id_region = _fetch_groups(source_region)
    return bool(set(groups_id_belong_user) & set(groups_id_region))
