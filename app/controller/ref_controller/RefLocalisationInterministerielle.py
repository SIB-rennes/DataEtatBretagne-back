from flask import current_app
from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.refs.localisation_interministerielle import LocalisationInterministerielleSchema, \
    LocalisationInterministerielle

oidc = current_app.extensions['oidc']
api = Namespace(name="Localisation interministerielle Controller", path='/loc-interministerielle',
                description='API referentiels des localisations interministerielles ')

parser_get_loc = get_pagination_parser()
parser_get_loc.add_argument('query', type=str, required=False, help="Recherche sur le code, site ou label")

loc_schema = LocalisationInterministerielleSchema(many=True)
model_json = JSONSchema().dump(loc_schema)['definitions']['LocalisationInterministerielleSchema']

loc_model = api.schema_model('LocalisationInterministerielle', model_json)
pagination_model = api.schema_model('Pagination',Pagination.jsonschema)

pagination_loc_model = api.model('LocalisationInterministeriellePagination', {
    'items': fields.List(fields.Nested(loc_model)),
    'pageInfo': fields.Nested(pagination_model)
})

@api.route('')
@api.doc(model=pagination_loc_model)
class RefLocalisationInterministerielle(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Récupération des Localisations interministerielle")
    @api.expect(parser_get_loc)
    @api.response(200, 'Success', pagination_loc_model)
    @api.response(204, 'No Result')
    def get(self):
        query_param = QueryParam(parser_get_loc)
        if query_param.is_query_search():
            like = query_param.get_search_like_param()
            stmt =  db.select(LocalisationInterministerielle).where((LocalisationInterministerielle.code == query_param.query_search)
                                                                    | (LocalisationInterministerielle.site.ilike(like))
                                                                    | (LocalisationInterministerielle.label.ilike(like)))\
                .order_by(LocalisationInterministerielle.code)
        else:
            stmt = db.select(LocalisationInterministerielle).order_by(LocalisationInterministerielle.code)

        page_result = db.paginate(stmt, per_page= query_param.limit, page=query_param.page_number,error_out=False)

        if page_result.items == [] :
            return "",204

        result = loc_schema.dump(page_result.items)

        return {'items': result, 'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200

@api.route('/<code>')
@api.doc(model=loc_model)
class RefLocalisationByCode(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les informations d'une localisation interministerielle")
    @api.response(200, 'Success', loc_model)
    def get(self, code):
        try:
            result = db.session.execute(db.select(LocalisationInterministerielle).filter_by(code=code)).scalar_one()
            schema = LocalisationInterministerielleSchema()
            result = schema.dump(result)
            return result, 200
        except NoResultFound:
            return "", 404

parser_get_loc_child = get_pagination_parser()


@api.route('/<code>/loc-interministerielle')
@api.doc(model=loc_model)
class RefLocalisationByCodeParent(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les localisations ministerielle associées au code parent")
    @api.expect(parser_get_loc_child)
    @api.response(200, 'Success', pagination_loc_model)
    def get(self, code):

        query_param = QueryParam(parser_get_loc_child)
        stmt = db.select(LocalisationInterministerielle).where(LocalisationInterministerielle.code_parent == code)\
            .order_by(LocalisationInterministerielle.code)

        page_result = db.paginate(stmt, per_page=query_param.limit, page=query_param.page_number, error_out=False)

        if page_result.items == []:
            return "", 204

        result = loc_schema.dump(page_result.items)

        return {'items': result,
                'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200
