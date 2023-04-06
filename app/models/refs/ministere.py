from sqlalchemy import Column, String, Text

from app import db, ma
from app.models.common.Audit import Audit


class Ministere(Audit, db.Model):
    __tablename__ = 'ref_ministere'
    code: str = Column(String, primary_key=True)
    sigle_ministere: str = Column(String, nullable=True)
    label: str = Column(String, nullable=False)
    description: str = Column(Text)

class MinistereSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ministere
        exclude = Ministere.exclude_schema()
