import logging

from flask import current_app, request

from flask_restx import Namespace, Resource, fields

from app import cache
from app.services.api_externes import ApisExternesService
from app.models.apis_externes.entreprise import InfoApiEntreprise
from app.models.apis_externes.subvention import InfoApiSubvention
from app.models.apis_externes.error import Error as ApiError


api = Namespace(
    name="External APIs",
    path="/",
    description="Controlleur qui construit les données via les APIs externes (api entreprise, data_subvention etc..)",
)

oidc = current_app.extensions["oidc"]

service = ApisExternesService()


def _document_error_responses(api: Namespace):
    """Décorateur qui décrit les différentes réponses en erreur possibles"""

    def decorator(f):
        @api.response(
            500,
            "Lors d'une erreur inconnue",
            model=ApiError.schema_model(api),
        )
        @api.response(
            429,
            "Lors d'une erreur inconnue",
            model=ApiError.schema_model(api),
        )
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        return inner

    return decorator


@api.route("/info-subvention/<siret>")
class InfoSubventionCtrl(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, "Success", model=InfoApiSubvention.schema_model(api))
    @_document_error_responses(api)
    def get(self, siret: str):
        logging.info(f"[API EXTERNES][CTRL] Info subventions")

        subvention = service.subvention(siret)
        json = InfoApiSubvention.ma_schema.dump(subvention)
        return json


parser_ds = api.model('query', {
    'operationName': fields.String(required=True),
    'query': fields.String,
    'variables': fields.Raw(required=False)
})

@api.route("/demarche-simplifie")
class DemarcheSimplifie(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.expect(parser_ds)
    @_document_error_responses(api)
    @cache.cached(timeout=300)
    def post(self):
        return service.api_demarche_simplifie.do_post(request.get_data())




@api.route("/info-entreprise/<siret>")
class InfoEntrepriseCtrl(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(
        200,
        "Informations de l'API entreprise",
        model=InfoApiEntreprise.schema_model(api),
    )
    @_document_error_responses(api)
    def get(self, siret: str):
        logging.info(f"[API EXTERNES][CTRL] Info entreprise")

        entreprise = service.entreprise(siret)
        json = InfoApiEntreprise.ma_schema.dump(entreprise)
        return json
