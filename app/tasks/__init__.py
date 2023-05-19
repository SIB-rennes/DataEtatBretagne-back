from functools import wraps
from time import sleep
from flask import current_app

from app import celeryapp
import redis

celery = celeryapp.celery
from celery import current_app


__all__= ('limiter_queue','LimitQueueException',)

MAX_QUEUE_SIZE = 'max_queue_size'
TIMEOUT_QUEUE_RETRY = 'timeout_queue_retry'
DEFAULT_MAX_QUEUE_SIZE = 100000
DEFAULT_TIMEOUT_QUEUE_RETRY = 60

if current_app.conf.broker_url is None:
    redis_conn = None
else :
    redis_conn = redis.from_url(current_app.conf.broker_url)

max_queue_size = current_app.conf[MAX_QUEUE_SIZE] if MAX_QUEUE_SIZE in current_app.conf else DEFAULT_MAX_QUEUE_SIZE
timeout_queue_retry = current_app.conf[TIMEOUT_QUEUE_RETRY] if TIMEOUT_QUEUE_RETRY in current_app.conf else DEFAULT_TIMEOUT_QUEUE_RETRY

def limiter_queue(queue_name:str, max_queue_size: int = max_queue_size, timeout_queue_retry: int = timeout_queue_retry):
    """
    Vérifie que le nombre de message dans la file "queue_name" de redis n'atteint pas la taille max
    Si taille max dépassé, attente de 1 seconde.
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            if not current_app.conf.task_always_eager or redis_conn is not None:
                num_retries=0
                while redis_conn.llen(queue_name) > max_queue_size:
                    if num_retries >= timeout_queue_retry:
                        raise LimitQueueException(f"Timeout exceeded while waiting for the queue '{queue_name}' to be available.")
                    sleep(1)
                    num_retries +=1

            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper


class LimitQueueException(Exception):
    pass


from .siret import *
from .import_financial_tasks import *
from .management_tasks import *
from .import_refs_tasks import *
from .refs import *