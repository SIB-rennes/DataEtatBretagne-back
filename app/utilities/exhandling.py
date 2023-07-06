import functools


def wrap_all_ex_to(exception_to_raise):
    """Catch all exception and wraps it into ex"""

    if not issubclass(exception_to_raise, BaseException):
        raise ValueError("Mauvaise utilisation du décorateur. ( e.g: @wrap_all_to_ex(Err) )")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_to_raise as e:
                raise e
            except Exception as e:
                raise exception_to_raise from e

        return wrapper

    return decorator
