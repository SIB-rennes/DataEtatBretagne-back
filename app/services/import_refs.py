import os
import re
import sys
from typing import List


import json
import logging
import pandas
from celery import subtask

from app import db, celeryapp
LOGGER = logging.getLogger()

celery = celeryapp.celery


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

@celery.task(name='import_file_ref')
def import_refs(file: str, class_name:str, columns: List , **kwargs):
    """Task that imports reference data from a file into the database.

Args:
           file (str): Path to the file containing the reference data.
           class_name (str): Name of the model class for the reference data.
           columns (List): List of column names in the reference data file.
           **kwargs: Optional keyword arguments for pandas.read_csv().

       Raises:
           MissingCodeColumns: If the 'Code' column is missing from the list of columns.
    """
    if 'code' not in columns:
        raise MissingCodeColumns()

    model = _get_instance_model_by_name(class_name)
    if _is_csv(file):
        df = pandas.read_csv(file, dtype=str, **kwargs)
    else:
        df =  pandas.read_excel(file, dtype=str, **kwargs)

    # Renommer les colonnes
    df.columns = columns
    try:
        for index, row in df.iterrows():
            if row.isna().code : # si le code est nan ou none, on passe
                continue
            subtask("import_line_one_ref").delay(class_name, row.to_json())
    except Exception as e:
        print(e)


@celery.task(name='import_line_one_ref')
def import_line_one_ref(class_name: str, row):
    """Task that imports a single line of reference data into the database.

        Args:
            class_name (str): Name of the model class for the reference data.
            row: A JSON string representing a single row of reference data.
    """
    model = _get_instance_model_by_name(class_name)
    row = json.loads(row)
    instance = db.session.query(model).filter_by(code=row['code']).one_or_none()
    if not instance:
        instance = model(**row)
        LOGGER.info('[IMPORT][REF] Ajout ref %s dans %s', model.__tablename__, row)
        db.session.add(instance)
    else:
        LOGGER.info('[IMPORT][REF] Update ref %s dans %s', model.__tablename__, row)
        for key in row.keys():
            try :
                setattr(instance, key, row[key])
            except AttributeError as e:
                LOGGER.warning("[IMPORT][REF] Error update attribute %s", key)
                raise  e
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        LOGGER.exception("[IMPORT][REF] Error sur ajout/maj ref %s dans %s ", model.__tablename__, row)
        raise e


def _is_csv(filename: str):
    # Extraire l'extension du nom de fichier
    file_ext = os.path.splitext(filename)[1]

    return file_ext.lower() != ".xlsx"

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