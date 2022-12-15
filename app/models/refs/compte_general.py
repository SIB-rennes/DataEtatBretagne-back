from sqlalchemy import Column, String, Text

from app import db

class CompteGeneral(db.Model):
    __tablename__ = 'ref_compte_general'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)