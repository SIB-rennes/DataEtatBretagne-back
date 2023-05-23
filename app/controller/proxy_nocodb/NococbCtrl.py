import functools
import io
import logging
import pandas
import requests
from nocodb.infra.requests_client import NocoDBRequestsClient

from flask_restx import Namespace, Resource, abort, reqparse
from flask import current_app, make_response, request
from nocodb.nocodb import NocoDBProject, APIToken

from app.controller.Decorators import retry_on_exception

args_get = reqparse.RequestParser()
args_get.add_argument('sort', type=str, required=False, help="Champ à trier")
args_get.add_argument('fields', type=str, required=False, help="Liste des champs à remonter")
args_get.add_argument('where', type=str, required=False, help="Filtre nocodb sur la table")
args_get.add_argument('limit', type=int, required=False, help="Limit de résultat (max 1000), 20 par défaut")
args_get.add_argument('offset', type=int, required=False, help="Limit de résultat (max 1000), 20 par défaut")


api = Namespace(name="nocodb", path='/',
                description='API passe plats nocodb')

oidc = current_app.extensions['oidc']

@api.route('/<table>/<views>')
class NocoDb(Resource):
    @api.expect(args_get)
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @retry_on_exception(max_retry=3) # Ajout du décorateur ici
    def get(self, table, views):
        # le nom du projet correspond au nom du blueprint
        project = request.blueprint
        client = build_client(project)

        params = request.args
        logging.debug(f'[NOCODB] get {table} {views} with params {params}')
        try:
            table_rows = client.table_row_list(NocoDBProject("noco", project), f'{table}/views/{views}', params=params)
            if ('msg' in table_rows):
                logging.error(f'[NOCODB] Erreur sur la réponse {table_rows["msg"]}')
                return table_rows, 400
            else:
                logging.debug('[NOCODB] return response')
                return table_rows, 200
        except requests.exceptions.JSONDecodeError :
            logging.exception('[NOCODB] Error JSOnDecodeError')


@api.route('/<table>/<views>/csv')
@api.expect(args_get)
class ExportCsv(Resource):
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def get(self, table, views):
        project = request.blueprint
        client = build_client(project)
        params = request.args
        logging.debug(f'[NOCODB] get CSV {table} {views} where {params}')

        table_rows = client.table_row_list(NocoDBProject("noco", project), f'{table}/views/{views}', params=params)
        if ('msg' in table_rows):
            logging.error(f'[NOCODB] Erreur sur la réponse {table_rows["msg"]}')
            return table_rows, 400
        else :
            logging.debug('[NOCODB] return response')
            data = table_rows['list']
            # on met à plat les données
            df = pandas.json_normalize(data, sep='_', max_level=1)
            # supression des colonnes les identifiant technique contenant _Id
            df = df[df.columns.drop(list(df.filter(regex='_Id')))]
            my_csv_string = df.to_csv(index=False)

            output = io.StringIO()
            output.write(my_csv_string)
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=test.csv"
            response.headers["Content-type"] = "text/csv"
            logging.debug('[NOCODB] return response csv')
            return response


@api.route('/')
class HealthCheck(Resource):
    @api.response(200, 'Success')
    def get(self):
        project = request.blueprint
        logging.debug('[NOCODB] HealthCheck')
        build_client(project)
        return 200



@functools.cache
def build_client(project) -> NocoDBRequestsClient:
    '''
    Construit le client nocodb
    :param project: nom du projet
    :return:
    '''
    uri = current_app.config['NOCODB_URL']
    token = current_app.config['NOCODB_PROJECT'][project]

    if token is None :
        abort(403, f"Information manquante pour le projet {project}")
    try :
        return NocoDBRequestsClient(APIToken(token), uri)
    except Exception as clientException:
        logging.error(clientException)
        abort(500, f"Erreur interne ")


# def build_params(args):
#     params = {
#         'limit': 20 if  args['limit'] is None else args['limit'],
#         'offset': 0 if args['offset'] is None else args['offset'],
#         'sort': None if args['sort'] is None else args['sort'],
#         'fields':  None if args['fields'] is None else args['fields'],
#         'where': None if args['where'] is None else args['where']
#     }
#     return params