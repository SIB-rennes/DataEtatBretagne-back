from sqlalchemy import Column, String, Text

from app import db

class CommuneCrte(db.Model):
    __tablename__ = 'ref_commune_crte'
    id = db.Column(db.Integer, primary_key=True)
    code_commune: str = Column(String, unique=True, nullable=False)
    code_crte: str = Column(String,nullable=True)
    label_crte: str = Column(String)

