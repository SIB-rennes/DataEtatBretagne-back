"""
This controller defines a Flask-RESTX Namespace called "preferences" with an endpoint for managing user preferences. The `/users/preferences` path is used for the namespace. The `post` method allows to create a new preference for the current user while the `get` method allows to retrieve the list of preferences for the current user. The `oidc` library is used for authentication and the `marshmallow` library is used for input validation.

The `preference` and `preference_get` models are used to define the expected input and output for the `post` and `get` methods respectively.

The `PreferenceUsers` class, which inherits from `Resource`, is responsible for handling the `post` and `get` methods, and it has the decorators to handle the request validation, token validation, and request/response serialization.
"""
import datetime
import logging
from http import HTTPStatus

from flask_restx import Namespace, Resource, fields, abort, reqparse
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.orm import lazyload

from app import db, oidc
from app.clients.keycloack.admin_client import build_admin_client, KeycloakAdminException
from app.models.preference.Preference import Preference, PreferenceSchema, PreferenceFormSchema, Share

api = Namespace(name="preferences", path='/users/preferences',
                description='API for managing users preference')


preference = api.model('CreateUpdatePreference', {
    'name': fields.String(required=True, description='Name of the preference'),
    'uuid': fields.String(required=False, description='Uuid of the preference for update'),
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
        from app.tasks.management_tasks import share_filter_user
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

        # on retire les shares pour soit même.
        shares = list(filter(lambda d: d['shared_username_email'] != json_data['username'], data['shares']))

        share_list = [Share(**share) for share in shares]
        application = request.origin
        pref = Preference(username = data['username'], name = data['name'], options = data['options'], filters = data['filters'], application_host=application)
        pref.shares = share_list

        try:
            db.session.add(pref)
            logging.info(f'[PREFERENCE][CTRL] Adding preference for user {json_data["username"]}')
            db.session.commit()

            if (len(pref.shares) > 0) :
                share_filter_user.delay(str(pref.uuid), request.origin)
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
        logging.debug(f"get users prefs {request.origin}")
        if 'username' not in g.oidc_token_info:
            return abort(message="Utilisateur introuvable", code=HTTPStatus.BAD_REQUEST)
        username = g.oidc_token_info['username']
        application = request.origin

        list_pref = Preference.query.options(lazyload(Preference.shares)).filter_by(username=username,application_host=application).order_by(
            Preference.id).all()
        list_pref_shared = Preference.query.join(Share).filter(Share.shared_username_email == username, Preference.application_host==application).distinct(Preference.id).all()

        schema = PreferenceSchema(many=True)
        create_by_user = schema.dump(list_pref)
        shared_with_user = schema.dump(list_pref_shared)
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
        application = request.origin
        preference = Preference.query.filter_by(uuid=uuid, application_host=application).one()

        if preference.username != username:
            return abort(message="Vous n'avez pas les droits de supprimer cette préférence", code=HTTPStatus.FORBIDDEN)

        try:
            db.session.delete(preference)
            db.session.commit()
            return "Success", 200
        except Exception as e:
            logging.error(f"[PREFERENCE][CTRL] Error when delete preference {uuid} {application}", e)
            return abort(message=f"Error when delete preference on application {application}", code=HTTPStatus.BAD_REQUEST)

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.expect(preference)
    @api.response(200, "Success if delete")
    def post(self, uuid):
        """
        Update uuid preference
        """
        from app.tasks.management_tasks import share_filter_user
        logging.debug(f"Update users prefs {uuid}")
        if 'username' not in g.oidc_token_info:
            return abort(message="Utilisateur introuvable", code=HTTPStatus.BAD_REQUEST)
        username = g.oidc_token_info['username']
        application = request.origin
        preference_to_save = Preference.query.filter_by(uuid=uuid, application_host=application).one()

        if preference_to_save.username != username:
            return abort(message="Vous n'avez pas les droits de modifier cette préférence", code=HTTPStatus.FORBIDDEN)

        json_data = request.get_json()

        # filter the shares list to exclude the current username
        shares = list(filter(lambda d: d['shared_username_email'] != username, json_data['shares']))
        # create a list of Share objects from the filtered shares
        new_share_list = [Share(**share) for share in shares]
        # initialize a list to store the final shares to save
        shares_to_save = []
        # create sets of existing and new shares, based on their shared_username_email values
        existing_shares = {s.shared_username_email for s in preference_to_save.shares}
        new_shares = {s.shared_username_email for s in new_share_list}

        # find shares to delete and add
        to_delete = existing_shares - new_shares
        to_add = new_shares - existing_shares

        # delete shares that are no longer in the new share list
        for current_share in preference_to_save.shares:
            if current_share.shared_username_email in to_delete:
                db.session.delete(current_share)

        # add new shares that were not in the existing share list
        for new_share in new_share_list:
            if new_share.shared_username_email in to_add:
                shares_to_save.append(new_share)

        # set the final shares for the preference to save
        preference_to_save.shares = shares_to_save + [s for s in preference_to_save.shares if
                                                      s.shared_username_email not in to_delete]

        preference_to_save.name = json_data['name']
        try:
            db.session.commit()
            if (len(preference_to_save.shares) >  0) :
                # send task async
                share_filter_user.delay(str(preference_to_save.uuid), request.origin)
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

        application = request.origin
        preference = Preference.query.filter_by(uuid=uuid, application_host=application).one()

        schema = PreferenceSchema()
        result = schema.dump(preference)
        try :
            preference.nombre_utilisation += 1
            preference.dernier_acces = datetime.datetime.utcnow()
            db.session.commit()
        except Exception as e:
            logging.warning(f"[PREFERENCE][CTRL] Error when update count usage preference {uuid}", e)

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
