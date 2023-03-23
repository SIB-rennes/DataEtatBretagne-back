from marshmallow import fields
from sqlalchemy import Column, String, Text

from app import db,ma

class GroupeMarchandise(db.Model):
    __tablename__ = 'ref_groupe_marchandise'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)

    domaine: str = Column(String)
    segment: str = Column(String)

    # mutualisation avec compte_general
    code_pce: str =  Column(String)
    label_pce: str = Column(String)

class GroupeMarchandiseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GroupeMarchandise
        exclude = ('id',)

    label = fields.String()
    code = fields.String()
    description = fields.String()
    domaine =  fields.String()
    segment = fields.String()
    code_pce = fields.String()
    label_pce = fields.String()