from functools import wraps
from unittest.mock import patch

# MOCK du accept_token
def mock_accept_token(*args, **kwargs):
    def wrapper(view_func):
        @wraps(view_func)
        def decorated(*args, **kwargs):
            print('ici')
            return view_func(*args, **kwargs)

        return decorated

    return wrapper


patch('flask_oidc.OpenIDConnect.accept_token', mock_accept_token).start()
