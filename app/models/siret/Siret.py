from sqlalchemy import Column, String

from app import db


class Siret(db.Model):
    __tablename__ = 'siret'
    id = db.Column(db.Integer, primary_key=True)
    siret: str = Column(String, unique=True, nullable=False)
    categorie_juridique: str = Column(String)
    code_commune: str = Column(String)
    denomination = Column(String)
    adresse = Column(String)
    longitude= Column(db.Float)
    latitude = Column(db.Float)