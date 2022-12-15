from sqlalchemy import Column, String, Text

from app import db

class CategorieJuridique(db.Model):
    __tablename__ = 'ref_categorie_juridique'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    type: str = Column(String)
    label: str = Column(String)