from sqlalchemy import Column, String

from app import db

class Region(db.Model):
    __tablename__ = 'ref_region'
    id = Column(db.Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    label = Column(String)
