from flask import current_app
from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.refs.code_programme import CodeProgrammeSchema, CodeProgramme

oidc = current_app.extensions['oidc']
api = Namespace(name="Programme Controller", path='/programme',
                description='API referentiels des Programmes')

parser_get_bop = get_pagination_parser()
parser_get_bop.add_argument('query', type=str, required=False, help="Recherche sur le label ou code")


code_programme_schema = CodeProgrammeSchema(many=True)
bop_model_json = JSONSchema().dump(code_programme_schema)['definitions']['CodeProgrammeSchema']


bop_model = api.schema_model('Bop', bop_model_json)


pagination_model = api.schema_model('Pagination',Pagination.jsonschema)

pagination_bop_model = api.model('BopPagination', {
    'items': fields.List(fields.Nested(bop_model)),
    'pageInfo': fields.Nested(pagination_model)
})


@api.route('')
@api.doc(model=pagination_bop_model)
class RefBop(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Récupération des Bops")
    @api.expect(parser_get_bop)
    @api.response(200, 'Success', pagination_bop_model)
    @api.response(204, 'No Result')
    def get(self):
        query_param = QueryParam(parser_get_bop)
        if query_param.is_query_search():
            like_query = query_param.get_search_like_param()
            stmt = db.select(CodeProgramme).where((CodeProgramme.code == query_param.query_search)
                                                | (CodeProgramme.label.ilike(like_query))) \
                .order_by(CodeProgramme.code)
        else:
            stmt = db.select(CodeProgramme).order_by(CodeProgramme.code)

        page_result = db.paginate(stmt, per_page=query_param.limit, page=query_param.page_number, error_out=False)

        if page_result.items == []:
            return "", 204

        result = code_programme_schema.dump(page_result.items)

        return {'items': result,
                'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200



@api.route('/<code>')
@api.doc(model=bop_model)
class CodeProgrammeByCode(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les informations d'un BOP")
    @api.response(200, 'Success', bop_model)
    def get(self, code):
        try:
            result = db.session.execute(db.select(CodeProgramme).filter_by(code=code)).scalar_one()
            centre_cout_schema = CodeProgrammeSchema()
            result = centre_cout_schema.dump(result)
            return result, 200
        except NoResultFound:
            return "", 404
