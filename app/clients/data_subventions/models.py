from dataclasses import dataclass

import marshmallow_dataclass as ma
from marshmallow_jsonschema import JSONSchema

@dataclass
class RepresentantLegal:
    nom: str
    prenom: str
    civilite: str
    role: str
    telephone: str
    email: str

    @staticmethod
    def marshmallow_schemaclass():
        return ma.class_schema(RepresentantLegal)

    @staticmethod
    def jsonschema():
        ma_schema = RepresentantLegal.marshmallow_schemaclass()()
        json_schema = JSONSchema().dump(ma_schema)['definitions']['RepresentantLegal']
        return json_schema


@dataclass
class ActionProposee:
    intitule: str
    objectifs: str

    @staticmethod
    def marshmallow_schemaclass():
        return ma.class_schema(ActionProposee)

    @staticmethod
    def jsonschema():
        ma_schema = Subvention.marshmallow_schemaclass()()
        json_schema = JSONSchema().dump(ma_schema)['definitions']['ActionProposee']
        return json_schema

@dataclass
class Subvention:
    ej: str
    service_instructeur: str
    dispositif: str
    sous_dispositif: str
    montant_demande: float
    montant_accorde: float

    actions_proposees: list[ActionProposee]

    @staticmethod
    def marshmallow_schemaclass():
        return ma.class_schema(Subvention)

    @staticmethod
    def jsonschema():
        ma_subvention_schema = Subvention.marshmallow_schemaclass()()

        json_schema = JSONSchema()
        json_schema = json_schema.dump(ma_subvention_schema)
        obj_json_schema = json_schema['definitions']['Subvention']
        return obj_json_schema