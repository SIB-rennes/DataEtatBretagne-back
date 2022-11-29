"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for a list of runserver options.
"""

from app import create_app_base
from flask_script import Manager


app_flask = create_app_base(init_falsk_migrate=False)
manager = Manager(app_flask)

if __name__ == "__main__":

    manager.run()
