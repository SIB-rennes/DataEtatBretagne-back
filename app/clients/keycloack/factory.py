import functools

from flask import current_app
from keycloak import KeycloakAdmin, KeycloakOpenID


class KeycloakConfigurationException(Exception):
    """Exception raised when there is an error building the KeycloakAdmin client.

    Attributes:
        message (str): The message describing the error.
    """

    def __init__(self, message="Configuration for Keyloak missing"):
        self.message = message
        super().__init__(self.message)


def make_keycloack_admin() -> KeycloakAdmin :
    """Builds a KeycloakAdmin client using the Flask app's configuration.

    Returns:
        KeycloakAdmin: The KeycloakAdmin client.

    Raises:
        KeycloakAdminException: If the Flask app's configuration is missing required values.
    """
    if 'KEYCLOAK_ADMIN' not in current_app.config:
        raise KeycloakConfigurationException()

    config = current_app.config['KEYCLOAK_ADMIN']
    if 'URL' not in config or 'SECRET_KEY' not in config or 'REALM' not in config:
        raise KeycloakConfigurationException()

    return KeycloakAdmin(server_url=config['URL'],
                         realm_name=config['REALM'],
                         client_secret_key=config['SECRET_KEY'])

@functools.cache
def make_or_get_keycloack_admin() -> KeycloakAdmin:
    return make_keycloack_admin()



def make_keycloack_openid() -> KeycloakOpenID:
    """Builds a KeycloakOpenID client using the Flask app's configuration.

    Returns:
        KeycloakOpenID: The KeycloakOpenIDConnection client.

    Raises:
        KeycloakAdminException: If the Flask app's configuration is missing required values.
    """
    if 'KEYCLOAK_OPENID' not in current_app.config:
        raise KeycloakConfigurationException()

    config = current_app.config['KEYCLOAK_OPENID']
    if 'URL' not in config or 'SECRET_KEY' not in config or 'REALM' not in config or 'CLIENT_ID' not in config:
        raise KeycloakConfigurationException()

    return KeycloakOpenID(server_url=config['URL'],
                         realm_name=config['REALM'],
                          client_id=config['CLIENT_ID'],
                         client_secret_key=config['SECRET_KEY'])

@functools.cache
def make_or_get_keycloack_openid() -> KeycloakOpenID:
    return make_keycloack_openid()