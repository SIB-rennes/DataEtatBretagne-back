from datetime import timedelta
from celery.schedules import crontab

RESULT_EXPIRES = None # Sinon, beat nettoie le result backend

TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {
    'importe-ademe-auto': {
        'task': 'import_file_ademe_from_website',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
        'args': ('https://www.data.gouv.fr/fr/datasets/r/e8a06bbd-08bb-448b-b040-2a2666b1e082',),
    },
}