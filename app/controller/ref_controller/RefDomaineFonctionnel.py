from flask import current_app
from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.refs.domaine_fonctionnel import DomaineFonctionnelSchema, DomaineFonctionnel

oidc = current_app.extensions['oidc']
api = Namespace(name="Domaine fonctionnel Controller", path='/domaine-fonct',
                description='API referentiels des Domaines Fonctionnels ')

parser_get_cc = get_pagination_parser()
parser_get_cc.add_argument('query', type=str, required=False, help="Recherche sur le label ou code")

domaine_schema = DomaineFonctionnelSchema(many=True)
model_json = JSONSchema().dump(domaine_schema)['definitions']['DomaineFonctionnelSchema']

domaine_model = api.schema_model('DomaineFonctionnel', model_json)
pagination_model = api.schema_model('Pagination',Pagination.jsonschema)

pagination_domaine_model = api.model('DomainesFonctionnelsPagination', {
    'items': fields.List(fields.Nested(domaine_model)),
    'pageInfo': fields.Nested(pagination_model)
})

@api.route('')
@api.doc(model=pagination_domaine_model)
class RefDomaineFonctionnels(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Récupération des Domaines fonctionnels")
    @api.expect(parser_get_cc)
    @api.response(200, 'Success', pagination_domaine_model)
    @api.response(204, 'No Result')
    def get(self):
        query_param = QueryParam(parser_get_cc)
        if query_param.is_query_search():
            like = query_param.get_search_like_param()
            stmt =  db.select(DomaineFonctionnel).where((DomaineFonctionnel.code.ilike(like))
                                                  | (DomaineFonctionnel.label.ilike(like) ))\
                .order_by(DomaineFonctionnel.code)
        else :
            stmt = db.select(DomaineFonctionnel).order_by(DomaineFonctionnel.code)

        page_result = db.paginate(stmt, per_page= query_param.limit, page=query_param.page_number,error_out=False)

        if page_result.items == [] :
            return "",204

        result = domaine_schema.dump(page_result.items)

        return {'items': result, 'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200

@api.route('/<code>')
@api.doc(model=domaine_model)
class DomaineFonctionnelByCode(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les informations d'un domaine fonctionnel")
    @api.response(200, 'Success', domaine_model)
    def get(self, code):
        try:
            result = db.session.execute(db.select(DomaineFonctionnel).filter_by(code=code)).scalar_one()
            domaine_schema = DomaineFonctionnelSchema()
            result = domaine_schema.dump(result)
            return result, 200
        except NoResultFound:
            return "", 404





