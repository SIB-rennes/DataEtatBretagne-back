import functools
import logging

import requests
from flask import current_app

class ApiDemarcheSimplifie():
    def __init__(self, token, url) -> None:
        self._token = token
        self._url = url

    def do_post(self, data) -> dict :
        headers = {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json'
        }
        answer = requests.post(
            url=self._url,
            headers=headers,
            data=data)

        answer.raise_for_status()
        return answer.json()


def make_api_demarche_simplifie() -> ApiDemarcheSimplifie:
    """Fabrique un client API pour l'api demarche simplifie
    """

    try:
        config = current_app.config["API_DEMARCHE_SIMPLIFIE"]

        url = config["URL"]
        token = config["TOKEN"]

    except KeyError as e:
        logging.warning("Impossible de trouver la configuration de l'API demarche simplifie.", exc_info=e)
        return None

    return ApiDemarcheSimplifie(token, url)

@functools.cache
def get_or_make_api_demarche_simplifie() -> ApiDemarcheSimplifie:
    return make_api_demarche_simplifie()
