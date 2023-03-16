import datetime
from sqlalchemy import Column, DateTime


class Audit():
    """
    Class for managing the audit of SQLAlchemy objects.
        Attributes:
            - created_at : Column(DateTime) : The date and time the object was created.
            - updated_at : Column(DateTime) : The date and time the object was last updated.
    """
    #audit
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)