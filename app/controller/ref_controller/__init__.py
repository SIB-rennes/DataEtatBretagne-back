from flask import Blueprint
from flask_restx import Api,Namespace

from app.controller.ref_controller.RefController import build_ref_controller
from app.controller.ref_controller.RefCrte import api as crte_api
from app.controller.ref_controller.RefLocalisationInterministerielle import api as loc_api
from app.models.refs.centre_couts import CentreCouts
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.groupe_marchandise import GroupeMarchandise

api_ref = Blueprint('api_ref', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ref, doc='/doc', prefix="/api/v1", description="API de récupérations des référentiels", title="Référentiel",
          authorizations=authorizations)
api.add_namespace(crte_api)



api_domaine = build_ref_controller(DomaineFonctionnel,
                                  Namespace(name="Domaine Fonctionnel Controler", path='/domaine-fonct',
                                            description='API referentiels des Domaine fonctionnels'),
                                  )

api_centre_cout = build_ref_controller(CentreCouts,
                                  Namespace(name="Centre couts Controler", path='/centre-couts',
                                            description='API referentiels des Centre de couts'),
                                    cond_opt=(CentreCouts.code_postal,)
                                  )

api_groupe = build_ref_controller(GroupeMarchandise,
                                  Namespace(name="Groupe Marchandise Controler", path='/groupe-marchandise',
                                            description='API referentiels des groupes de marchandises'),
                                    cond_opt=(GroupeMarchandise.domaine,GroupeMarchandise.segment,)
                                  )

api_bop = build_ref_controller(CodeProgramme,
                                  Namespace(name="Code Programme Controler", path='/programme',
                                            description='API referentiels des codes programmes')
                                  )

api.add_namespace(api_domaine)
api.add_namespace(api_centre_cout)
api.add_namespace(api_groupe)
api.add_namespace(api_bop)


api.add_namespace(loc_api)
