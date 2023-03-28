import os
import json
import logging
import re
import sys

from flask import current_app
from werkzeug.utils import secure_filename

from app.services.file_service import allowed_file, FileNotAllowedException


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


def import_refs(file, data):
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
            f'[IMPORT REF] Maj referentiel {cls_name}, '
            'columns {columns}, is_csv {is_csv}, '
            'kwargs {other_args}, fichier {filename}'
        )
        from app.tasks.import_refs_tasks import import_refs_task

        return  import_refs_task.delay(str(save_path), cls_name, columns, is_csv, **other_args)
    else:
        logging.error(f'[IMPORT REF] Fichier refusé {file.filename}')
        raise  FileNotAllowedException()


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