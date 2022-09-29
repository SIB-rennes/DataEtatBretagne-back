from sqlalchemy import Column, String, Text

from app import db


class CodeProgramme(db.Model):
    __tablename__ = 'ref_code_programme'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    # FK
    theme = Column(db.Integer, db.ForeignKey('ref_theme.id'), nullable=True)

    label: str = Column(String)
    description: str = Column(Text)