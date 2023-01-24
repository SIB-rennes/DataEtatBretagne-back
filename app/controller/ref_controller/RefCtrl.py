from flask import jsonify
from flask_restx import Namespace, Resource, reqparse
from sqlalchemy import text

from app import oidc, db

api = Namespace(name="referentiel", path='/',
                description='API referentiels')
parser_crte = reqparse.RequestParser()
parser_crte.add_argument("nom", type=str, required=False, help="Search on name")
parser_crte.add_argument("limit", type=int, required=False, default=5, help="Number of results")

@api.route('/crte')
class RefCrte(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.expect(parser_crte)
    def get(self):
        p_args = parser_crte.parse_args()
        name = f'%{p_args.get("nom")}%' if p_args.get("name") is not None else None
        limit = p_args.get("limit")
        if name is not None :
            result = db.engine.execute(text("SELECT DISTINCT label_crte, code_crte FROM ref_commune WHERE label_crte ilike :name ORDER BY label_crte  LIMIT :limit"),
                                       limit = limit, name=name).all()

        else :
            result = db.engine.execute(
                text("SELECT DISTINCT label_crte, code_crte FROM ref_commune ORDER BY label_crte LIMIT :limit"), limit=limit).all()

        return [{'nom': row[0], 'code':row[1]} for row in result], 200
