import csv
import json
import logging
import os

import pandas
from flask import current_app
from werkzeug.utils import secure_filename

from app.models.financial.Chorus import Chorus
from app.services import allowed_file, FileNotAllowedException
from app.services.file_service import InvalidFile

CHORUS_COLUMN_NAME = ['programme_code', 'domaine_code', 'centre_cout_code',
                      'ref_programmation_code', 'n_ej', 'n_poste_ej', 'date_modif',
                      'Fournisseur_code', 'Fournisseur_label', 'siret', 'compte_code',
                      'compte_budgetaire', 'groupe_marchandise_code', 'contrat_etat_region', 'contrat_etat_region_2',
                      'localisation_interministerielle_code', 'montant']
def import_ae(file_chorus, source_region:str ,annee: int, force_update: bool):

    if file_chorus.filename == '':
        logging.info('Pas de fichier')
        return {"statut": 'Aucun fichier importé'}, 400

    if file_chorus and allowed_file(file_chorus.filename):

        check_file(file_chorus.filename)

        from app.tasks.import_chorus_tasks import import_file_ae_chorus
        filename = secure_filename(file_chorus.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_chorus.save(save_path)

        logging.info(f'[IMPORT CHORUS] Récupération du fichier {filename}')
        return import_file_ae_chorus.delay(str(save_path), source_region, annee, force_update)
    else:
        logging.error(f'[IMPORT CHORUS] Fichier refusé {file_chorus.filename}')
        raise FileNotAllowedException(message='le fichier n\'est pas un csv')




def check_file(fichier):
    try:
        data_chorus = pandas.read_csv(fichier, sep=",", skiprows=8, nrows=5,
                                      names=Chorus.get_columns_files_ae(),
                                      dtype={'programme_code': str, 'n_ej': str, 'n_poste_ej': int,
                                             'Fournisseur_code': str,
                                             'siret': 'str'})
    except Exception:
        raise FileNotAllowedException(message="Erreur de lecture du fichier")

    if data_chorus.isnull().values.any():
        raise InvalidFile("le fichier contient des valeurs vides")


