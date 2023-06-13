import logging

from api_entreprise import ApiError

from app import db
from app.clients.entreprise import get_or_make_api_entreprise, DonneesEtablissement
from app.clients.geo import get_info_commune
from app.models.refs.commune import Commune
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


def check_siret(siret):
    """Rempli les informations du siret via l'API entreprise

    Raises:
        LimitHitError: Si le ratelimiter de l'API entreprise est déclenché
    """
    if siret is not None :
        siret_entity = update_siret_from_api_entreprise(siret, insert_only=True)
        __check_commune(siret_entity.code_commune)
        try:
            db.session.add(siret_entity)
            db.session.commit()
        except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            logger.exception(f"[SIRET] Error sur ajout Siret {siret}")
            raise e

        logger.info(f"[SIRET] Siret {siret} ajouté")

def __check_commune(code):
    instance = db.session.query(Commune).filter_by(code=code).one_or_none()
    if not instance:
        logger.info('[IMPORT][COMMUNE] Ajout commune %s', code)
        commune = Commune(code = code)
        try:
            commune = _maj_one_commune(commune)
            db.session.add(commune)
        except Exception:
            logger.exception(f"[IMPORT][CHORUS] Error sur ajout commune {code}")

def _maj_one_commune(commune: Commune):
    """
    Lance la MAj d'une communce
    :param commune:
    :return:
    """
    apigeo = get_info_commune(commune)
    commune.label_commune = apigeo['nom']
    if 'epci' in apigeo:
        commune.code_epci = apigeo['epci']['code']
        commune.label_epci = apigeo['epci']['nom']
    if 'region' in apigeo:
        commune.code_region = apigeo['region']['code']
        commune.label_region = apigeo['region']['nom']
    if 'departement' in apigeo:
        commune.code_departement = apigeo['departement']['code']
        commune.label_departement = apigeo['departement']['nom']
    return commune



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

    try:
        etablissement = _api().donnees_etablissement(code)
        if etablissement is None:
            logger.warning(f"Aucune information sur l'entreprise via API entreprise pour le siret {code}")
            return siret
    except ApiError :
        logger.exception(f"Error api entreprise {code}")
        return siret
    
    _map(siret, etablissement)

    return siret
