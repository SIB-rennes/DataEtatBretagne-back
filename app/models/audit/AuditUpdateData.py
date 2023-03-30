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
    id: int = Column(Integer, primary_key=True, nullable = False)

    username: str = Column(String, nullable=False)
    filename: str = Column(String, nullable=False)
    data_type:DataType  = Column(db.Enum(DataType), nullable=False)

    date: DateTime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
