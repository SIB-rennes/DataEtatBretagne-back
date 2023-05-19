import codecs

import json
import logging

from app import db, celeryapp
from app.services.import_refs import _get_instance_model_by_name
LOGGER = logging.getLogger()

celery = celeryapp.celery

@celery.task(name='import_line_one_ref_default')
def import_line_one_ref_default(cls: str, data: str):
    """Task default that imports a single line of reference data into the database.

        Args:
            class_name (str): Name of the model class for the reference data.
            row: A JSON string representing a single row of reference data.
    """
    model = _get_instance_model_by_name(cls)
    data = data.replace('\\"',r"'")
    row = json.loads(codecs.decode(data, 'unicode_escape'))

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
