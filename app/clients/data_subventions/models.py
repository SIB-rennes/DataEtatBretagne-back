from dataclasses import dataclass

from app.models.utils import _AddMarshmallowAndJsonSchema


@dataclass
class RepresentantLegal(metaclass=_AddMarshmallowAndJsonSchema):
    nom: str
    prenom: str
    civilite: str
    role: str
    telephone: str
    email: str

@dataclass
class ActionProposee(metaclass=_AddMarshmallowAndJsonSchema):
    intitule: str
    objectifs: str

@dataclass
class Subvention(metaclass=_AddMarshmallowAndJsonSchema):
    ej: str
    service_instructeur: str
    dispositif: str
    sous_dispositif: str
    montant_demande: float
    montant_accorde: float

    actions_proposees: list[ActionProposee]