import io
import logging

from app import oidc
from flask_restx import Namespace, Resource, abort, reqparse
from flask import current_app, make_response, request
from nocodb.nocodb import NocoDBProject

from app.proxy_nocodb.client.NocoDBRequestsCustomClient import NocoDBRequestsCustomClient, get_auth_token

args_get = reqparse.RequestParser()
args_get.add_argument('sort', type=str, required=False, help="Champ à trier")
args_get.add_argument('fields', type=str, required=False, help="Liste des champs à remonter")
args_get.add_argument('where', type=str, required=False, help="Filtre nocodb sur la table")
args_get.add_argument('limit', type=int, required=False, help="Limit de résultat (max 1000), 20 par défaut")
args_get.add_argument('offset', type=int, required=False, help="Limit de résultat (max 1000), 20 par défaut")


api = Namespace(name="nocodb", path='/',
                description='API passe plats nocodb')

@api.route('/<table>/<views>')
class NocoDb(Resource):
    @api.expect(args_get)
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def get(self, table, views):
        # le nom du projet correspond au nom du blueprint
        project = request.blueprint
        client = build_client(project)

        params = build_params(args_get.parse_args())
        logging.debug(f'[NOCODB] get {table} {views} where {params}')
        table_rows = client.table_row_list(NocoDBProject("noco", project), f'{table}/views/{views}', params=params)
        logging.debug('[NOCODB] return response')
        return table_rows, 200


@api.route('/<table>/<views>/csv')
@api.expect(args_get)
class ExportCsv(Resource):
    @api.response(200, 'Success')
    @api.doc(security="Bearer")
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    def get(self, table, views):
        project = request.blueprint
        client = build_client(project)
        params = build_params(args_get.parse_args())
        logging.debug(f'[NOCODB] get CSV {table} {views} where {params}')
        table_rows = client.table_export_csv(NocoDBProject("noco", project), f'{table}/views/{views}',
                                             params=params)
        output = io.StringIO()
        output.write(table_rows.content.decode('utf-8'))
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=test.csv"
        response.headers["Content-type"] = "text/csv"
        logging.debug('[NOCODB] return response csv')
        return response



def build_client(project) -> NocoDBRequestsCustomClient:
    '''
    Construit le client nocodb
    :param project: nom du projet
    :return:
    '''
    uri = current_app.config['NOCODB_URL']
    email = current_app.config['NOCODB_TECH_LOGIN']
    pwd = current_app.config['NOCODB_TECH_PWD']

    if uri is None or email is None or pwd is None:
        abort(403, f"Information manquante pour le projet {project}")

    return NocoDBRequestsCustomClient(get_auth_token(uri, email, pwd), uri)

def build_params(args):
    params = {
        'limit': 20 if  args['limit'] is None else args['limit'],
        'offset': 0 if args['offset'] is None else args['offset'],
        'sort': None if args['sort'] is None else args['sort'],
        'fields':  None if args['fields'] is None else args['fields'],
        'where': None if args['where'] is None else args['where'],
    }
    return params