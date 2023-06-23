import logging
import requests

from flask import current_app

from app.models.refs.commune import Commune

LOGGER = logging.getLogger()

class ApiGeoException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def get_info_commune(commune: Commune):
    api_geo = current_app.config['API_GEO']

    response = requests.get(f'{api_geo}/communes/{commune.code}?fields=nom,epci,codeDepartement,departement,codeRegion,region&format=json')
    if response.status_code == 200:
        return response.json()
    else:
        raise ApiGeoException(f'Commune introuvable {commune.code}')

