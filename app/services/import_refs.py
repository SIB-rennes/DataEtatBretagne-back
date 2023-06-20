import os
import json
import logging
import re
import sys
from dataclasses import dataclass
from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.exceptions.exceptions import FileNotAllowedException
from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.DataType import DataType
from app.services.file_service import allowed_file


class MissingCodeColumns(Exception):
    """Exception raised when the 'Code' column is missing from the list of columns."""
    def __init__(self, message="The list does not contain the 'Code' value."):
        self.message = message
        super().__init__(self.message)

class ReferentielNotFound(Exception):
    """Exception raised when a referential file does not exist."""
    def __init__(self, name="", message="The referential file does not exist:"):
        self.message = message
        self.name = name
        super().__init__(f'{self.message} {self.name}')


@dataclass
class RefTaskImportChorus():
    cls_name:str
    columns: list[str]
    usecols: list[int]
    sheet_name: str
    skiprows: int



LIST_REF_TASK_IMPORT : list[RefTaskImportChorus] = [
    RefTaskImportChorus(cls_name='CodeProgramme', columns = ['code_ministere','code','label'], usecols= [0,2,3],sheet_name="03 - Programmes", skiprows=8),
    RefTaskImportChorus(cls_name='Ministere', columns=['code', 'sigle_ministere','label'], usecols=[0,1,2],
                        sheet_name="02 - Ministères" ,skiprows=8),
    RefTaskImportChorus(cls_name='DomaineFonctionnel', columns=['code', 'label'], usecols=[4,5],
                        sheet_name="07 - Domaines Fonct. (DF)", skiprows=8),
    RefTaskImportChorus(cls_name='GroupeMarchandise', columns=['domaine','segment','code', 'label', 'description','code_pce','label_pce'],usecols=[1,3,4,5,7,10,11],
                        sheet_name="19 - Groupe Marchandise", skiprows=8),
    RefTaskImportChorus(cls_name='ReferentielProgrammation',columns=['code', 'label'],usecols=[9, 10],
                        sheet_name="08 - Activités (OS,OP,OB,ACT)", skiprows=8),
]


def import_refs(file, data, username=""):
    try:
        _get_instance_model_by_name(data['class_name'])
    except ReferentielNotFound as exception:
        logging.exception('Error Referentiel not found')
        raise exception
    cls_name = data['class_name']
    columns = data['columns'].split(',')
    is_csv = True
    if 'is_csv' in data and data['is_csv'] == 'false':
        is_csv = False
    other_args = json.loads(data['other']) if 'other' in data else {}

    if file and allowed_file(file.filename, {'csv','ods','xls','xlsx'}):
        # save du fichier
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        logging.info(
            f'[IMPORT REF] Maj referentiel {cls_name},columns {columns}, is_csv {is_csv},kwargs {other_args}, fichier {filename}'
        )
        from app.tasks.import_refs_tasks import import_refs_task

        task = import_refs_task.delay(str(save_path), cls_name, columns, is_csv, **other_args)
        try:
            db.session.add(
                AuditUpdateData(username=username, filename=file.filename, data_type=DataType.REFERENTIEL))
            db.session.commit()
        except Exception:
            logging.exception('[IMPORT REF] Erreur saving AuditUpdateData')
        return task
    else:
        logging.error(f'[IMPORT REF] Fichier refusé {file.filename}')
        raise  FileNotAllowedException()


def import_ref_calculette(file, username = ""):
    """
    Import en masse les référentiels issue de chorus
    :param file:    le fichier calculette de chorus
    :param username: le nom de l'utilisateur
    :return:
    """
    if file and allowed_file(file.filename, allowed_extensions={'xlsx'}):
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        logging.info(
            f'[IMPORT REF][calculettre] Maj referentiel référentiel chorus fichier {filename}'
        )

        from app.tasks.import_refs_tasks import import_refs_task
        for ref in LIST_REF_TASK_IMPORT:
            logging.info(
                f'[IMPORT REF] Send task Maj ref for {ref.cls_name}'
            )
            import_refs_task.delay(str(save_path),ref.cls_name, ref.columns, is_csv=False, usecols=ref.usecols, skiprows=ref.skiprows, sheet_name=ref.sheet_name)

        try:
            db.session.add(
                AuditUpdateData(username=username, filename=file.filename, data_type=DataType.REFERENTIEL))
            db.session.commit()
        except Exception:
            logging.exception('[IMPORT REF] Erreur saving AuditUpdateData')
    else:
        logging.error(f'[IMPORT REF] Fichier refusé {file.filename}')
        raise FileNotAllowedException()

def _get_instance_model_by_name(class_name: str):
    """Get the model class object for a given class name.

        Args:
            class_name (str): Name of the model class.

        Returns:
            model class object.

        Raises:
            ReferentielNotFound: If the model class object is not found.

    """
    file_name = re.sub('(?<!^)(?=[A-Z])', '_', class_name).lower()
    try :
        return getattr(sys.modules['app.models.refs.'+file_name], class_name)
    except KeyError:
        raise ReferentielNotFound(name=class_name)