from sqlalchemy import Column, String, Text

from app import db


class CentreCouts(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ref_centre_couts'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)
    code_postal: str = Column(String)
    ville: str = Column(String)