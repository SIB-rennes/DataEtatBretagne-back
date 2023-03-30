from dataclasses import dataclass


from ..utils import _InstrumentForFlaskRestx


from api_entreprise import (
    DonneesEtablissement,
    NumeroTvaHolder,
    ChiffreDaffairesHolder,
    CertificationRgeHolder,
    CertificationQualibat,
)

@dataclass
class InfoApiEntreprise(metaclass=_InstrumentForFlaskRestx):
    """Informations qui proviennent de l'API entreprise"""
    donnees_etablissement: DonneesEtablissement
    tva: NumeroTvaHolder | None
    chiffre_d_affaires: list[ChiffreDaffairesHolder]
    certifications_rge: list[CertificationRgeHolder]
    certification_qualibat: CertificationQualibat | None
