from dataclasses import dataclass
from typing import Optional

from ...utils import _AddMarshmallowSchema

## Unité légale
@dataclass
class PersonneMoraleAttributs:
    raison_sociale: str | None
    sigle: str | None

@dataclass
class FormeJuridique:
    code: str
    libelle: str

@dataclass
class UniteLegale:
    forme_juridique: FormeJuridique
    personne_morale_attributs: PersonneMoraleAttributs


## Adresse
# TODO: reconstituer l'adresse complète
@dataclass
class Adresse:
    code_commune: str | None

##
@dataclass
class DonneesEtablissement(metaclass = _AddMarshmallowSchema):
    siret: str

    unite_legale: UniteLegale
    adresse: Adresse