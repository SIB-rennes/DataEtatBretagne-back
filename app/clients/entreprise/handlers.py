import functools

from requests import HTTPError, Response
from pyrate_limiter import BucketFullException,Limiter

from . import logger
from .ratelimiter import API_ENTREPRISE_RATELIMITER_ID

from .exceptions import Http429Error, LimitHitError

def _self(*args):
    return args[0]

def _handle_response_429(response: Response, api_entreprise):

    ratelimiter: Limiter = api_entreprise._ratelimiter
    volume = ratelimiter.get_current_volume(API_ENTREPRISE_RATELIMITER_ID)

    headers = response.headers
    limit = headers.get("RateLimit-Limit")
    remaining = headers.get("RateLimit-Remaining")
    reset = headers.get("RateLimit-Reset")
    retry_after = headers.get("Retry-After")

    logger.warning(
        f"Ratelimiter de l'API entreprise déclenché. "
        "Cela ne devrait pas se produire (ou peu)! "
        f"{remaining}/{limit} - reset: {reset}. retry after: {retry_after}. "
        f"Quant à lui, notre ratelimiter a un volume de {volume}"
    )
    raise Http429Error(retry_after)

def _handle_httperr_429_ex(f):
    """Décorateur qui gère l'erreur transforme l'erreur HTTPError 429 en Http429Error"""
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPError as e:
            response: Response = e.response
            if response.status_code != 429:
                raise

            _handle_response_429(response, _self(*args))

    return inner

def _handle_bucketfull_ex(f):
    """Décorateur qui gère l'erreur BucketFullException renvoyé par le ratelimite de pyratelimiter"""
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BucketFullException as e:
            logger.debug(f"Ratelimiter plein.")
            remaining = max(e.meta_info["remaining_time"], 1)
            raise LimitHitError(remaining)
    
    return inner

def _handle_httperr_404_returns_none(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPError as e:
            response: Response = e.response

            if response.status_code == 404:
                return None
            else:
                raise

    return inner
