import logging

from flask import  current_app
from sqlalchemy.exc import NoResultFound

from app.controller.utils.Error import ErrorController


@current_app.errorhandler(NoResultFound)
def handle_not_result_found(e):
    return ErrorController("Aucune données n'est présente").to_json(), 404


@current_app.errorhandler(Exception)
def handler_exception(error):
    message = None
    if hasattr(error,'message') :
        message = error.message
    logging.exception(error)
    return ErrorController(message).to_json(), 500