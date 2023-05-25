from app.clients.demarche_simplifie import get_or_make_api_demarche_simplifie
from app.clients.entreprise import get_or_make_api_entreprise, ApiEntrepriseClientError
from app.clients.data_subventions import get_or_make_app_api_subventions_client

from app.models.apis_externes.entreprise import InfoApiEntreprise
from app.models.apis_externes.subvention import InfoApiSubvention

import logging

def _siren(siret: str):
    return siret[0:9]

class ApisExternesService:
    """Service qui construit les informations provenant des API externes"""
    
    def __init__(self) -> None:
        self.api_entreprise = get_or_make_api_entreprise()
        self.api_subvention = get_or_make_app_api_subventions_client()
        self.api_demarche_simplifie = get_or_make_api_demarche_simplifie()
    
    def subvention(self, siret: str):
        subventions = self.api_subvention.get_subventions_pour_etablissement(siret)
        contacts = self.api_subvention.get_representants_legaux_pour_etablissement(siret)

        return InfoApiSubvention(subventions=subventions, contacts=contacts)
    
    def entreprise(self, siret: str) -> InfoApiEntreprise:

        siren = _siren(siret)
        donnees_etab = self.api_entreprise.donnees_etablissement(siret)

        #
        # TODO: Verrue le temps d'avoir notre compte API entreprise
        # avec les droits suffisants
        #
        # ca = self.api_entreprise.chiffre_d_affaires(siret)
        ca: list = []
        ca_indispo = False

        tva = None
        tva_indispo = False
        rge = []
        rge_indispo = False
        qualibat = None
        qualibat_indispo = False

        try:
            tva = self.api_entreprise.numero_tva_intercommunautaire(siren)
        except ApiEntrepriseClientError as e:
            tva_indispo = True
            logging.exception(e)
        try:
            rge = self.api_entreprise.certifications_rge(siret)
        except ApiEntrepriseClientError as e:
            rge_indispo = True
            logging.exception(e)

        try:
            qualibat = self.api_entreprise.certification_qualibat(siret)
        except ApiEntrepriseClientError as e:
            qualibat_indispo = True
            logging.exception(e)

        return InfoApiEntreprise(
            donnees_etablissement=donnees_etab,

            tva_indispo=tva_indispo,
            tva=tva,

            chiffre_d_affaires_indispo=ca_indispo,
            chiffre_d_affaires=ca,

            certifications_rge_indispo=rge_indispo,
            certifications_rge=rge,

            certification_qualibat_indispo=qualibat_indispo,
            certification_qualibat=qualibat
        )
