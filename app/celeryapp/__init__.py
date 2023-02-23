from celery import Celery
from kombu import Queue

CELERY_TASK_LIST = [
    'app.tasks',
]

db_session = None
celery = None


def create_celery_app(_app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's config.

    Wrap all tasks in the context of the Flask application.

    :param _app: Flask app
    :return: Celery app
    """
    # New Relic integration
    # if os.environ.get('NEW_RELIC_CELERY_ENABLED') == 'True':
    #     _app.initialize('celery')

    celery = Celery(_app.import_name,
                    backend=_app.config['result_backend'],
                    broker=_app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(_app.config)
    celery.conf.task_queues = (
        Queue('file'),
        Queue('line'),
    )

    celery.conf.task_routes = [{
        'import_file_*': {
            'queue': 'file'
        },
        'update_all_*': {
            'queue': 'file'
        },
        'share_*': {
            'queue': 'line'
        },
        'import_line_*': {
            'queue': 'line'
        }
    }]

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

