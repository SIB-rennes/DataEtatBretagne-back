from flask import current_app
from flask_restx import Namespace, Resource

from app import db
from app.controller.ref_controller import build_ref_controller
from app.controller.utils.ControllerUtils import get_pagination_parser
from app.models.common.Pagination import Pagination
from app.models.common.QueryParam import QueryParam
from app.models.refs.localisation_interministerielle import LocalisationInterministerielleSchema, \
    LocalisationInterministerielle

oidc = current_app.extensions['oidc']

api = build_ref_controller(LocalisationInterministerielle,
                                  Namespace(name="Localisation interministerielle Controller", path='/loc-interministerielle',
                                            ddescription='API referentiels des localisations interministerielles'),
                           cond_opt=(LocalisationInterministerielle.site,)
                                  )

parser_get_loc_child = get_pagination_parser()


@api.route('/<code>/loc-interministerielle')
@api.doc(model=api.models['LocalisationInterministerielle'])
class RefLocalisationByCodeParent(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer", description="Remonte les localisations ministerielle associées au code parent")
    @api.expect(parser_get_loc_child)
    @api.response(200, 'Success', api.models['LocalisationInterministeriellePagination'])
    def get(self, code):

        query_param = QueryParam(parser_get_loc_child)
        stmt = db.select(LocalisationInterministerielle).where(LocalisationInterministerielle.code_parent == code)\
            .order_by(LocalisationInterministerielle.code)

        page_result = db.paginate(stmt, per_page=query_param.limit, page=query_param.page_number, error_out=False)

        if page_result.items == []:
            return "", 204

        result = LocalisationInterministerielleSchema(many=True).dump(page_result.items)

        return {'items': result,
                'pageInfo': Pagination(page_result.total, page_result.page, page_result.per_page).to_json()}, 200
