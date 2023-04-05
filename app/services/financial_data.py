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
from app.models.financial.Chorus import Chorus
from app.services import allowed_file, FileNotAllowedException

def import_ae(file_chorus, source_region:str ,annee: int, force_update: bool,username=""):

    if file_chorus.filename == '':
        raise InvalidFile(message="Pas de fichier")

    if file_chorus and allowed_file(file_chorus.filename):

        filename = secure_filename(file_chorus.filename)
        if 'UPLOAD_FOLDER' in current_app.config:
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else :
            save_path = os.path.join(tempfile.gettempdir(), filename)
        file_chorus.save(save_path)
        check_file(save_path)

        logging.info(f'[IMPORT CHORUS] Récupération du fichier {filename}')
        from app.tasks.import_chorus_tasks import import_file_ae_chorus
        task = import_file_ae_chorus.delay(str(save_path), source_region, annee, force_update)

        db.session.add(AuditUpdateData(username=username, filename=file_chorus.filename,data_type=DataType.FINANCIAL_DATA))
        db.session.commit()
        return task
    else:
        logging.error(f'[IMPORT CHORUS] Fichier refusé {file_chorus.filename}')
        raise FileNotAllowedException(message='le fichier n\'est pas un csv')




def check_file(fichier):
    try:
        data_chorus = pandas.read_csv(fichier, sep=",", skiprows=8, nrows=5,
                                      names=Chorus.get_columns_files_ae(),
                                       dtype={'programme': str, 'n_ej': str, 'n_poste_ej': int,
                                                     'fournisseur_titulaire': str,
                                                     'siret': 'str'})
    except Exception:
        logging.exception(msg="[CHECK FILE]Erreur de lecture du fichier")
        raise FileNotAllowedException(message="Erreur de lecture du fichier")

    if data_chorus.isnull().values.any():
        raise InvalidFile(message="Le fichier contient des valeurs vides")


