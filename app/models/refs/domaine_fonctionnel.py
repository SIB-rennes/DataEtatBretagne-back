import dataclasses
import re

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import fields


from app import db, ma

@dataclasses.dataclass
class DomaineFonctionnel(db.Model):
    __tablename__ = 'ref_domaine_fonctionnel'
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
            matches = re.search(r"^(\d{4})(-)?", self.code)
            if (matches is not None) :
                return matches.group(1)[1:]
        return None


class DomaineFonctionnelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DomaineFonctionnel
        exclude = ('id',)

    code_programme = fields.String()
    label = fields.String()
    description = fields.String()