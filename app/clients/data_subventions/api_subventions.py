import logging
import requests

from .models import Subvention, ActionProposee, RepresentantLegal
from .handlers import _handle_response_in_error

from ..utils import _dict_get_nested

LOGGER = logging.getLogger()

class ApiSubventions():
    def __init__(self, token, url) -> None:
        self._token = token
        self._url = url
        self._timeout=10

    @_handle_response_in_error
    def get_representants_legaux_pour_etablissement(self, siret: str):
        url = f"{self._url}/etablissement/{siret}"
        auth_params = self._auth_params()
        answer = requests.get(url, params=auth_params, timeout=self._timeout)
        answer.raise_for_status()
        json = answer.json()
        return self._json_to_representants_legaux(json)

    @_handle_response_in_error
    def get_subventions_pour_etablissement(self, siret: str):
        url = f"{self._url}/etablissement/{siret}/subventions"
        auth_params = self._auth_params()
        answer = requests.get(url, params=auth_params,timeout=self._timeout)
        answer.raise_for_status()
        json = answer.json()
        return self._json_to_subventions(json)
    
    def _auth_params(self):
        return {
            'token': self._token
        }
    
    def _json_to_representants_legaux(self, json_dict) -> list[RepresentantLegal]:

        def map(raw):
            representant = RepresentantLegal(
                nom = _dict_get_nested(raw, 'value', 'nom'),
                prenom = _dict_get_nested(raw, 'value', 'prenom'),
                civilite = _dict_get_nested(raw, 'value', 'civilite'),
                role = _dict_get_nested(raw, 'value', 'role'),
                telephone = _dict_get_nested(raw, 'value', 'telephone'),
                email = _dict_get_nested(raw, 'value', 'email'),
            )
            return representant

        raws = _dict_get_nested(json_dict, 'etablissement', 'representants_legaux')
        return [map(x) for x in raws]
    
    def _json_to_subventions(self, json_dict) -> list[Subvention]:

        def map(raw):
            raw_actions_proposee = _dict_get_nested(raw, 'actions_proposee', default=[])

            subvention = Subvention(
                ej = _dict_get_nested(raw, 'ej', 'value'),
                service_instructeur = _dict_get_nested(raw, 'service_instructeur', 'value'),
                dispositif = _dict_get_nested(raw, 'dispositif', 'value'),
                sous_dispositif = _dict_get_nested(raw, 'sous_dispositif', 'value'),
                montant_demande = _dict_get_nested(raw, 'montants', 'demande', 'value'),
                montant_accorde = _dict_get_nested(raw, 'montants', 'accorde', 'value'),

                actions_proposees=[_parse_action_proposee(x) for x in raw_actions_proposee]
            )
            return subvention

        raws = json_dict['subventions']
        return [map(x) for x in raws]

def _parse_action_proposee(dict) -> ActionProposee:
    return ActionProposee(
        intitule = _dict_get_nested(dict, 'intitule', 'value'),
        objectifs = _dict_get_nested(dict, 'objectifs', 'value'),
    )
    