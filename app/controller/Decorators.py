from flask import g
from functools import wraps

from requests import RequestException

from app.models.enums.ConnectionProfile import ConnectionProfile


def check_permission(permission: ConnectionProfile):
    """Decorator that checks if the user has the specified permission.

    If the user does not have the permission, the decorated function returns an HTTP 403 error response.

    Args:
        permission (ConnectionProfile): The permission required to execute the decorated function.

    Returns:
        inner_wrapper (function): The decorated function, which checks if the user has the specified permission before executing it.
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            if not _user_has_permission(permission):
                response_body = {'error': 'invalid_role'}
                return response_body, 403, {'WWW-Authenticate': 'Bearer'}
            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper

def _user_has_permission(permission: ConnectionProfile):
    """Checks if the user has the specified permission.

    Args:
        permission (ConnectionProfile): The permission to check.

    Returns:
        bool: True if the user has the permission, False otherwise.
    """
    return 'profile' in g.oidc_token_info and g.oidc_token_info['profile'] == permission.value



def retry_on_exception(max_retry):
    """
    A decorator to retry a function call in case of exceptions.
    :param max_retry: Maximum number of retries.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            while retry_count < max_retry:
                try:
                    return func(*args, **kwargs)
                except RequestException as e:
                    retry_count += 1
                    if retry_count == max_retry:
                        raise e
        return wrapper
    return decorator
