import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app import db
from app.models.enums.DataType import DataType


class AuditUpdateData(db.Model):
    """
    Table d'audit pour stocker les dernière mise à jours de JDD
    """
    __tablename__ = 'audit_update_data'
    __table_args__ = {'schema': 'audit'}
    __bind_key__ = "audit"
    # PK
    id = Column(Integer, primary_key=True, nullable = False)

    username = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    data_type = Column(db.Enum(DataType), nullable=False)

    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)