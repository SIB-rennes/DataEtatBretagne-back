import logging

from app import db
from app.clients.entreprise import get_or_make_api_entreprise, DonneesEtablissement, LimitHitError
from app.models.refs.siret import Siret

logger = logging.getLogger(__name__)

def _map(siret: Siret, etablissement: DonneesEtablissement):
    categorie_juridique = etablissement.unite_legale.forme_juridique.code
    code_commune = etablissement.adresse.code_commune
    raison_sociale = etablissement.unite_legale.personne_morale_attributs.raison_sociale
    adresse = etablissement.adresse_postale_legere

    siret.categorie_juridique = categorie_juridique
    siret.code_commune = code_commune
    siret.denomination = raison_sociale
    siret.adresse = adresse

def _api():
    return get_or_make_api_entreprise()

def update_siret_from_api_entreprise(code: str, insert_only = False):
    """Met à jour le siret donné via une requête à l'API entreprise

    Args:
        code (str): siret
        insert_only (bool, optional): Si mis à vrai, ne gère que l'insertion (pas d'update). Defaults to False.

    Raises:
        LimitHitError: si le ratelimiter de l'API est plein.
    """
    logger.info(
        f"[SERVICE][SIRET] Mise à jour du siret {code} "
        "avec les informations de l'API entreprise"
    )
    siret = db.session.query(Siret).filter_by(code=str(code)).one_or_none()
    if siret is not None and insert_only:
        logger.debug(f"Le siret {code} existe déjà. On ne met pas à jour les données")
        return siret
    if siret is None:
        siret = Siret(code=str(code))
    assert siret is not None

    etablissement = _api().donnees_etablissement(code)
    if etablissement is None:
        logger.warning(f"Aucune information sur l'entreprise via API entreprise pour le siret {code}")
        return siret
    
    _map(siret, etablissement)

    return siret

