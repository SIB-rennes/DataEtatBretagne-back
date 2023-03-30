import logging
from flask import current_app

from flask_restx import Namespace, Resource

from app.services.api_externes import ApisExternesService
from app.models.apis_externes.entreprise import InfoApiEntreprise

api = Namespace(name="External APIs", path='/', 
                description="Controlleur qui construit les données via les APIs externes (api entreprise, data_subvention etc..)")

oidc = current_app.extensions['oidc']

service = ApisExternesService()

@api.route('/hello_world')
class HelloWorldCtrl(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, 'Success')
    def get(self, siret):
        logging.info(f"[API EXTERNES][CTRL] Hello world")

        return 200,"Success"

@api.route('/info_subvention/<siret>')
class InfoSubventionCtrl(Resource):

    # TODO: put back
    # @oidc.accept_token(require_token=True, scopes_required=['openid'])
    # @api.doc(security="Bearer")
    @api.response(200, 'Success')
    def get(self, siret: str):
        logging.info(f"[API EXTERNES][CTRL] Info subventions")
        return service.subvention(siret)
    
@api.route('/info_entreprise/<siret>')
class InfoEntrepriseCtrl(Resource):
    # TODO: put back
    # @oidc.accept_token(require_token=True, scopes_required=['openid'])
    # @api.doc(security="Bearer")
    @api.response(200, 'Success', model = InfoApiEntreprise.schema_model(api))
    def get(self, siret: str):
        logging.info(f"[API EXTERNES][CTRL] Info entreprise")

        entreprise = service.entreprise(siret)
        json = InfoApiEntreprise.ma_schema.dump(entreprise)
        return json

