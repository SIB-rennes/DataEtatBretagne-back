from sqlalchemy import Column, String, Text

from app import db
from app.models.common.Audit import Audit


class Theme(Audit, db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ref_theme'
    id = db.Column(db.Integer, primary_key=True)
    label: str = Column(String)
    description: str = Column(Text)