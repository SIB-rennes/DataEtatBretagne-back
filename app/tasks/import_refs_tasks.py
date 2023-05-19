from typing import List

import logging
import pandas
from celery import subtask
from celery import current_app
from app import celeryapp
from app.services import MissingCodeColumns
from app.services.import_refs import _get_instance_model_by_name
from app.tasks import limiter_queue, LimitQueueException

LOGGER = logging.getLogger()

celery = celeryapp.celery

@celery.task(name='import_file_ref', bind=True)
def import_refs_task(self, file: str, model_name:str, columns: List , is_csv=True, **kwargs):
    """Task that imports reference data from a file into the database.

Args:
           file (str): Path to the file containing the reference data.
           model_name (str): Name of the model class for the reference data.
           columns (List): List of column names in the reference data file.
           is_csv (bool): File is csv or not
           **kwargs: Optional keyword arguments for pandas.read_csv().

       Raises:
           MissingCodeColumns: If the 'Code' column is missing from the list of columns.
    """
    if 'code' not in columns:
        raise MissingCodeColumns()

    model = _get_instance_model_by_name(model_name)
    if is_csv:
        df = pandas.read_csv(file, dtype=str, **kwargs)
    else:
        df =  pandas.read_excel(file, dtype=str, **kwargs)

    # Renommer les colonnes
    df.columns = columns

    # déterminiation de la task name
    task_name = 'import_line_one_ref_default'
    if (check_task_exists(f'import_line_one_ref_{model_name}')):
        task_name = f'import_line_one_ref_{model_name}'

    try:
        for index, row in df.iterrows():
            if row.isna().code : # si le code est nan ou none, on passe
                continue
            send_subtask(task_name, model_name=model_name, data=row.to_json())
    except LimitQueueException as e:
        LOGGER.exception('[IMPORT][REFS] Error limit queue exception', e)
        raise e

@limiter_queue(queue_name='line')
def send_subtask(task_name,model_name, data):
    subtask(task_name).delay(model_name=model_name, data=data)

def check_task_exists(task_name):

    return task_name in list(name for name in current_app.tasks
                        if name.startswith('import_line_one_ref_'))
