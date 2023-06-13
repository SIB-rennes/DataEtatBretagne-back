import sys

from flask import current_app
from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam

oidc = current_app.extensions['oidc']



def build_ref_controller(cls, namespace: Namespace, help_query="Recherche sur le code et le label", cond_opt: tuple=None):
    """
    Construit dynamiquement des endpoint pour un referentiel
    L'api contient un endpoint de recherche paginé, et une endpoint pour retourner un objet par son code

    :param cls:   La Classe du modèle. Le schema sera automatiquement détecté si le nom est le même que
    la classe, suffixé par Schema
    :param namespace:  Le namespace du controller
    :param help_query:  Spécification de l'aide pour l'api de recherche
    :param cond_opt:    des Clause supplémentaire pour rechercher des objets. par défaut, on recherche sur le 'code' et le 'label'.
        Exemple pour ajouter un attribut "code_postal" : cond_opt=(CentreCouts.code_postal,)
    :return:
    """
    api = namespace

    module_name = cls().__class__.__module__
    schema = getattr(sys.modules[module_name], f"{cls.__name__}Schema")


    parser_get = get_pagination_parser()
    parser_get.add_argument('query', type=str, required=False, help=help_query)

    schema_many = schema(many=True)

    model_json = JSONSchema().dump(schema_many)['definitions'][schema.__name__]
    model_single_api = api.schema_model(cls.__name__, model_json)
    pagination_model = api.schema_model('Pagination',Pagination.definition_jsonschema)

    pagination_with_model = api.model(f'{cls.__name__}Pagination', {
        'items': fields.List(fields.Nested(model_single_api)),
        'pageInfo': fields.Nested(pagination_model)
    })

    @api.route('')
    @api.doc(model=pagination_with_model)
    class RefControllerList(Resource):
        @oidc.accept_token(require_token=True, scopes_required=['openid'])
        @api.doc(security="Bearer")
        @api.expect(parser_get)
        @api.response(200, 'Success', pagination_with_model)
        @api.response(204, 'No Result')
        def get(self):
            query_param = QueryParam(parser_get)
            if query_param.is_query_search():
                where_clause = _build_where_clause(cls, query_param, cond_opt)
                stmt = db.select(cls).where(where_clause).order_by(cls.code)
            else:
                stmt = db.select(cls).order_by(cls.code)

            page_result = db.paginate(stmt, per_page=query_param.limit, page=query_param.page_number, error_out=False)

            if page_result.items == []:
                return "", 204

            result = schema_many.dump(page_result.items)

            return {'items': result,
                    'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200

    @api.route('/<code>')
    @api.doc(model=model_single_api)
    class RefByCode(Resource):
        @oidc.accept_token(require_token=True, scopes_required=['openid'])
        @api.doc(security="Bearer")
        @api.response(200, 'Success', model_single_api)
        def get(self, code):
            try:
                result = db.session.execute(db.select(cls).filter_by(code=code)).scalar_one()
                schema_m = schema()
                result = schema_m.dump(result)
                return result, 200
            except NoResultFound:
                return "", 404
    return api




def _build_where_clause(cls,query_param: QueryParam, cond_opt: tuple):
    """
    Construit dynamiquement la clause where de la query de recherche
    :param cls:     l'instance de la clase
    :param query_param: l'objet QueryParam pour la recherche
    :param cond_opt:    les conditions supplémentaire
    :return:
    """
    like = query_param.get_search_like_param()

    where_clause = ((cls.code.ilike(like)) | (cls.label.ilike(like)))

    if cond_opt is not None:
        for cond in cond_opt:
            where_clause = where_clause | cond.ilike(like)

    return where_clause












