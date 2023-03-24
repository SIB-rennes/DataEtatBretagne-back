import functools
from flask import current_app

from api_entreprise import ApiEntreprise, ContextInfo, Config

from .ratelimiter import _make_rate_limiter

def make_api_entreprise() -> ApiEntreprise:
    """Fabrique un client API pour l'api entreprise

    Utilise la configuration `API_ENTREPRISE` de l'application
    """

    config = current_app.config["API_ENTREPRISE"]

    url = config["URL"]
    token = config["TOKEN"]

    context = config["CONTEXT"]
    recipient = config["RECIPIENT"]
    object = config["OBJECT"]

    api_entreprise_config = Config(
        url,
        token,
        ContextInfo(
            context=context,
            recipient=recipient,
            object=object,
        ),
        _make_rate_limiter(),
    )

    return ApiEntreprise(api_entreprise_config)


@functools.cache
def make_or_get_api_entreprise() -> ApiEntreprise:
    return make_api_entreprise()
