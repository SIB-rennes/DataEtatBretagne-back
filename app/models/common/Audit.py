import datetime
from sqlalchemy import DateTime, Column
from sqlalchemy.orm import deferred, declared_attr


class Audit(object):
    """
    Class for managing the audit of SQLAlchemy objects.
        Attributes:
            - created_at : Column(DateTime) : The date and time the object was created.
            - updated_at : Column(DateTime) : The date and time the object was last updated.
    """
    @declared_attr
    def created_at(cls):
        return deferred(Column(DateTime, default=datetime.datetime.utcnow))

    @declared_attr
    def updated_at(cls):
        return deferred(Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow))

    @staticmethod
    def exclude_schema():
        return ('created_at','updated_at')