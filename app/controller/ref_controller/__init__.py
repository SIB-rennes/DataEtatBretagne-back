from flask import Blueprint
from flask_restx import Api, Namespace

from app.controller.ref_controller.RefController import build_ref_controller
from app.controller.ref_controller.RefCrte import api as crte_api
from app.controller.ref_controller.RefLocalisationInterministerielle import api as api_loc_interministerielle
# models
from app.models.refs.centre_couts import CentreCouts
from app.models.refs.code_programme import CodeProgramme
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.groupe_marchandise import GroupeMarchandise
from app.models.refs.ministere import Ministere
from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.controller.ref_controller.LoginController import api as api_auth

api_ref = Blueprint('api_ref', __name__)

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(api_ref, doc='/doc', prefix="/api/v1", description="API de récupérations des référentiels",
          title="Référentiel",
          authorizations=authorizations)

api_domaine = build_ref_controller(DomaineFonctionnel,
                                   Namespace(name="Domaine Fonctionnel", path='/domaine-fonct',
                                             description='API referentiels des Domaine'),
                                   )

api_centre_cout = build_ref_controller(CentreCouts,
                                       Namespace(name="Centre couts", path='/centre-couts',
                                                 description='API referentiels des Centre de couts'),
                                       cond_opt=(CentreCouts.code_postal,)
                                       )

api_groupe_marchandise = build_ref_controller(GroupeMarchandise,
                                  Namespace(name="Groupe Marchandise", path='/groupe-marchandise',
                                            description='API referentiels des groupes de marchandises'),
                                  cond_opt=(GroupeMarchandise.domaine, GroupeMarchandise.segment,)
                                  )

api_bop = build_ref_controller(CodeProgramme,
                               Namespace(name="Code Programme", path='/programme',
                                         description='API referentiels des codes programmes')
                               )

api_ref_programmation = build_ref_controller(ReferentielProgrammation,
                               Namespace(name="Referentiel Programmation", path='/ref-programmation',
                                         description='API referentiels des referentiel de programmation')
                               )

api_ref_ministere = build_ref_controller(Ministere,
                               Namespace(name="Ministere", path='/ministere',
                                         description='API referentiels des ministères')
                               )


api.add_namespace(api_auth)

api.add_namespace(api_ref_ministere)
api.add_namespace(api_bop)
api.add_namespace(api_loc_interministerielle)
api.add_namespace(api_ref_programmation)
api.add_namespace(api_domaine)
api.add_namespace(api_centre_cout)
api.add_namespace(api_groupe_marchandise)
api.add_namespace(crte_api)