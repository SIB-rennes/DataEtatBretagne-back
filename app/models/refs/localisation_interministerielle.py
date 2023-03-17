from sqlalchemy import Column, String, Text

from app import db

class LocalisationInterministerielle(db.Model):
    __tablename__ = 'ref_localisation_interministerielle'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    code_departement: str = Column(String)
    commune: str = Column(String)
    site: str = Column(String)
    description: str = Column(Text)