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

    """En cas d'erreur de l'API entreprise en requêtant la TVA"""
    tva_indispo: bool
    tva: NumeroTvaHolder | None

    """En cas d'erreur de l'API entreprise en requêtant le CA"""
    chiffre_d_affaires_indispo: bool
    chiffre_d_affaires: list[ChiffreDaffairesHolder]

    """En cas d'erreur de l'API entreprise en requêtant les certifs RGE"""
    certifications_rge_indispo: bool
    certifications_rge: list[CertificationRgeHolder]

    """En cas d'erreur de l'API entreprise en requêtant les certifs RGE"""
    certification_qualibat_indispo: bool
    certification_qualibat: CertificationQualibat | None
