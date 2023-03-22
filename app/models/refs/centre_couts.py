from sqlalchemy import Column, String, Text

from app import db, ma

class CentreCouts(db.Model):
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
        exclude = ('id',)
