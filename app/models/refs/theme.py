from sqlalchemy import Column, String, Text

from app import db


class Theme(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ref_theme'
    id = db.Column(db.Integer, primary_key=True)
    label: str = Column(String)
    description: str = Column(Text)