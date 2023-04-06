
import sqlalchemy
from flask import  current_app

from flask_restx import Namespace, Resource, fields
from marshmallow_jsonschema import JSONSchema
from sqlalchemy.exc import NoResultFound

from app import db
from app.clients.keycloack.factory import make_or_get_keycloack_admin, KeycloakConfigurationException
from app.controller import ErrorController
from app.controller.Decorators import check_permission
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.audit.AuditUpdateData import AuditUpdateData, AuditUpdateDataSchema
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.enums.DataType import DataType
from app.models.enums.ConnectionProfile import ConnectionProfile

api = Namespace(name="audit", path='/audit',
                description='API de récupération des audits')

parser_get = get_pagination_parser(default_limit=5)

oidc = current_app.extensions['oidc']

schema_many = AuditUpdateDataSchema(many=True)

model_json = JSONSchema().dump(schema_many)['definitions']['AuditUpdateDataSchema']
model_single_api = api.schema_model('AuditUpdateDataSchema', model_json)
pagination_model = api.schema_model('Pagination', Pagination.definition_jsonschema)

pagination_with_model = api.model('AuditUpdateDataSchemaPagination', {
    'items': fields.List(fields.Nested(model_single_api)),
    'pageInfo': fields.Nested(pagination_model)
})

@api.errorhandler(KeyError)
def handle_type_not_exist(e):
    return ErrorController("Type inconnue").to_json(), 400


@api.route('/<type>')
@api.doc(params={'type': str([e.value for e in DataType])})
@api.doc(model=pagination_with_model)
class Audit(Resource):
    @api.response(200, 'List of update data')
    @api.doc(security="Bearer")
    @api.expect(parser_get)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.response(204, 'No Result')
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    def get(self, type: DataType):
        query_param = QueryParam(parser_get)
        enum_type = DataType[type]

        stmt = db.select(AuditUpdateData).where( (AuditUpdateData.data_type == enum_type.name)).order_by(AuditUpdateData.date.desc())
        page_result = db.paginate(stmt, per_page=query_param.limit, page=query_param.page_number, error_out=False)

        if page_result.items == []:
            return "", 204

        schema_many = AuditUpdateDataSchema(many=True)
        result = schema_many.dump(page_result.items)

        return {'items': result,
                'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200


@api.route('/<type>/last')
class AuditLastImport(Resource):

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.marshal_with(api.model("date-last-import",{'date': fields.DateTime}), code=200)
    def get(self, type: DataType):

        enum_type =  DataType[type]

        stmt = db.select(sqlalchemy.sql.functions.max(AuditUpdateData.date)).where(
            AuditUpdateData.data_type == enum_type.name)
        result = db.session.execute(stmt).scalar_one()
        if result is None:
            raise NoResultFound()

        return {"date": result.isoformat() }, 200


