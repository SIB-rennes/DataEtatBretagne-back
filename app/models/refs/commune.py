from sqlalchemy import Column, String

from app import db

class Commune(db.Model):
    __tablename__ = 'ref_commune'
    id = db.Column(db.Integer, primary_key=True)
    code_commune: str = Column(String, unique=True, nullable=False)
    label_commune: str = Column(String)
    code_crte: str = Column(String,nullable=True)
    label_crte: str = Column(String)

    code_region: str = Column(String)
    label_region: str = Column(String)

    code_epci: str = Column(String)
    label_epci: str = Column(String)

    code_departement: str= Column(String)
    label_departement: str = Column(String)


