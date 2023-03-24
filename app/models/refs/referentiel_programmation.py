import re

from sqlalchemy import Column, String, Text
from marshmallow import fields
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, ma

class ReferentielProgrammation(db.Model):
    __tablename__ = 'ref_programmation'
    id = db.Column(db.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    label: str = Column(String)
    description: str = Column(Text)

    @hybrid_property
    def code_programme(self) -> str | None:
        """
        Retourne le code programme associé
        :return:
        """
        if (self.code and type(self.code) == str) :
            matches = re.search(r"^(\d{4})(.*)", self.code)
            if (matches is not None) :
                return matches.group(1)[1:]
        return None


class ReferentielProgrammationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReferentielProgrammation
        exclude = ('id',)

    label = fields.String()
    description = fields.String()
    code_programme = fields.String()