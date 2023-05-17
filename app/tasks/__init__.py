from functools import wraps
from time import sleep

from app import celeryapp
import redis

celery = celeryapp.celery

__all__= ('limiter_queue',)

redis_conn = redis.from_url(celery._preconf['broker_url'])
def limiter_queue():
    """
    Vérifie sur la request contient les bon paramètres
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            while redis_conn.llen('line') > 2:
                sleep(1)

            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper

from .siret import *
from .import_financial_tasks import *
from .management_tasks import *
from .import_refs_tasks import *
from .refs import *