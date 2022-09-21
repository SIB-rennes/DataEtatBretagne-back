import logging
import requests
import pandas

from datetime import datetime
from flask_script import Command
from flask import current_app

from app import db
from app.models.Chorus import Chorus
from app.models.refs.centre_couts import CentreCouts
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.compte_general import CompteGeneral
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.fournisseur_titulaire import FournisseurTitulaire
from app.models.refs.groupe_marchandise import GroupeMarchandise
from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.models.siret import Siret

CHORUS_COLUMN_NAME = ['programme_code','domaine_code','domaine_label','centre_cout_code','centre_cout_label',
                                             'ref_programmation_code','ref_programmation_label','n_ej','n_poste_ej','date_modif',
                                             'Fournisseur_code','Fournisseur_label','siret','compte_code','compte_label','compte_budgetaire',
                                             'groupe_marchandise_code','groupe_marchandise_label',
                                             'contrat_etat_region','contrat_etat_region_2','localisation_interministerielle_code',
                                             'localisation_interministerielle_label','montant']

LOGGER = logging.getLogger('transform')
class ImportChorus(Command):


    def run(self):
        # get file
        file = current_app.config['data']['chorus']
        LOGGER.info('[IMPORT][CHORUS] Start')
        data_chorus = pandas.read_csv(file,sep=",", skiprows=8, names=CHORUS_COLUMN_NAME,
                                      dtype={'programme_code': str, 'n_ej': str, 'n_poste_ej':int, 'Fournisseur_code': str, 'siret': 'str'})

        self._import_data_chorus(data_chorus)
        LOGGER.info('[IMPORT][CHORUS] End')


    def _import_data_chorus(self, data_frame):

        for index,chorus_data in data_frame.iterrows():
            # MAJ des referentiels si necessaire
            if chorus_data['siret'] != '#':
                chorus_instance = self._check_insert__update_chorus(chorus_data)
                if chorus_instance != False :
                    try :
                        self._check_ref(CodeProgramme, **{ 'code':  chorus_data['programme_code']} )
                        self._check_ref(CentreCouts, **{'code': chorus_data['centre_cout_code'], 'label': chorus_data['centre_cout_label']})
                        self._check_ref(CompteGeneral, **{'code': chorus_data['compte_code'], 'label': chorus_data['compte_label']})
                        self._check_ref(DomaineFonctionnel, **{'code': chorus_data['domaine_code'], 'label': chorus_data['domaine_label']})
                        self._check_ref(FournisseurTitulaire, **{'code': chorus_data['Fournisseur_code'], 'label': chorus_data['Fournisseur_label']})
                        self._check_ref(GroupeMarchandise, **{'code': chorus_data['groupe_marchandise_code'], 'label': chorus_data['groupe_marchandise_label']})
                        self._check_ref(LocalisationInterministerielle, **{'code': chorus_data['localisation_interministerielle_code'], 'label': chorus_data['localisation_interministerielle_label']})
                        self._check_ref(ReferentielProgrammation, **{'code': chorus_data['ref_programmation_code'], 'label': chorus_data['ref_programmation_label']})

                        # SIRET
                        self._check_siret(chorus_data['siret'])

                        # CHORUS
                        if chorus_instance == True:
                            self._insert_chorus(chorus_data)
                        else :
                            self._update_chorus(chorus_data, chorus_instance)
                    except Exception as e:
                        LOGGER.error("erreur index %s", index)
                        LOGGER.error(e)
            # break


    def _check_ref(self, model, **kwargs):
        instance = db.session.query(model).filter_by(**kwargs).one_or_none()
        if not instance:
            instance = model(**kwargs)
            LOGGER.info('[IMPORT][CHORUS] Ajout ref %s dans %s',model.__tablename__, kwargs)
            try:
                db.session.add(instance)
                db.session.commit()
            except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
                db.session.rollback()
                LOGGER.error(e)


    def _check_siret(self, siret):
        instance = db.session.query(Siret.Siret).filter_by(siret=siret).one_or_none()
        if not instance:
            resp = requests.get(url=current_app.config['api_siren']+siret)
            siret = Siret.Siret(siret=int(siret))
            if resp.status_code != 200:
                LOGGER.warning("[IMPORT][CHORUS] Siret %s non trouvé via l'api", siret)
            else :
                data = resp.json()
                info = data['etablissement']
                siret.categorie_juridique=info['unite_legale']['categorie_juridique']
                siret.code_commune=info['code_commune']
                siret.denomination=info['unite_legale']['denomination']
                siret.adresse = info['geo_adresse']
                if info['longitude'] is not None and info['latitude'] is not None:
                    siret.longitude = float(info['longitude'])
                    siret.latitude = float(info['latitude'])

            LOGGER.info("[IMPORT][CHORUS] Siret %s ajouté", siret)
            try:
                db.session.add(siret)
                db.session.commit()
            except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
                db.session.rollback()
                LOGGER.error(e)


    def _check_insert__update_chorus(self, chorus_data):
        '''

        :param chorus_data:
        :return: True -> Chorus à créer
                 False -> rien à faire
                 Instance chorus -> Chorus à maj
        '''
        instance = db.session.query(Chorus).filter_by(n_ej=chorus_data['n_ej'],
                                                      n_poste_ej=chorus_data['n_poste_ej']).one_or_none()
        if instance :
            if datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y') > instance.date_modification_ej :
                LOGGER.info('[IMPORT][CHORUS] Doublon trouvé, MAJ à faire sur la date')
                return instance
            else :
                LOGGER.info('[IMPORT][CHORUS] Doublon trouvé, Pas de maj')
                return False
        return True

    def _insert_chorus(self, chorus_data):
        chorus = Chorus(n_ej=chorus_data['n_ej'], n_poste_ej=chorus_data['n_poste_ej'],
                            programme=chorus_data['programme_code'],
                            domaine_fonctionnel=chorus_data['domaine_code'],
                            centre_couts=chorus_data['centre_cout_code'],
                            referentiel_programmation=chorus_data['ref_programmation_code'],
                            localisation_interministerielle=chorus_data['localisation_interministerielle_code'],
                            groupe_marchandise=chorus_data['groupe_marchandise_code'],
                            compte_general=chorus_data['compte_code'],
                            fournisseur_titulaire=chorus_data['Fournisseur_code'],
                            siret=chorus_data['siret'],
                            date_modification_ej=datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y'),
                            compte_budgetaire=chorus_data['compte_budgetaire'],
                            contrat_etat_region=chorus_data['contrat_etat_region'],
                            montant= float(str(chorus_data['montant']).replace('\U00002013', '-').replace(',','.')))
        try:
           db.session.add(chorus)
           LOGGER.info('[IMPORT][CHORUS] Ajout ligne chorus')
           db.session.commit()
        except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
           LOGGER.error(e)


    def _update_chorus(self, chorus_data, chorus_to_update):

        chorus_to_update.programme=chorus_data['programme_code']
        chorus_to_update.domaine_fonctionnel=chorus_data['domaine_code']
        chorus_to_update.centre_couts=chorus_data['centre_cout_code']
        chorus_to_update.referentiel_programmation=chorus_data['ref_programmation_code']
        chorus_to_update.localisation_interministerielle=chorus_data['localisation_interministerielle_code']
        chorus_to_update.groupe_marchandise=chorus_data['groupe_marchandise_code']
        chorus_to_update.compte_general=chorus_data['compte_code']
        chorus_to_update.fournisseur_titulaire=chorus_data['Fournisseur_code']
        chorus_to_update.siret=chorus_data['siret']
        chorus_to_update.date_modification_ej=datetime.strptime(chorus_data['date_modif'], '%d.%m.%Y')
        chorus_to_update.compte_budgetaire=chorus_data['compte_budgetaire']
        chorus_to_update.contrat_etat_region=chorus_data['contrat_etat_region']
        chorus_to_update.montant= float(str(chorus_data['montant']).replace('\U00002013', '-').replace(',','.'))
        try:
           # db.session.update(chorus_to_update)
           LOGGER.info('[IMPORT][CHORUS] Update ligne chorus')
           db.session.commit()
        except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
           LOGGER.error(e)


