import logging
from flask_restx import Namespace, Resource, reqparse, fields
from flask import abort

from app import oidc

from app.clients.data_subventions import get_or_make_app_api_subventions_client, Subvention, ActionProposee, RepresentantLegal

api = Namespace(name="Data Subventions", path='/',
                description='Proxy API Data Subventions')

_get_subventions_req_parser = reqparse.RequestParser()
_get_subventions_req_parser.add_argument('ej', type=str, help="Numéro d'ej", location='args')

action_proposee_model = api.schema_model('ActionProposee', ActionProposee.jsonschema())
subvention_model = api.schema_model('Subvention', Subvention.jsonschema())

reprensentant_legal_model = api.schema_model('RepresentantLegal', RepresentantLegal.jsonschema())
representants_legaux_model = api.model('RepresentantsLegaux',  {
    'representants_legaux': fields.List(fields.Nested(reprensentant_legal_model))
})


@api.route('/representants_legaux/<siret>')
@api.doc(model = representants_legaux_model)
class RepresentantLegauxCtrl(Resource):

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.response(200, 'Success', representants_legaux_model)
    def get(self, siret):
        logging.debug(f"[DATASUBVENTIONS][CTRL] Get representants legaux pour le siret {siret}")

        representants_legaux = _get_representants_legaux(siret)
        return {
            'representants_legaux': representants_legaux
        }

@api.route('/subventions/<siret>')
@api.doc(model = action_proposee_model)
@api.doc(model = subvention_model)
class SubventionsCtrl(Resource):

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.expect(_get_subventions_req_parser)
    @api.response(200, 'Success', subvention_model)
    def get(self, siret):
        args = _get_subventions_req_parser.parse_args()
        ej = args['ej']
        logging.debug(f"[DATASUBVENTIONS][CTRL] Get subventions pour le siret {siret} et l'EJ {ej}")

        subvention = _get_subvention(siret, ej)
        if subvention is None:
            abort(404, f"Aucune subvention pour l'établissement {siret} et l'ej {ej}")
        return subvention

def _get_subvention(siret: str, ej: str):
    client = get_or_make_app_api_subventions_client()
    subventions = client.get_subventions_pour_etablissement(siret)
    subventions = _avec_ej(subventions, ej)

    assert len(subventions) <=1, "On ne devrait avoir qu'une subvention pour un ej donné"

    if len(subventions) == 0:
        return None

    raw = Subvention.marshmallow_schemaclass()().dump(subventions[0])
    return raw

def _avec_ej(subventions: list[Subvention], ej: str) -> Subvention:
    return [s for s in subventions if s.ej == ej]

def _get_representants_legaux(siret: str):

    client = get_or_make_app_api_subventions_client()
    representants = client.get_representants_legaux_pour_etablissement(siret)

    raw = RepresentantLegal.marshmallow_schemaclass()(many=True).dump(representants)
    return raw
