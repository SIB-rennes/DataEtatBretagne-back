from marshmallow import fields
from sqlalchemy import Column, String, Text



from app import db, ma
from app.models.common.Audit import Audit


class LocalisationInterministerielle(Audit,db.Model):
    __tablename__ = 'ref_localisation_interministerielle'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    code_departement: str = Column(String)
    commune: str = Column(String)
    site: str = Column(String)
    description: str = Column(Text)
    niveau: str = Column(String)
    code_parent = Column(String)

class LocalisationInterministerielleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LocalisationInterministerielle
        exclude = ('id',) + LocalisationInterministerielle.exclude_schema()

    label = fields.String()
    code_departement = fields.String()
    commune = fields.String()
    site = fields.String()
    description = fields.String()
    niveau =  fields.String()
    code_parent = fields.String()