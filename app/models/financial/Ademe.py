from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Date, Float

from app import db, ma
from app.models.financial import FinancialData


@dataclass
class Ademe(FinancialData, db.Model):
    __tablename__ = 'ademe'
    #PK
    id = Column(Integer, primary_key=True)
    date_convention = Column(Date)
    # UNIQUE
    reference_decision = Column(String(255), unique=True, nullable=False)

    objet = Column(String(255))
    montant = Column(Float)
    nature = Column(String(255))
    conditions_versement = Column(String(255))
    dates_periode_versement = Column(String(255))
    notification_ue = Column(String(255))
    pourcentage_subvention = Column(Float)

    #FK
    attribuant = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)

    location_lat = Column(Float)
    location_lon = Column(Float)
    departement = Column(String(5))


class AdemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ademe
        exclude = ('id',)




