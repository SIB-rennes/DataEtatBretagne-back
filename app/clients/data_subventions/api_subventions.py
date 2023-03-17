import logging
import requests

from .models import Subvention, ActionProposee, RepresentantLegal


LOGGER = logging.getLogger()

class ApiDataSubventionsException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class ApiSubventions():
    def __init__(self, token, url) -> None:
        self._token = token
        self._url = url

    def get_representants_legaux_pour_etablissement(self, siret: str):
        url = f"{self._url}/etablissement/{siret}"
        headers = self._auth_headers()
        answer = requests.get(url, headers=headers)
        json = answer.json()
        return self._json_to_representants_legaux(json)

    def get_subventions_pour_etablissement(self, siret: str):
        url = f"{self._url}/etablissement/{siret}/subventions"
        headers = self._auth_headers()
        answer = requests.get(url, headers=headers)
        json = answer.json()
        return self._json_to_subventions(json)
    
    def _auth_headers(self):
        return {
            'x-access-token': self._token
        }
    
    def _json_to_representants_legaux(self, json_dict) -> list[RepresentantLegal]:

        def map(raw):
            representant = RepresentantLegal(
                nom = _get_nested(raw, 'value', 'nom'),
                prenom = _get_nested(raw, 'value', 'prenom'),
                civilite = _get_nested(raw, 'value', 'civilite'),
                role = _get_nested(raw, 'value', 'role'),
                telephone = _get_nested(raw, 'value', 'telephone'),
                email = _get_nested(raw, 'value', 'email'),
            )
            return representant

        raws = _get_nested(json_dict, 'etablissement', 'representants_legaux')
        return [map(x) for x in raws]
    
    def _json_to_subventions(self, json_dict) -> list[Subvention]:

        def map(raw):
            raw_actions_proposee = _get_nested(raw, 'actions_proposee', default=[])

            subvention = Subvention(
                ej = _get_nested(raw, 'ej', 'value'),
                service_instructeur = _get_nested(raw, 'service_instructeur', 'value'),
                dispositif = _get_nested(raw, 'dispositif', 'value'),
                sous_dispositif = _get_nested(raw, 'sous_dispositif', 'value'),
                montant_demande = _get_nested(raw, 'montants', 'demande', 'value'),
                montant_accorde = _get_nested(raw, 'montants', 'accorde', 'value'),

                actions_proposees=[_parse_action_proposee(x) for x in raw_actions_proposee]
            )
            return subvention

        raws = json_dict['subventions']
        return [map(x) for x in raws]

def _parse_action_proposee(dict) -> ActionProposee:
    return ActionProposee(
        intitule = _get_nested(dict, 'intitule', 'value'),
        objectifs = _get_nested(dict, 'objectifs', 'value'),
    )
    
def _get_nested(dict, *keys, default = None):
    """Récupère les valeurs imbriquées dans un dictionnaire

    Exemple:

    d = { 'a': { 'b': { 'c': 'foo' }  } }
    nested = _get_nested(d, 'a', 'b', 'c') # nested == 'foo'
    nested = _get_nested(d, 'does', 'not', 'exist') # nested == None


    Args:
        dict (_type_): Structure à parcourir
        default (_type_, optional): Valeur par défaut en cas de clef inexistante. Defaults to None.
    """

    v = dict
    for key in keys:
        try:
            v = v.get(key, default)
        except AttributeError:
            v = default
            break
    return v
