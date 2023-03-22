from flask import current_app
from flask_restx import Namespace, Resource, reqparse, fields
from sqlalchemy import text, bindparam

from app import db

api = Namespace(name="CRTE Controller", path='/crte',
                description='API referentiels des CRTE')
parser_crte = reqparse.RequestParser()
parser_crte.add_argument("nom", type=str, required=False, help="Recherche sur le nom du CRTE")
parser_crte.add_argument("departement", type=str, required=False, help="Recherche sur le numéro du département")
parser_crte.add_argument("limit", type=int, required=False, default=500, help="Nombre de résultat")

oidc = current_app.extensions['oidc']

crte_model = api.model('crte',model=  {
    'code': fields.String(),
    'nom': fields.String()
})

@api.route('')
@api.doc(model=crte_model)
class RefCrte(Resource):
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.expect(parser_crte)
    @api.response(200, 'Success', fields.List(fields.Nested(crte_model)))
    def get(self):
        p_args = parser_crte.parse_args()
        name = f'%{p_args.get("nom")}%' if p_args.get("nom") is not None else None
        dept = p_args.get("departement") if p_args.get("departement") is not None else None
        limit = p_args.get("limit")
        sql_select = "SELECT DISTINCT label_crte, code_crte FROM ref_commune"
        if name is None and dept is None :
            sql_execute = text(f"{sql_select} ORDER BY label_crte LIMIT :limit").\
                bindparams(bindparam('limit', value=limit))
        else :
            where_clause = []
            params = (bindparam('limit', value=limit), )
            if name is not None :
                where_clause.append('label_crte ilike :name')
                params = params + ( bindparam('name', value=name), )
            if dept is not None:
                where_clause.append('code_departement =:dpt')
                params = params + (bindparam('dpt', value=dept),)

            sql_execute = text(f"{sql_select} WHERE {' AND '.join(where_clause)} ORDER BY label_crte LIMIT :limit").bindparams(*params)

        with db.engine.connect() as conn:
            result = conn.execute(sql_execute).all()

        return [{'nom': row[0], 'code':row[1]} for row in result], 200

