from sqlalchemy import Column, String, Text

from app import db


class CodeProgramme(db.Model):
    __tablename__ = 'ref_code_programme'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    # FK
    code_ministere = Column(String, db.ForeignKey('ref_ministere.code'), nullable=True)

    label: str = Column(String)
    description: str = Column(Text)