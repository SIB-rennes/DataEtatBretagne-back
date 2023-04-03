import sqlalchemy
from flask import jsonify, current_app, request, g
from flask_restx import Namespace, Resource, reqparse, inputs, fields
from sqlalchemy.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from app import db
from app.controller.Decorators import check_permission
from app.exceptions.exceptions import BadRequestDataRegateNum
from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.ConnectionProfile import ConnectionProfile
from app.models.enums.DataType import DataType
from app.services.financial_data import import_ae

api = Namespace(name="chorus", path='/chorus',
                description='Api de délenchements des taks chorus')

parser = reqparse.RequestParser()
parser.add_argument('fichier', type=FileStorage, help="fichier à importer", location='files', required=True)
parser.add_argument('code_region', type=str, help="Code INSEE de la région émettrice du fichier chorus",location='files', required=True)
parser.add_argument('annee', type=int, help="Année d'engagement du fichier Chorus",location='files', required=True)
parser.add_argument('force_update', type=inputs.boolean, required=False, default=False,location='files', help="Force la mise à jours si la ligne existe déjà")

oidc = current_app.extensions['oidc']


@api.route('/import/ae')
class ChorusImport(Resource):

    @api.expect(parser)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission([ConnectionProfile.ADMIN, ConnectionProfile.COMPTABLE])
    @api.doc(security="Bearer")
    def post(self):
        data = request.form

        if 'fichier' not in  request.files :
            raise BadRequestDataRegateNum("Missing File")
        if 'code_region' not in data or 'annee' not in data:
            raise BadRequestDataRegateNum("Missing Argument code_region or annee")

        if not isinstance(int(data['annee']), int):
            raise BadRequestDataRegateNum("Missing Argument code_region or annee")
        file_chorus = request.files['fichier']
        force_update = False
        if 'force_update' in data and data['force_update'] == 'true':
            force_update = True

        username = g.oidc_token_info['username'] if hasattr(g,'oidc_token_info') and 'username' in g.oidc_token_info else ''
        task = import_ae(file_chorus,data['code_region'],int(data['annee']), force_update, username)
        return jsonify({"status": f'Fichier récupéré. Demande d`import de donnée chorus AE en cours (taches asynchrone id = {task.id}'})



@api.route('/last-import')
class LastImport(Resource):

    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @api.doc(security="Bearer")
    @api.marshal_with(api.model("date-last-import",{'date': fields.DateTime}), code=200)
    def get(self):

        stmt = db.select(sqlalchemy.sql.functions.max(AuditUpdateData.date)).where(
            AuditUpdateData.data_type == DataType.FINANCIAL_DATA.name)
        result = db.session.execute(stmt).scalar_one()
        if result is None:
            raise NoResultFound()

        return {"date": result.isoformat() }, 200



parser_line = reqparse.RequestParser()
parser_line.add_argument('json', type=str, help="ligne chorus à importer en json", required=True)
@api.route('/import/line')
class LineImport(Resource):

    @api.expect(parser_line)
    @oidc.accept_token(require_token=True, scopes_required=['openid'])
    @check_permission(ConnectionProfile.ADMIN)
    @api.doc(security="Bearer")
    def post(self):
        args = parser_line.parse_args()
        json_line = args['json']
        from app.tasks.import_chorus_tasks import import_line_chorus_ae
        task = import_line_chorus_ae.delay(str(json_line),-1)
        return jsonify({
            "statut": f'Ligne récupéré. Demande d`import d\'une ligne chorus AE en cours (taches asynchrone id = {task.id}'})
