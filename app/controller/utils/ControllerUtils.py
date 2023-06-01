import hashlib
from argparse import ArgumentTypeError

from flask import request
from flask_restx import reqparse

def get_origin_referrer(request):
    # This function returns the origin of the request if it is present
    # and it is not "localhost", otherwise it returns the referrer
    if request.origin is not None and "localhost" not in request.origin:
        return request.origin
    else:
        return request.host

def make_cache(*args, **kwargs):
    '''
    Construit le cache d'un méthode
    :param args:
    :param kwargs:
    :return:
    '''
    hash_object  = hashlib.sha256()
    hash_object.update(request.get_data())
    hash = hash_object.hexdigest()
    return str(hash)

def positive():
    def require_positive(value):
        number = int(value)
        if number < 0:
            return 0
        return number

    return require_positive

def get_pagination_parser(default_page_number = 1, default_limit = 100):
    """Returns a request parser for pagination parameters.

       Args:
           default_page_number (int, optional): The default page number. Defaults to 1.
           default_limit (int, optional): The default page size. Defaults to 100.

       Returns:
           RequestParser: The pagination request parser.
    """
    pagination_parser = reqparse.RequestParser()
    pagination_parser.add_argument("page_number", type=positive(), required=False, default=default_page_number, help="Numéro de la page de resultat")
    pagination_parser.add_argument("limit", type=positive(), required=False, default=default_limit, help="Nombre de résultat par page")
    return  pagination_parser