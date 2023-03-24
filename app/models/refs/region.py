from sqlalchemy import Column, String

from app import db
from app.models.common.Audit import Audit


class Region(Audit, db.Model):
    __tablename__ = 'ref_region'
    id = Column(db.Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    label = Column(String)
