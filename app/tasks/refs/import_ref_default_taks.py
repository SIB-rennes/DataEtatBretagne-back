import codecs

import json
import logging

from app import db, celeryapp
from app.services.import_refs import _get_instance_model_by_name
LOGGER = logging.getLogger()

celery = celeryapp.celery

@celery.task(name='import_line_one_ref_default')
def import_line_one_ref_default(model_name : str, data: str):
    """
    Cette fonction importe une ligne de référence par défaut dans une table de base de données.

        Args:
            model_name  (str): Le nom de la classe modèle dans laquelle importer la référence.
            data (str): Les données de la référence au format JSON.

        Raises:
            AttributeError: Si une erreur se produit lors de la mise à jour d'un attribut.
            Exception: Si une erreur se produit lors de l'ajout ou de la mise à jour de la référence dans la base de données.

    """
    model = _get_instance_model_by_name(model_name)
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
