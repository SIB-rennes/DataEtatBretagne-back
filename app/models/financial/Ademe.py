from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Float, Boolean

from app import db, ma
from app.models.financial import FinancialData


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
    siret_beneficiaire: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)

    location_lat = Column(Float)
    location_lon = Column(Float)
    departement = Column(String(5))

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


class AdemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ademe
        exclude = ('id',)




