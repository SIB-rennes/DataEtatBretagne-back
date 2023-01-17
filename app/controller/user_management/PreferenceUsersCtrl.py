"""
This controller defines a Flask-RESTX Namespace called "preferences" with an endpoint for managing user preferences. The `/users/preferences` path is used for the namespace. The `post` method allows to create a new preference for the current user while the `get` method allows to retrieve the list of preferences for the current user. The `oidc` library is used for authentication and the `marshmallow` library is used for input validation.

The `preference` and `preference_get` models are used to define the expected input and output for the `post` and `get` methods respectively.

The `PreferenceUsers` class, which inherits from `Resource`, is responsible for handling the `post` and `get` methods, and it has the decorators to handle the request validation, token validation, and request/response serialization.
"""
import logging
from http import HTTPStatus

from flask_restx import Namespace, Resource, fields, abort
from flask import request, g
from marshmallow import ValidationError
from app import db, oidc
from app.models.preference.Preference import Preference, PreferenceSchema, PreferenceFormSchema

api = Namespace(name="preferences", path='/users/preferences',
                description='API for managing users preference')


preference = api.model('CreatePreference', {
    'name': fields.String(required=True, description='Name of the preference'),
    'filters':  fields.Wildcard(fields.Raw, description="JSON object representing the user's filter")
})

preference_get  = api.model('Preference', {
    'name': fields.String(required=True, description='Name of the preference'),
    'uuid': fields.String(required=True, description='Uuid of the preference'),
    'filters':  fields.Wildcard(fields.Raw, description="JSON object representing the user's filter")
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
        pref = Preference(**data)

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
    @api.response(200, "List of the user's preferences", [preference_get] )
    def get(self):
        """
        Retrieve the list
        """
        logging.debug("get users prefs")

        if 'username' not in g.oidc_token_info:
            return abort(message="Utilisateur introuvable", code=HTTPStatus.BAD_REQUEST)
        username = g.oidc_token_info['username']

        list_pref =  Preference.query.filter_by(username=username).order_by(Preference.id).all()
        schema = PreferenceSchema(many=True)
        result = schema.dump(list_pref)
        return result,200