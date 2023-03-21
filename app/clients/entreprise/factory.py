import functools
from flask import current_app

from .api import ApiEntreprise
from .models import ContextInfo
from .models.config import Config, RedisConfig, RateLimiterConfig

def make_api_entreprise() -> ApiEntreprise:
    """Fabrique un client API pour l'api entreprise

    Utilise la configuration `API_ENTREPRISE` de l'application
    """

    config = current_app.config['API_ENTREPRISE']

    url = config['URL']
    token = config['TOKEN']

    context = config['CONTEXT']
    recipient = config['RECIPIENT']
    object = config['OBJECT']

    ratelimiter = config['RATELIMITER']
    ratelimiter_redis = ratelimiter['REDIS']

    api_entreprise_config = Config(
        url, token,
        ContextInfo(
            context=context,
            recipient=recipient,
            object=object,
        ),
        RateLimiterConfig(
            limit=ratelimiter['LIMIT'],
            duration=ratelimiter['DURATION'],
            redis=RedisConfig(ratelimiter_redis['HOST'], ratelimiter_redis['PORT'], ratelimiter_redis['DB'])
        )
    )
        
    return ApiEntreprise(api_entreprise_config)

@functools.cache
def make_or_get_api_entreprise() -> ApiEntreprise:
    return make_api_entreprise()