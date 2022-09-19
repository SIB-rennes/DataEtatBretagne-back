"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for a list of runserver options.
"""
import logging

from app import create_app
from flask_script import Manager
from flask_migrate import upgrade as _upgrade

from app.script import ImportChorus

app_flask = create_app()
manager = Manager(app_flask)
manager.add_command('import', ImportChorus())

if __name__ == "__main__":
    with app_flask.app_context():
        _upgrade()

    logging.basicConfig(format='%(asctime)s.%(msecs)03d : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S', )
    logging.getLogger("data-transform").setLevel(logging.INFO)
    manager.run()
