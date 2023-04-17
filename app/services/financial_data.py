import logging
import os
import tempfile
import pandas
from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.exceptions.exceptions import InvalidFile
from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.DataType import DataType
from app.models.financial.FinancialCp import FinancialCp
from app.models.financial.FinancialAe import FinancialAe
from app.services import allowed_file, FileNotAllowedException

def import_ae(file_ae, source_region:str, annee: int, force_update: bool, username=""):
    save_path = _check_file_and_save(file_ae)
    _check_file(save_path, FinancialAe.get_columns_files_ae())

    logging.info(f'[IMPORT FINANCIAL] Récupération du fichier {save_path}')
    from app.tasks.import_financial_tasks import import_file_ae_financial
    task = import_file_ae_financial.delay(str(save_path), source_region, annee, force_update)
    db.session.add(AuditUpdateData(username=username, filename=file_ae.filename, data_type=DataType.FINANCIAL_DATA))
    db.session.commit()
    return task


def import_cp(file_cp, source_region:str, annee: int, force_update: bool, username=""):
    save_path = _check_file_and_save(file_cp)
    _check_file(save_path, FinancialCp.get_columns_files_cp())

    logging.info(f'[IMPORT FINANCIAL] Récupération du fichier {save_path}')
    from app.tasks.import_financial_tasks import import_file_ae_financial
    task = import_file_ae_financial.delay(str(save_path), source_region, annee, force_update)
    db.session.add(AuditUpdateData(username=username, filename=file_cp.filename, data_type=DataType.FINANCIAL_DATA))
    db.session.commit()
    return task

def _check_file_and_save(file) -> str:
    if file.filename == '':
        raise InvalidFile(message="Pas de fichier")

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        if 'UPLOAD_FOLDER' in current_app.config:
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else:
            save_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(save_path)
        return save_path
    else:
        logging.error(f'[IMPORT FINANCIAL] Fichier refusé {file.filename}')
        raise FileNotAllowedException(message='le fichier n\'est pas un csv')



def _check_file(fichier, column_names):
    try:
        data_chorus = pandas.read_csv(fichier, sep=",", skiprows=8, nrows=5,
                                      names=column_names,
                                       dtype={'programme': str, 'n_ej': str, 'n_poste_ej': int,
                                                     'fournisseur_titulaire': str,
                                                     'siret': 'str'})
    except Exception:
        logging.exception(msg="[CHECK FILE] Erreur de lecture du fichier")
        raise FileNotAllowedException(message="Erreur de lecture du fichier")

    if data_chorus.isnull().values.any():
        raise InvalidFile(message="Le fichier contient des valeurs vides")


