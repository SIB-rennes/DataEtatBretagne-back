from flask import current_app
from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.refs.centre_couts import CentreCoutsSchema, CentreCouts

oidc = current_app.extensions['oidc']
api = Namespace(name="Centre couts Controller", path='/centre-couts',
                description='API referentiels des Centre de couts')

parser_get_cc = get_pagination_parser()
parser_get_cc.add_argument('query', type=str, required=False, help="Recherche sur le label, code ou code_postal")



centre_cout_schema = CentreCoutsSchema(many=True)
model_json = JSONSchema().dump(centre_cout_schema)['definitions']['CentreCoutsSchema']

centre_cout_model = api.schema_model('CentreCouts', model_json)
pagination_model = api.schema_model('Pagination',Pagination.jsonschema)

pagination_centre_cout_model = api.model('CentreCoutsPagination', {
    'items': fields.List(fields.Nested(centre_cout_model)),
    'pageInfo': fields.Nested(pagination_model)
})


@api.route('')
@api.doc(model=pagination_centre_cout_model)
class RefCentreCouts(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Récupération des Centre de Couts")
    @api.expect(parser_get_cc)
    @api.response(200, 'Success', pagination_centre_cout_model)
    @api.response(204, 'No Result')
    def get(self):
        query_param = QueryParam(parser_get_cc)
        if query_param.is_query_search():
            like = query_param.get_search_like_param()
            stmt =  db.select(CentreCouts).where( (CentreCouts.code_postal == query_param.query_search)
                                                  | (CentreCouts.code.ilike(like))
                                                  | (CentreCouts.label.ilike(like) ))\
                .order_by(CentreCouts.code)
        else :
            stmt = db.select(CentreCouts).order_by(CentreCouts.code)

        page_result = db.paginate(stmt, per_page= query_param.limit, page=query_param.page_number,error_out=False)

        if page_result.items == [] :
            return "",204

        result = centre_cout_schema.dump(page_result.items)

        return {'items': result, 'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200

@api.route('/<code>')
@api.doc(model=centre_cout_model)
class CentreCoutByCode(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les informations d'un centre de couts")
    @api.response(200, 'Success', centre_cout_model)
    def get(self, code):
        try:
            result = db.session.execute(db.select(CentreCouts).filter_by(code=code)).scalar_one()
            centre_cout_schema = CentreCoutsSchema()
            result = centre_cout_schema.dump(result)
            return result, 200
        except NoResultFound:
            return "", 404





