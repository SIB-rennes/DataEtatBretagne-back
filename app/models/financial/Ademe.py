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

    location_lat = Column(Float)
    location_lon = Column(Float)
    departement = Column(String(5))

    # Données techniques 

    file_import_taskid = Column(String(255))
    """Task ID de la tâche d'import racine pour cette ligne"""
    file_import_lineno = Column(Integer())
    """Numéro de ligne correspondant dans le fichier original"""

    __table_args__ = UniqueConstraint('file_import_taskid', 'file_import_lineno', name="uq_file_line_import_ademe"),

    def __init__(self, line_csv: dict):
        """
        init à partir d'une ligne issue d'un fichier csv

        :param line_chorus: dict contenant les valeurs d'une ligne issue d'un fichier chorus
        :param source_region:
        :param annee:
        """

        self.update_attribute(line_csv)


    def __setattr__(self, key, value):
        if (key == 'notification_ue') :
            value = True if value is not None else False

        if key == "date_convention" and isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()

        super().__setattr__(key, value)

    @staticmethod
    def get_columns_files():
        return [
            'Nom de l attribuant', 'siret_attribuant', 'date_convention', 'reference_decision', 'nomBeneficiaire', 'siret_beneficiaire',
            'objet','montant', 'nature', 'conditions_versement', 'dates_periode_versement', 'notification_ue', 'pourcentage_subvention',
            'location_lat', 'location_lon', 'departement', 'naf1etlib', 'naf2etlib', 'naf3etlib', 'naf4etlib', 'naf5etlib'
        ]




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
        exclude = ('updated_at','created_at','location_lat','location_lon', 'ref_siret_attribuant')

    siret_beneficiaire = SiretField(attribute="siret_beneficiaire")
    commune = CommuneField(attribute="ref_siret_beneficiaire")


