from flask_restx import Namespace, Resource

api = Namespace(name="nocodb", path='/nocodb',
                description='API passe plat noco db')


@api.route('/test')
class NocoDb(Resource):
    @api.response(200, 'Success')
    def get(self):
        return "", 200