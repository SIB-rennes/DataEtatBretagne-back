import json
import logging

import pandas

from datetime import datetime

import sqlalchemy.exc
from celery import subtask

from app import db, celeryapp
from app.models.financial.Chorus import Chorus
from app.models.refs.centre_couts import CentreCouts
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.commune import Commune
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.fournisseur_titulaire import FournisseurTitulaire
from app.models.refs.groupe_marchandise import GroupeMarchandise
from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.models.refs.siret import Siret
from app.tasks import maj_one_commune

from app.clients.entreprise import make_or_get_api_entreprise, LimitHitError

CHORUS_COLUMN_NAME = ['programme_code', 'domaine_code', 'domaine_label', 'centre_cout_code', 'centre_cout_label',
                      'ref_programmation_code', 'ref_programmation_label', 'n_ej', 'n_poste_ej', 'date_modif',
                      'Fournisseur_code', 'Fournisseur_label', 'siret', 'compte_code', 'compte_label',
                      'compte_budgetaire',
                      'groupe_marchandise_code', 'groupe_marchandise_label',
                      'contrat_etat_region', 'contrat_etat_region_2', 'localisation_interministerielle_code',
                      'localisation_interministerielle_label', 'montant']

LOGGER = logging.getLogger()

celery = celeryapp.celery

class ChorusException(Exception):
    pass

@celery.task(bind=True, name='import_file_ae_chorus')
def import_file_ae_chorus(self, fichier, source_region: str, annee: int, force_update: bool):
    # get file
    LOGGER.info(f'[IMPORT][CHORUS] Start for region {source_region}, year {annee}')
    try:
        data_chorus = pandas.read_csv(fichier, sep=",", skiprows=8, names=CHORUS_COLUMN_NAME,
                                      dtype={'programme_code': str, 'n_ej': str, 'n_poste_ej': int,
                                             'Fournisseur_code': str,
                                             'siret': 'str'})
        # _import_data_chorus(data_chorus)
        for index, chorus_data in data_chorus.iterrows():
            # MAJ des referentiels si necessaire
            if chorus_data['siret'] != '#':
                subtask("import_line_chorus_ae").delay(chorus_data.to_json(), index, source_region, annee, force_update)

        LOGGER.info('[IMPORT][CHORUS] End')
        return True
    except Exception as e:
        LOGGER.exception(f"[IMPORT][CHORUS] Error lors de l'import du fichier {fichier} chorus")
        raise e


@celery.task(bind=True, name='import_line_chorus_ae', autoretry_for=(ChorusException,),  retry_kwargs={'max_retries': 4, 'countdown': 10})
def import_line_chorus_ae(self, data_chorus, index, source_region: str, annee: int, force_update: bool):
    line = json.loads(data_chorus)
    try :
        chorus_instance = _check_insert__update_chorus(line, force_update)
    except sqlalchemy.exc.OperationalError as o:
        LOGGER.exception(f"[IMPORT][CHORUS] Erreur index {index} sur le check ligne chorus")
        raise ChorusException(o)


    if chorus_instance != False:
        try:
            _check_ref(CodeProgramme, **{'code': line['programme_code']})
            _check_ref(CentreCouts, **{'code': line['centre_cout_code'],
                                       'label': line['centre_cout_label']})
            _check_ref(DomaineFonctionnel,
                       **{'code': line['domaine_code'], 'label': line['domaine_label']})
            _check_ref(FournisseurTitulaire, **{'code': line['Fournisseur_code'],
                                                'label': line['Fournisseur_label']})
            _check_ref(GroupeMarchandise, **{'code': line['groupe_marchandise_code'],
                                             'label': line['groupe_marchandise_label'],
                                             'code_pce': line['compte_code'],
                                             'label_pce': line['compte_label']})
            _check_ref(LocalisationInterministerielle,
                       **{'code': line['localisation_interministerielle_code'],
                          'label': line['localisation_interministerielle_label']})
            _check_ref(ReferentielProgrammation, **{'code': line['ref_programmation_code'],
                                                    'label': line['ref_programmation_label']})

            # SIRET
            _check_siret(line['siret'])

            # CHORUS
            if chorus_instance == True:
                _insert_chorus(line, source_region, annee)
            else:
                _update_chorus(line, chorus_instance, source_region, annee)

        except LimitHitError as e:
            delay = (e.delay) + 5
            LOGGER.info(
                f"[IMPORT][CHORUS] Limite d'appel à l'API entreprise atteinte pour l'index {str(index)}. " 
                f"Ré essai de la tâche dans {str(delay)} secondes"
            )
            # XXX: max_retries=None ne désactive pas le mécanisme 
            # de retry max contrairement à ce que stipule la doc !
            # on met donc un grand nombre.
            self.retry(countdown=delay, max_retries=1000, retry_jitter=True)

        except Exception as e:
            LOGGER.exception(f"[IMPORT][CHORUS] erreur index {index}")
            raise e


def _check_ref(model, **kwargs):
    instance = db.session.query(model).filter_by(code=kwargs.get('code')).one_or_none()
    if not instance:
        instance = model(**kwargs)
        LOGGER.info('[IMPORT][CHORUS] Ajout ref %s dans %s', model.__tablename__, kwargs)
        try:
            db.session.add(instance)
            db.session.commit()
        except Exception:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            db.session.rollback()
            LOGGER.warning("[IMPORT][CHORUS] Error sur ajout ref %s dans %s ",model.__tablename__, kwargs)


def __check_commune(code):
    instance = db.session.query(Commune).filter_by(code_commune=code).one_or_none()
    if not instance:
        LOGGER.info('[IMPORT][CHORUS] Ajout commune %s', code)
        commune = Commune(code_commune = code)
        try:
            commune = maj_one_commune(commune)
            db.session.add(commune)
        except Exception:
            db.session.rollback()
            LOGGER.warning(f"[IMPORT][CHORUS] Error sur ajout commune {code}")

def _check_siret(siret):
    """Rempli les informations du siret via l'API entreprise

    Raises:
        LimitHitError: Si le ratelimiter de l'API entreprise est déclenché
    """
    instance = db.session.query(Siret).filter_by(code=str(siret)).one_or_none()

    if not instance:
        siret_entity = Siret(code=str(siret))

        etablissement = _donnees_etab(siret)

        if etablissement is None:
            LOGGER.warning("[IMPORT][CHORUS] Siret %s non trouvé via l'api", siret)
        else:
            #
            categorie_juridique = etablissement.unite_legale.forme_juridique.code
            code_commune = etablissement.adresse.code_commune
            raison_sociale = etablissement.unite_legale.personne_morale_attributs.raison_sociale
            adresse = etablissement.adresse_postale_legere

            siret_entity.categorie_juridique = categorie_juridique
            siret_entity.code_commune = code_commune
            siret_entity.denomination = raison_sociale
            siret_entity.adresse = adresse

            __check_commune(siret_entity.code_commune)

        LOGGER.info(f"[IMPORT][CHORUS] Siret {siret} ajouté")
        try:
            db.session.add(siret_entity)
            db.session.commit()
        except Exception:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            db.session.rollback()
            LOGGER.warning(f"[IMPORT][CHORUS] Error sur ajout Siret {siret} ")

def _donnees_etab(siret: str):
    client_api_entreprise = make_or_get_api_entreprise()
    etablissement = client_api_entreprise.donnees_etablissement(siret)
    return etablissement

def _check_insert__update_chorus(chorus_data, force_update: bool):
    '''

    :param chorus_data:
    :param force_update:
    :return: True -> Chorus à créer
             False -> rien à faire
             Instance chorus -> Chorus à maj
    '''
    instance = db.session.query(Chorus).filter_by(n_ej=chorus_data['n_ej'],
                                                  n_poste_ej=chorus_data['n_poste_ej']).one_or_none()
    if instance:
        if force_update:
            LOGGER.info('[IMPORT][CHORUS] Doublon trouvé, Force Update')
            return instance
        if datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y') > instance.date_modification_ej:
            LOGGER.info('[IMPORT][CHORUS] Doublon trouvé, MAJ à faire sur la date')
            return instance
        else:
            LOGGER.info('[IMPORT][CHORUS] Doublon trouvé, Pas de maj')
            return False
    return True


def _insert_chorus(chorus_data, source_region: str, annee: int):
    chorus = Chorus(n_ej=chorus_data['n_ej'], n_poste_ej=chorus_data['n_poste_ej'],
                    programme=chorus_data['programme_code'],
                    domaine_fonctionnel=chorus_data['domaine_code'],
                    centre_couts=chorus_data['centre_cout_code'],
                    referentiel_programmation=chorus_data['ref_programmation_code'],
                    localisation_interministerielle=chorus_data['localisation_interministerielle_code'],
                    groupe_marchandise=chorus_data['groupe_marchandise_code'],
                    fournisseur_titulaire=chorus_data['Fournisseur_code'],
                    siret=str(chorus_data['siret']),
                    date_modification_ej=datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y'),
                    compte_budgetaire=chorus_data['compte_budgetaire'],
                    contrat_etat_region=chorus_data['contrat_etat_region'],
                    montant=float(str(chorus_data['montant']).replace('\U00002013', '-').replace(',', '.')),
                    source_region=source_region,
                    annee=annee)

    db.session.add(chorus)
    LOGGER.info('[IMPORT][CHORUS] Ajout ligne chorus')
    db.session.commit()


def _update_chorus(chorus_data, chorus_to_update, code_source_region: str, annee: int):
    chorus_to_update.programme = chorus_data['programme_code']
    chorus_to_update.domaine_fonctionnel = chorus_data['domaine_code']
    chorus_to_update.centre_couts = chorus_data['centre_cout_code']
    chorus_to_update.referentiel_programmation = chorus_data['ref_programmation_code']
    chorus_to_update.localisation_interministerielle = chorus_data['localisation_interministerielle_code']
    chorus_to_update.groupe_marchandise = chorus_data['groupe_marchandise_code']
    chorus_to_update.fournisseur_titulaire = chorus_data['Fournisseur_code']
    chorus_to_update.siret = str(chorus_data['siret'])
    chorus_to_update.date_modification_ej = datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y')
    chorus_to_update.compte_budgetaire = chorus_data['compte_budgetaire']
    chorus_to_update.contrat_etat_region = chorus_data['contrat_etat_region']
    chorus_to_update.montant = float(str(chorus_data['montant']).replace('\U00002013', '-').replace(',', '.'))

    chorus_to_update.source_region = code_source_region
    chorus_to_update.annee = annee
    LOGGER.info('[IMPORT][CHORUS] Update ligne chorus')
    db.session.commit()
