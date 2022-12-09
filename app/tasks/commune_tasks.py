import logging
import time

from app import db, celeryapp
from app.clients import get_info_commune
from app.models.refs.commune import Commune

LOGGER = logging.getLogger()

celery = celeryapp.celery


@celery.task(name='update_all_ref_commune_task', bind=True)
def maj_all_communes_tasks(self):
    LOGGER.info('[UPDATE][COMMUNE] Start')

    communes = Commune.query.filter(Commune.code_epci == None).all()
    index = 0
    for commune in communes:
        index += 1
        if (index == 40):
            LOGGER.info('[UPDATE][COMMUNE] sleep 1s après 40 appel api geo')
            index = 0
            time.sleep(1)

        commune = maj_one_commune(commune)
        logging.info(f'[UPDATE][COMMUNE] {commune.code_commune} {commune.label_commune}')
        db.session.commit()


def maj_one_commune(commune: Commune):
    """
    Lance la MAj d'une communce
    :param commune:
    :return:
    """
    apigeo = get_info_commune(commune)
    commune.label_commune = apigeo['nom']
    if 'epci' in apigeo:
        commune.code_epci = apigeo['epci']['code']
        commune.label_epci = apigeo['epci']['nom']
    if 'region' in apigeo:
        commune.code_region = apigeo['region']['code']
        commune.label_region = apigeo['region']['nom']
    if 'departement' in apigeo:
        commune.code_departement = apigeo['departement']['code']
        commune.label_departement = apigeo['departement']['nom']
    return commune



