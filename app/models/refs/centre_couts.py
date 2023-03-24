from sqlalchemy import String, Text

from app import db, ma
from sqlalchemy import Column

from app.models.common.Audit import Audit

class CentreCouts(Audit, db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ref_centre_couts'
    id: int = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)
    code_postal: str = Column(String)
    ville: str = Column(String)

class CentreCoutsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CentreCouts
        exclude = ('id',) + CentreCouts.exclude_schema()
