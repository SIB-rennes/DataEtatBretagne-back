from flask import g
from functools import wraps

from requests import RequestException

from app.controller import ErrorController
from app.models.enums.ConnectionProfile import ConnectionProfile


def check_permission(permissions):
    """Decorator that checks if the user has the specified permission.

    If the user does not have the permission, the decorated function returns an HTTP 403 error response.

    Args:
        permissions (Union[str, List[str]]): The permission required to execute the decorated function. It can be a single string or a list of strings.

    Returns:
        inner_wrapper (function): The decorated function, which checks if the user has the specified permission before executing it.
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            user_permissions = _get_user_permissions()  # get the user's permissions
            if isinstance(permissions, ConnectionProfile):
                permissions_to_check = [permissions]
            elif isinstance(permissions, list):
                permissions_to_check = permissions
            else:
                raise TypeError("permissions should be a ConnectionProfile or a list of ConnectionProfiles")

            if user_permissions is not None :
                for perm in permissions_to_check:
                    if perm.value == user_permissions:
                        return func(*args, **kwargs)  # the user has the required permission

            response_body = ErrorController("Vous n`avez pas les droits").to_json()
            return response_body, 403, {'WWW-Authenticate': 'Bearer'}
        return inner_wrapper
    return wrapper


def _get_user_permissions():
    """Get User permission.

    Returns:
        None if no permission
    """
    return g.oidc_token_info['profile'] if 'profile' in g.oidc_token_info else None



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
