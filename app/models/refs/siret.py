from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app import db
from app.models.common.Audit import Audit

JSONVariant = JSON().with_variant(JSONB(), "postgresql")

class Siret(Audit, db.Model):
    __tablename__ = 'ref_siret'
    id = db.Column(db.Integer, primary_key=True)
    # code siret
    code: str = Column(String, unique=True, nullable=False)

    #FK
    code_commune = Column(String, db.ForeignKey('ref_commune.code'), nullable=False)
    categorie_juridique = Column(String, db.ForeignKey('ref_categorie_juridique.code'), nullable=True)

    denomination = Column(String)
    adresse = Column(String)
    # Ajout de la partie Naf
    naf = Column(JSONVariant, nullable=True)

    ref_commune =  relationship("Commune", lazy="select")
    ref_categorie_juridique =  relationship("CategorieJuridique", lazy="select", uselist=False)
    type_categorie_juridique = association_proxy('ref_categorie_juridique', 'type')