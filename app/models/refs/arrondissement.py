from sqlalchemy import Column, String

from app import db, ma
from app.models.common.Audit import Audit


class Arrondissement(Audit, db.Model):
    __tablename__ = 'ref_arrondissement'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)

    code_region: str = Column(String)
    code_departement: str= Column(String)

    label: str= Column(String)


class ArrondissementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Arrondissement
        exclude = Arrondissement.exclude_schema()

