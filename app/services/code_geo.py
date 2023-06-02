import dataclasses
from app.models.enums.TypeCodeGeo import TypeCodeGeo

class BadCodeGeoException(Exception):
    message: str
    def __init__(self, message):
        self.message = message
        super().__init__(message)


@dataclasses.dataclass
class CodeGeo():
    code_geo: str = None
    @property
    def type(self) -> TypeCodeGeo:
        '''
        Retourne le type du code geo
        :return:   le type
        :raise BadCodeGeoException si le type n'est pas reconnu
        '''
        if (self.code_geo is None):
            raise BadCodeGeoException(message="Le code geo n'est pas renseigné")

        if (self.code_geo.isdigit()): # si le code geo est un nombre
            length_code_geo = len(self.code_geo)
            match length_code_geo:
                case 2 :
                    return TypeCodeGeo.DEPARTEMENT
                case 3 | 4:
                    return TypeCodeGeo.ARRONDISSEMENT
                case 5:
                    return TypeCodeGeo.COMMUNE
                case 9:
                    return TypeCodeGeo.EPCI
                case _:
                    raise BadCodeGeoException(message=f"Le code geo {self.code_geo} n'est pas reconnu")

        elif (self.code_geo.lower().startswith("crte-")) :
            return TypeCodeGeo.CRTE
        elif (self.code_geo == '2A' or self.code_geo == '2B') : # cas specifique corse
            return TypeCodeGeo.DEPARTEMENT

        raise BadCodeGeoException(message=f"Le code geo {self.code_geo} n'est pas reconnu")

class BuilderCodeGeo():
    @staticmethod
    def build_list_code_geo(list_code: [str]) -> (TypeCodeGeo, [str]):
        '''
        Construit une liste d'objets CodeGeo à partir d'une liste de codes géographiques
        :param list_code: liste des codes géographiques
        :return: le type de code géo commun à tous les éléments de la liste et une liste des codes géographiques
        :raise BadCodeGeoException: si la liste ne contient pas des code geo de même type
        '''
        list_code_geo = []
        for code_geo in list_code:
            list_code_geo.append(CodeGeo(code_geo))

        type_geo = list_code_geo[0].type

        all_same_type_geo = all(code_geo.type == type_geo for code_geo in list_code_geo)
        if not all_same_type_geo:
            raise BadCodeGeoException(message="La liste ne contient pas des codes geo de même type")

        return type_geo, [code_geo.code_geo for code_geo in list_code_geo]


