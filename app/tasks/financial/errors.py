from functools import wraps
from api_entreprise import LimitHitError
import sqlalchemy

from app.tasks.financial import logger
from app.tasks.management_tasks import sqlalchemy

class Reessayer(Exception):
    """Exception qui commande à l'import de réessayer"""
    
    def __init__(self, delai: float = 10.0, max_retries = 1):
        self.max_retries = max_retries
        """Nombre de retry maximum"""
        self.delai = delai
        """Delai d'attente en seconde"""
    
    @staticmethod
    def fromLimitHitError(cause: LimitHitError):

        delai = (cause.delay) + 5
        e = Reessayer(delai, max_retries=None)
        e.__cause__ = cause
        return e
    
    @staticmethod
    def fromIntegrityError(cause: sqlalchemy.exc.IntegrityError):

        delai = 10
        e = Reessayer(delai, max_retries=4)
        e.__cause__ = cause
        return e

class AnnuleLaTache(Exception):
    """Exception qui commande à la tâche en cours de s'annuler. ie: echouer silencieusement """

    @staticmethod
    def fromUniqueViolationOnFileLineImport(cause: sqlalchemy.exc.IntegrityError):
        e = AnnuleLaTache()
        e.__cause__ = cause
        return e


def _handle_exception_import(name):
    """
    Gère les exceptions pour les imports
    S'attend à être utilisé en conjonction des tâches celery
    ```
    ...
    @celery.task(...)
    @_handle_exception_import('nom')
    def import_func():
        ...
    ...
    ```
    """
    def wrapper(func):

        @_map_exceptions
        def mapped(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        def inner_wrapper(caller, *args, **kwargs):
            try :
                return mapped(caller, *args, **kwargs)
            except Reessayer as e:
                # XXX: max_retries=None ne désactive pas le mécanisme
                # de retry max contrairement à ce que stipule la doc !
                # on met donc un grand nombre.
                nb_retries = e.max_retries if e.max_retries is not None else 1000
                caller.retry(countdown=e.delai, max_retries=nb_retries, retry_jitter = True)
            
            except AnnuleLaTache as e:
                logger.warning(f"[IMPORT][{name}] tâche annulée.")
                return "tâche annulée"

            except Exception as e:
                logger.exception(f"[IMPORT][{name}] erreur")
                raise e

        return inner_wrapper

    return wrapper

def _map_exceptions(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:

            return func(*args, **kwargs)

        except LimitHitError as e:
            logger.info( f"[IMPORT] Limite d'appel à l'API entreprise atteinte.")
            raise Reessayer.fromLimitHitError(e)

        except sqlalchemy.exc.IntegrityError as e:
            message = str(e)

            # Cas de doublon en insertion de ligne, on peut annuler la tache silencieusement.
            if "duplicate key value violates unique constraint" in message \
                and "uq_file_line_import" in message:

                logger.warning("On tente d'insérer une ligne deux fois. On ignore le second insert.")
                raise AnnuleLaTache.fromUniqueViolationOnFileLineImport(e)
                
            msg = "IntegrityError. Cela peut être dû à un soucis de concourrence. On retente."
            logger.exception(f"[IMPORT] {msg}")
            raise Reessayer.fromIntegrityError(e)

    return inner
        
