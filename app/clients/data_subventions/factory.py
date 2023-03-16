import functools
from flask import current_app

from .api_subventions import ApiSubventions

def make_app_api_subventions_client() -> ApiSubventions:
    """Fabrique un client API de DataSubvention 

    Utilise la confiugration `API_DATA_SUBVENTIONS` de l'application.
    """

    config = current_app.config['API_DATA_SUBVENTIONS']

    url = config['URL']
    token = config['TOKEN']

    return ApiSubventions(token, url)

@functools.cache
def get_or_make_app_api_subventions_client() -> ApiSubventions:
    return make_app_api_subventions_client()