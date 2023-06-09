import datetime
import logging
from datetime import datetime
from dataclasses import dataclass

from marshmallow import fields
from marshmallow_sqlalchemy import auto_field
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app import db, ma
from app.models.financial import FinancialData, json_type_object_code_label
from app.models.financial.MontantFinancialAe import MontantFinancialAe
from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.models.refs.siret import Siret

COLUMN_MONTANT_NAME= 'montant'

__all__ = ('FinancialAe','FinancialAeSchema')

@dataclass
class FinancialAe(FinancialData, db.Model):
    __tablename__ = 'financial_ae'
    # PK
    id: int = Column(Integer, primary_key=True)

    # UNIQUE
    n_ej: str = Column(String, nullable=False)
    n_poste_ej: int = Column(Integer, nullable=False)
    UniqueConstraint("n_ej", "n_poste_ej", name="n_ej_n_poste_ej"),

    # liens vers les référentiels
    source_region: str = Column(String, ForeignKey('ref_region.code'), nullable=True)
    programme: str  = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel:str = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts: str = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation: str = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    localisation_interministerielle: str = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    groupe_marchandise: str = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    fournisseur_titulaire: str = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)

    # autre colonnes
    date_modification_ej: datetime = Column(DateTime, nullable=False) #date issue du fichier Chorus
    compte_budgetaire: str = Column(String(255), nullable= False)
    contrat_etat_region: str = Column(String(255))
    annee: int = Column(Integer, nullable= False) # annee de l'AE chorus

    montant_ae = relationship("MontantFinancialAe", uselist=True, lazy="select")
    financial_cp = relationship("FinancialCp", uselist=True, lazy="select")
    ref_programme = relationship("CodeProgramme", lazy="select")
    ref_domaine_fonctionnel = relationship("DomaineFonctionnel", lazy="select")
    ref_ref_programmation = relationship("ReferentielProgrammation", lazy="select")
    ref_siret = relationship("Siret", lazy="select")
    ref_localisation_interministerielle = relationship("LocalisationInterministerielle", lazy="select")

    @hybrid_property
    def montant_ae_total(self):
        return sum(montant_financial_ae.montant for montant_financial_ae in self.montant_ae)

    @hybrid_property
    def montant_cp(self):
        return sum(financial_cp.montant for financial_cp in self.financial_cp)

    @hybrid_property
    def date_cp(self):
        if self.financial_cp:
            return max(self.financial_cp, key=lambda obj: obj.date_derniere_operation_dp).date_derniere_operation_dp
        return None

    def __init__(self, **kwargs):
        """
        init à partir d'une ligne issue d'un fichier chorus
        """
        self.update_attribute(kwargs)

    def __setattr__(self, key, value):
        if key == "date_modification_ej" and isinstance(value, str):
            value = datetime.strptime(value, '%d.%m.%Y')

        super().__setattr__(key, value)

    def update_attribute(self, new_financial: dict):
        # Applicatin montant négatif
        if (self._should_update_montant_ae(new_financial)):
            nouveau_montant = float(new_financial[COLUMN_MONTANT_NAME].replace(",",".")) if isinstance(new_financial[COLUMN_MONTANT_NAME], str) else new_financial[COLUMN_MONTANT_NAME]
            self.add_or_update_montant_ae(nouveau_montant, new_financial[FinancialAe.annee.key])
            if (nouveau_montant < 0 and self.annee):
                del new_financial[FinancialAe.annee.key] # on ne maj pas l'année comptable si montant <0

        super().update_attribute(new_financial)


    def should_update(self, new_financial: dict)-> bool:
        '''
        Indique si MAJ ou non l'objet
        :param new_financial:
        :return:
        '''

        if (self._should_update_montant_ae(new_financial)):
            logging.debug(f"[FINANCIAL AE] Montant negatif détecté, application sur ancien montant {self.n_poste_ej}, {self.n_ej}")
            return True
        else :
            return datetime.strptime(new_financial['date_modification_ej'], '%d.%m.%Y') > self.date_modification_ej

    def add_or_update_montant_ae(self, nouveau_montant: float, annee):
        '''
        Ajoute un montant à une ligne AE
        :param nouveau_montant: le nouveau montant à ajouter
        :param annee: l'année comptable
        :return:
        '''
        if (self.montant_ae is None or not self.montant_ae): # si aucun montant AE encore, on ajoute
            self.montant_ae = [MontantFinancialAe(montant=nouveau_montant, annee=annee)]
        else:
            montant_ae_annee = next((montant_ae for montant_ae in self.montant_ae if montant_ae.annee == annee), None) # recherche d'un montant sur la même année existant

            if (nouveau_montant > 0) : # Si nouveau montant positif
                montant_ae_positif = next((montant_ae for montant_ae in self.montant_ae if montant_ae.montant > 0), None)

                if (montant_ae_positif is None):
                    if (montant_ae_annee is None): # si aucun montant positif enregistré et sur, alors on ajoute
                        self.montant_ae.append(MontantFinancialAe(montant=nouveau_montant, annee=annee))
                    else :
                        montant_ae_annee.montant = nouveau_montant
                        montant_ae_annee.annee = annee
                else :
                    # sinon je prend le montant positif le plus récent
                    montant_ae_positif.montant = nouveau_montant if (montant_ae_positif.annee <= annee) else montant_ae_positif.montant
                    montant_ae_positif.annee = annee if (montant_ae_positif.annee <= annee) else montant_ae_positif.annee

            else: # nouveau_montant < 0
                if (montant_ae_annee is None) : # si l'année n'est pas déjà enregistré, alors on ajoute le montant
                    self.montant_ae.append(MontantFinancialAe(montant=nouveau_montant, annee=annee))
                else : # sinon on MAJ
                    montant_ae_annee.montant = nouveau_montant


    def _should_update_montant_ae(self, new_financial: dict)-> bool:
        '''
        ajoute ou maj un montant dans montant_ae
        :param new_financial:
        :return:
        '''
        if(self.source_region is not None and new_financial[FinancialAe.source_region.key] != self.source_region):
            return False

        nouveau_montant = float(new_financial[COLUMN_MONTANT_NAME].replace(",",".")) if isinstance(new_financial[COLUMN_MONTANT_NAME], str) else new_financial[COLUMN_MONTANT_NAME]

        annee = new_financial[FinancialAe.annee.key]

        if any(montant_ae.montant == nouveau_montant and montant_ae.annee == annee for montant_ae in self.montant_ae):
            return False

        return True

    @staticmethod
    def get_columns_files_ae():
        return ['programme', 'domaine_fonctionnel', 'centre_couts',
                              'referentiel_programmation', 'n_ej', 'n_poste_ej', 'date_modification_ej',
                              'fournisseur_titulaire', 'fournisseur_label', 'siret', 'compte_code',
                              'compte_budgetaire', 'groupe_marchandise', 'contrat_etat_region',
                              'contrat_etat_region_2','localisation_interministerielle', COLUMN_MONTANT_NAME]




class CommuneField(fields.Field):
    """Field Commune
    """
    def _jsonschema_type_mapping(self):
        return json_type_object_code_label()

    def _serialize(self, value: Siret, attr, obj, **kwargs):
        if value is None:
            return {}
        return {
            'label': value.ref_commune.label_commune,
            'code': value.ref_commune.code
        }


class ReferentielField(fields.Field):
    """Field Ref programmation
    """
    def _jsonschema_type_mapping(self):
        return json_type_object_code_label()

    def _serialize(self, code: String, attr, obj: FinancialAe, **kwargs):
        if code is None:
            return {}
        return {
            'label': obj.ref_ref_programmation.label,
            'code': code
        }

class DomaineField(fields.Field):
    """Field Domaine fonctionnel
    """
    def _jsonschema_type_mapping(self):
        return json_type_object_code_label()

    def _serialize(self, code: String, attr, obj: FinancialAe, **kwargs):
        if code is None:
            return {}
        return {
            'label': obj.ref_domaine_fonctionnel.label,
            'code': code
        }

class ProgrammeField(fields.Field):
    """Field programme
    """

    def _jsonschema_type_mapping(self):
        return {
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'code': {'type': 'string'},
                'theme': {'type': 'string'}
            }
        }

    def _serialize(self, code: String, attr, obj: FinancialAe, **kwargs):
        if code is None:
            return {}
        return {
            'label': obj.ref_programme.label,
            'code': code,
            'theme': obj.ref_programme.label_theme
        }

class SiretField(fields.Field):
    """Field Siret
    """
    def _jsonschema_type_mapping(self):
        return {
            'type': 'object',
            'properties': {
                'nom_beneficiare': {'type': 'string'},
                'code': {'type': 'string'},
                'categorie_juridique': {'type': 'string'}
            }
        }

    def _serialize(self, code: String, attr, obj: FinancialAe, **kwargs):
        if code is None:
            return {}
        return {
            'nom_beneficiare': obj.ref_siret.denomination,
            'code': code,
            'categorie_juridique': obj.ref_siret.type_categorie_juridique
        }

class FinancialAeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FinancialAe
        exclude = ('groupe_marchandise','updated_at','created_at','source_region','compte_budgetaire','contrat_etat_region','financial_cp')

    montant_ae = fields.Float(attribute='montant_ae_total')
    montant_cp = fields.Float()
    date_cp = fields.String()
    commune = CommuneField(attribute="ref_siret")
    domaine_fonctionnel = DomaineField(attribute="domaine_fonctionnel")
    referentiel_programmation = ReferentielField()
    programme =  ProgrammeField()
    n_ej = fields.String()
    n_poste_ej = fields.Integer()
    annee = fields.Integer()
    siret = SiretField()