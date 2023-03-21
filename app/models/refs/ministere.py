from sqlalchemy import Column, String, Text

from app import db


class Ministere(db.Model):
    __tablename__ = 'ref_ministere'
    code: str = Column(String, primary_key=True)
    sigle_ministere: str = Column(String, nullable=True)
    label: str = Column(String, nullable=False)
    description: str = Column(Text)