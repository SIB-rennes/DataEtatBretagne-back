"""
This controller defines a Flask-RESTX Namespace called "preferences" with an endpoint for managing user preferences. The `/users/preferences` path is used for the namespace. The `post` method allows to create a new preference for the current user while the `get` method allows to retrieve the list of preferences for the current user. The `oidc` library is used for authentication and the `marshmallow` library is used for input validation.

The `preference` and `preference_get` models are used to define the expected input and output for the `post` and `get` methods respectively.

The `PreferenceUsers` class, which inherits from `Resource`, is responsible for handling the `post` and `get` methods, and it has the decorators to handle the request validation, token validation, and request/response serialization.
"""
import logging
from http import HTTPStatus

from flask_restx import Namespace, Resource, fields, abort, reqparse
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy import distinct, join
from sqlalchemy.orm import joinedload, subqueryload, lazyload

from app import db, oidc
from app.clients.keycloack.admin_client import build_admin_client, KeycloakAdminException
from app.models.preference.Preference import Preference, PreferenceSchema, PreferenceFormSchema, Share

api = Namespace(name="preferences", path='/users/preferences',
                description='API for managing users preference')


preference = api.model('CreatePreference', {
    'name': fields.String(required=True, description='Name of the preference'),
    'filters':  fields.Wildcard(fields.Raw, description="JSON object representing the user's filter"),
    'shares': fields.List(fields.Nested( api.model('shares', {
        'shared_username_email': fields.String(required=True, description="Courriel d'un utilisateur"),
    }), required = False), required = False)
})

preference_get  = api.model('Preference', {
    'name': fields.String(required=True, description='Name of the preference'),
    'username': fields.String(required = True, description='Creator of the preference'),
    'uuid': fields.String(required=True, description='Uuid of the preference'),
    'filters':  fields.Wildcard(fields.Raw, description="JSON object representing the user's filter"),
    'shares': fields.List(fields.Nested( api.model('shares', {
        'shared_username_email': fields.String(required=True, description="Courriel d'un utilisateur"),
    }), required = False), required = False)
})

list_preference_get = api.model('Preference_Share', {
    'create_by_user' : fields.List(fields.Nested(preference_get)),
    'shared_with_user': fields.List(fields.Nested(preference_get))
})

@api.route('')
class PreferenceUsers(Resource):
    """
    Resource for managing users.
    """
    @api.response(200, 'The preference created', preference)
    @api.doc(security="Bearer")
    @api.expect(preference)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def post(self):
        """
        Create a new preference for the current user
        """
        logging.debug("[PREFERENCE][CTRL] Post users prefs")
        json_data = request.get_json()
        if 'username' not in g.oidc_token_info :
             return abort(message= "User not found", code=HTTPStatus.BAD_REQUEST)
        json_data['username'] = g.oidc_token_info['username']

        schema_create_validation = PreferenceFormSchema()
        try:
            data = schema_create_validation.load(json_data)
        except ValidationError as err:
            logging.error(f"[PREFERENCE][CTRL] {err.messages}")
            return {"message": "Invalid", "details": err.messages}, 400

        share_list = [Share(**share) for share in data['shares']]
        pref = Preference(username = data['username'], name = data['name'], options = data['options'], filters = data['filters'])
        pref.shares = share_list

        try:
            db.session.add(pref)
            logging.info(f'[PREFERENCE][CTRL] Adding preference for user {json_data["username"]}')
            db.session.commit()
        except Exception as e:
            logging.error("[PREFERENCE][CTRL] Error when saving preference", e)
            return abort(message= "Error when saving preference", code=HTTPStatus.BAD_REQUEST)

        return  PreferenceSchema().dump(pref)

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, "List of the user's preferences", [list_preference_get] )
    def get(self):
        """
        Retrieve the list
        """
        logging.debug("get users prefs")

        if 'username' not in g.oidc_token_info:
            return abort(message="Utilisateur introuvable", code=HTTPStatus.BAD_REQUEST)
        username = g.oidc_token_info['username']

        list_pref = Preference.query.options(lazyload(Preference.shares)).filter_by(username=username).order_by(
            Preference.id).all()
        list_pref_shared = Preference.query.join(Share).filter(Share.shared_username_email == username).distinct(Preference.id).all()

        schema = PreferenceSchema(many=True)
        create_by_user = schema.dump(list_pref)
        shared_with_user=schema.dump(list_pref_shared)
        return { 'create_by_user': create_by_user, 'shared_with_user' :shared_with_user} ,200

@api.route('/<uuid>')
class CrudPreferenceUsers(Resource):

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, "Success if delete")
    def delete(self, uuid):
        """
        Delete uuid preference
        """
        logging.debug(f"Delete users prefs {uuid}")

        if 'username' not in g.oidc_token_info:
            return abort(message="Utilisateur introuvable", code=HTTPStatus.BAD_REQUEST)
        username = g.oidc_token_info['username']
        preference = Preference.query.filter_by(uuid=uuid).one()

        if preference.username != username:
            return abort(message="Vous n'avez pas les droits de supprimer cette préférence", code=HTTPStatus.FORBIDDEN)

        try:
            db.session.delete(preference)
            db.session.commit()
            return "Success", 200
        except Exception as e:
            logging.error(f"[PREFERENCE][CTRL] Error when delete preference {uuid}", e)
            return abort(message="Error when delete preference", code=HTTPStatus.BAD_REQUEST)


    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, "User preference", preference_get)
    def get(self, uuid):
        """
        Get by uuid preference
        """
        logging.debug(f"Get users prefs {uuid}")

        preference = Preference.query.filter_by(uuid=uuid).one()

        schema = PreferenceSchema()
        result = schema.dump(preference)
        return result,200


parser_search =  reqparse.RequestParser()
parser_search.add_argument("username", type=str, required=True, help="Username")
@api.route('/search-user')
class UsersSearch(Resource):

    @api.response(200, 'Search user by email/username for sharing')
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

            return [{'username': user['username']} for user in users], 200
        except KeycloakAdminException as admin_exception:
            return admin_exception.message, 400