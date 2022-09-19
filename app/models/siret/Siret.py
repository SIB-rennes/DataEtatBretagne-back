from sqlalchemy import Column, String

from app import db


class Siret(db.Model):
    __tablename__ = 'siret'
    siret = db.Column(db.Integer, primary_key=True)
    type_etablissement: str = Column(String)
    code_commune: str = Column(String)
    departement = Column(String)
    denomination = Column(String)
    adresse = Column(String)