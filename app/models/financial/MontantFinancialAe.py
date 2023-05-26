from dataclasses import dataclass

from sqlalchemy import Column,Integer, Float
from app import db
from app.models.common.Audit import Audit

@dataclass
class MontantFinancialAe(Audit, db.Model):
    __tablename__ = 'montant_financial_ae'
    # PK
    id: int = Column(Integer, primary_key=True)

    # FK
    id_financial_ae: int = Column(Integer, db.ForeignKey('financial_ae.id'), nullable=False)
    montant: float = Column(Float)
    annee: int = Column(Integer, nullable= False)


    def __init__(self, montant:float , annee: int):
        self.montant = montant
        self.annee = annee