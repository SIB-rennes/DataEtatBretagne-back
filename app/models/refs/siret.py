from sqlalchemy import Column, String

from app import db


class Siret(db.Model):
    __tablename__ = 'ref_siret'
    id = db.Column(db.Integer, primary_key=True)
    # code siret
    code: str = Column(String, unique=True, nullable=False)

    #FK
    code_commune = Column(String, db.ForeignKey('ref_commune_crte.code_commune'), nullable=False)
    categorie_juridique = Column(String, db.ForeignKey('ref_categorie_juridique.code'), nullable=True)

    denomination = Column(String)
    adresse = Column(String)
    longitude= Column(db.Float)
    latitude = Column(db.Float)