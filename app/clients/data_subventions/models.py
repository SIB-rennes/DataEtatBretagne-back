from dataclasses import dataclass

import marshmallow_dataclass as ma
from marshmallow_jsonschema import JSONSchema

class _WithSchemaGen(type):
    """Metaclass qui génère le schema marshmallow et le json schema pour la classe cible.

    Lorsque une dataclass est instanciée avec WithSchemaGen:

    class A(metaclass=WithSchemaGen):
      pass

    Elle aura deux proprietés de classe:

    - A.MarshmallowSchema: la classe représentant le schema marshmallow. 
      `schema = A.MarshmallowSchema()`
    
    - A.jsonschema: une structure native python serialisable qui représente la structure de donnée
      sous format json schema.
      `A.jsonschema`
    """
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)
    
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        ma_schema_class = ma.class_schema(cls)
        ma_schema = ma_schema_class()
        json_schema = JSONSchema().dump(ma_schema)['definitions'][name]

        cls.MarshmallowSchema = ma_schema_class
        cls.jsonschema = json_schema


@dataclass
class RepresentantLegal(metaclass=_WithSchemaGen):
    nom: str
    prenom: str
    civilite: str
    role: str
    telephone: str
    email: str

@dataclass
class ActionProposee(metaclass=_WithSchemaGen):
    intitule: str
    objectifs: str

@dataclass
class Subvention(metaclass=_WithSchemaGen):
    ej: str
    service_instructeur: str
    dispositif: str
    sous_dispositif: str
    montant_demande: float
    montant_accorde: float

    actions_proposees: list[ActionProposee]