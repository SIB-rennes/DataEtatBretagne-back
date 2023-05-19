"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for a list of runserver options.
"""
#import redis

from app import create_app_base

# r = redis.from_url('redis://57.128.45.224:60379/1')
# r.llen('line')

app_flask = create_app_base()

if __name__ == "__main__":
    app_flask.run()
