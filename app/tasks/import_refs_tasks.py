import codecs
from typing import List


import json
import logging
import pandas
from celery import subtask

from app import db, celeryapp
from app.services import MissingCodeColumns
from app.services.import_refs import _get_instance_model_by_name

LOGGER = logging.getLogger()

celery = celeryapp.celery

@celery.task(name='import_file_ref', bind=True)
def import_refs_task(self, file: str, class_name:str, columns: List , is_csv=True, **kwargs):
    """Task that imports reference data from a file into the database.

Args:
           file (str): Path to the file containing the reference data.
           class_name (str): Name of the model class for the reference data.
           columns (List): List of column names in the reference data file.
           is_csv (bool): File is csv or not
           **kwargs: Optional keyword arguments for pandas.read_csv().

       Raises:
           MissingCodeColumns: If the 'Code' column is missing from the list of columns.
    """
    if 'code' not in columns:
        raise MissingCodeColumns()

    model = _get_instance_model_by_name(class_name)
    if is_csv:
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
def import_line_one_ref(class_name: str, row: str):
    """Task that imports a single line of reference data into the database.

        Args:
            class_name (str): Name of the model class for the reference data.
            row: A JSON string representing a single row of reference data.
    """
    model = _get_instance_model_by_name(class_name)
    row = json.loads(codecs.decode(row,'unicode_escape'))
    check_model = model(**row)
    instance = db.session.query(model).filter_by(code=check_model.code).one_or_none()
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
