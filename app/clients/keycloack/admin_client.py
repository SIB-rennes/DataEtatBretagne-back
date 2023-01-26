from flask import current_app
from keycloak import KeycloakAdmin


class KeycloakAdminException(Exception):
    """Exception raised when there is an error building the KeycloakAdmin client.

    Attributes:
        message (str): The message describing the error.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def build_admin_client():
    """Builds a KeycloakAdmin client using the Flask app's configuration.

    Returns:
        KeycloakAdmin: The KeycloakAdmin client.

    Raises:
        KeycloakAdminException: If the Flask app's configuration is missing required values.
    """
    if 'KEYCLOAK_ADMIN' not in current_app.config:
        raise KeycloakAdminException("Configuration for Keyloak missing")

    config = current_app.config['KEYCLOAK_ADMIN']
    if 'URL' not in config or 'SECRET_KEY' not in config or 'REALM' not in config:
        raise KeycloakAdminException("Configuration for Keyloak missing")

    return KeycloakAdmin(server_url=config['URL'],
                         realm_name=config['REALM'],
                         client_secret_key=config['SECRET_KEY'])
