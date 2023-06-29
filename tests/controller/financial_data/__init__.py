
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def patching_roles(roles = None):
    if roles is None:
        roles = ["ADMIN"]
    
    class _Mocked:
        @property
        def roles(self):
            return roles
        
        @property
        def current_region(self):
            return "053"

        @property
        def username(self):
            return "user@domain.fr"
    
    with patch('app.services.authentication.connected_user.ConnectedUser.from_current_token_identity',return_value=_Mocked()):
        yield