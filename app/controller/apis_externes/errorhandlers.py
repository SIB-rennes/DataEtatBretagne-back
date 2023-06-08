import dataclasses

from . import api
from . import logger
from app.models.apis_externes.error import (
    Error as ApiError,
    CODE_UNKNOWN,
    CODE_CALL_FAILED,
    CODE_LIMIT_HIT,
)
from requests import Timeout

from app.clients.entreprise import ApiError as ApiEntrepriseError, LimitHitError
from app.clients.data_subventions import CallError as ApiSubventionCallError


#
# Exceptions de l'API subvention
#
@api.errorhandler(ApiSubventionCallError)
@api.response(500, "Internal Server Error", model=ApiError.schema_model(api))
def handle_api_subvention_call_error(error: ApiSubventionCallError):
    """Lorsqu'une erreur lors d'un appel à l'API subvention est survenue"""

    logger.error(
        f"[API EXTERNES][CTRL] "
        "Une erreur lors de l'appel à l'API subvention est survenue"
    )

    desc = error.call_error_description
    message = (
        desc.description
        if desc.description is not None
        else "Une erreur lors de l'appel à l'API subvention est survenue"
    )
    err = ApiError(code=CODE_CALL_FAILED, message=message, remote_errors=[desc])
    dict = dataclasses.asdict(err)
    return dict


#
# Exceptions de l'api entreprise
#
@api.errorhandler(LimitHitError)
@api.response(429, "Limite d'usage API atteint", model=ApiError.schema_model(api))
def handle_limit_hit(error: LimitHitError):
    """Lorsqu'une limite d'usage API a été atteint"""

    msg = f"Limite d'utilisation API atteintes (réessayer dans {error.delay} secondes)"
    logger.error(f"[API EXTERNES][CTRL] {msg}")

    err = ApiError(
        code=CODE_LIMIT_HIT,
        message=f"{msg}",
    )
    dict = dataclasses.asdict(err)
    return dict


@api.errorhandler(ApiEntrepriseError)
@api.response(500, "Internal Server Error", model=ApiError.schema_model(api))
def handle_api_entreprise_error(error: ApiEntrepriseError):
    """Lorsqu'une erreur lors de l'appel à l'API entreprise est survenue"""

    logger.error(
        f"[API EXTERNES][CTRL] Une erreur lors de l'appel à l'API entreprise est survenue"
    )

    err = ApiError(
        code=CODE_CALL_FAILED,
        message=f"Une erreur de l'API entreprise est survenue",
        remote_errors=error.errors,
    )
    dict = dataclasses.asdict(err)
    return dict


@api.errorhandler(Timeout)
@api.response(500, "Internal Server Error", model=ApiError.schema_model(api))
def handle_generic(error: Timeout):
    """Lorsqu'un timeout vers le service externe est survenu"""

    logger.error(f"[API EXTERNES][CTRL] Un timeout s'est produit")

    err = ApiError(
        code=CODE_CALL_FAILED,
        message=f"Un timeout s'est produit en appelant le service distant.",
    )

    dict = dataclasses.asdict(err)
    return dict


@api.errorhandler(Exception)
@api.response(500, "Internal Server Error", model=ApiError.schema_model(api))
def handle_generic(error):
    """Lorsqu'une erreur 500 vers la ressource externe est survenue"""

    logger.error(f"[API EXTERNES][CTRL] Une erreur est survenue")

    err = ApiError(
        code=CODE_UNKNOWN,
        message=f"Une erreur inconnue est survenue",
    )

    dict = dataclasses.asdict(err)
    return dict
