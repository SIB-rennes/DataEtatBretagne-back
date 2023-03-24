from sqlalchemy import Column, String, Text
from marshmallow import fields

from app import db, ma

class ReferentielProgrammation(db.Model):
    __tablename__ = 'ref_programmation'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)


class ReferentielProgrammationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReferentielProgrammation
        exclude = ('id',)

    label = fields.String()
    description = fields.String()