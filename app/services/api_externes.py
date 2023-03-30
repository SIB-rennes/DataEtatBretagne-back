from app.clients.entreprise import get_or_make_api_entreprise
from app.clients.data_subventions import get_or_make_app_api_subventions_client

from app.models.apis_externes.entreprise import InfoApiEntreprise
from app.models.apis_externes.subvention import InfoApiSubvention

def _siren(siret: str):
    return siret[0:9]

class ApisExternesService:
    """Service qui construit les informations provenant des API externes"""
    
    def __init__(self) -> None:
        self.api_entreprise = get_or_make_api_entreprise()
        self.api_subvention = get_or_make_app_api_subventions_client()
    
    def subvention(self, siret: str):
        subvention = self.api_subvention.get_subventions_pour_etablissement(siret)
        contacts = self.api_subvention.get_representants_legaux_pour_etablissement(siret)

        return InfoApiSubvention(subvention=subvention, contacts=contacts)
    
    def entreprise(self, siret: str) -> InfoApiEntreprise:

        siren = _siren(siret)
        donnees_etab = self.api_entreprise.donnees_etablissement(siret)
        tva = self.api_entreprise.numero_tva_intercommunautaire(siren)
        ca = self.api_entreprise.chiffre_d_affaires(siret)
        rge = self.api_entreprise.certifications_rge(siret)
        qualibat = self.api_entreprise.certification_qualibat(siret)

        return InfoApiEntreprise(
            donnees_etablissement=donnees_etab,
            tva=tva,
            chiffre_d_affaires=ca,
            certifications_rge=rge,
            certification_qualibat=qualibat
        )
