from dataclasses import dataclass
from datetime import datetime

from marshmallow import fields
from sqlalchemy import Column, Integer, String, Date, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app import db, ma
from app.models.financial import FinancialData, json_type_object_code_label
from app.models.refs.siret import Siret

__all__ = ('Ademe','AdemeSchema')


@dataclass
class Ademe(FinancialData, db.Model):
    __tablename__ = 'ademe'
    #PK
    id = Column(Integer, primary_key=True)
    date_convention = Column(Date)

    reference_decision = Column(String(255),nullable=False)

    objet = Column(String(255))
    montant = Column(Float)
    nature = Column(String(255))
    conditions_versement = Column(String(255))
    dates_periode_versement = Column(String(255))
    notification_ue = Column(Boolean, default=False)
    pourcentage_subvention = Column(Float)

    #FK
    siret_attribuant = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)
    siret_beneficiaire = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)

    ref_siret_attribuant = relationship("Siret", lazy="select", foreign_keys=[siret_attribuant])
    ref_siret_beneficiaire = relationship("Siret", lazy="select", foreign_keys=[siret_beneficiaire])

    # Données techniques 
    file_import_taskid = Column(String(255))
    """Task ID de la tâche d'import racine pour cette ligne"""
    file_import_lineno = Column(Integer())
    """Numéro de ligne correspondant dans le fichier original"""

    __table_args__ = UniqueConstraint('file_import_taskid', 'file_import_lineno', name="uq_file_line_import_ademe"),

    @staticmethod
    def from_datagouv_csv_line(line_dict: dict):
        ademe = Ademe()

        date_convention = line_dict['dateConvention']
        date_convention = datetime.strptime(date_convention, '%Y-%m-%d').date()

        notification_ue = line_dict['notificationUE']
        notification_ue = True if notification_ue is not None else False

        ademe.date_convention = date_convention
        ademe.reference_decision = line_dict['referenceDecision']
        ademe.objet = line_dict['objet']
        ademe.montant = line_dict['montant']
        ademe.nature = line_dict['nature']
        ademe.conditions_versement = line_dict['conditionsVersement']
        ademe.dates_periode_versement = line_dict['datesPeriodeVersement']
        ademe.notification_ue = notification_ue
        ademe.pourcentage_subvention = line_dict['pourcentageSubvention']

        ademe.siret_attribuant = line_dict['idAttribuant']
        ademe.siret_beneficiaire = line_dict['idBeneficiaire']

        return ademe


class SiretField(fields.Field):
    """Field Siret
    """
    def _jsonschema_type_mapping(self):
        return {
            'type': 'object',
            'properties': {
                'nom': {'type': 'string'},
                'code': {'type': 'string'},
                'categorie_juridique': {'type': 'string'}
            }
        }

    def _serialize(self, siret: str, attr: str, obj: Ademe, **kwargs):
        if siret is None:
            return {}
        return {
            'nom_beneficiare': obj.ref_siret_beneficiaire.denomination,
            'code': siret,
            'categorie_juridique': obj.ref_siret_beneficiaire.type_categorie_juridique
        }

class CommuneField(fields.Field):
    """Field Commune
    """
    def _jsonschema_type_mapping(self):
        return json_type_object_code_label()

    def _serialize(self, value:Siret, attr, obj: Ademe, **kwargs):
        if value is None:
            return {}
        return {
            'label': value.ref_commune.label_commune,
            'code': value.ref_commune.code
        }

class AdemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ademe
        exclude = ('updated_at', 'created_at', 'ref_siret_attribuant')

    siret_beneficiaire = SiretField(attribute="siret_beneficiaire")
    commune = CommuneField(attribute="ref_siret_beneficiaire")


