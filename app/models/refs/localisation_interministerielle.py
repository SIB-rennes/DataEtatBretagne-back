from marshmallow import fields
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app import db, ma
from app.models.common.Audit import Audit
from app.models.refs.commune import CommuneSchema


class LocalisationInterministerielle(Audit,db.Model):
    __tablename__ = 'ref_localisation_interministerielle'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    site: str = Column(String)
    description: str = Column(Text)
    niveau: str = Column(String)
    code_parent = Column(String)


    # FK
    commune_id = Column(db.Integer, db.ForeignKey('ref_commune.id'), nullable=True)
    commune = relationship("Commune", lazy="select")

class LocalisationInterministerielleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LocalisationInterministerielle
        exclude = ('id','commune_id',) + LocalisationInterministerielle.exclude_schema()

    label = fields.String()
    site = fields.String()
    description = fields.String()
    niveau =  fields.String()
    code_parent = fields.String()
    commune = fields.Nested(CommuneSchema)