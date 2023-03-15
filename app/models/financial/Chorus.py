import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from app import db
from app.models.common.Audit import Audit

@dataclass
class Chorus(Audit, db.Model):
    __tablename__ = 'data_chorus'
    # PK
    n_ej: str = Column(String, primary_key=True)
    n_poste_ej: str = Column(Integer, primary_key=True)
    # liens vers les référentiels
    source_region: str = Column(String, ForeignKey('ref_region.code'), nullable=True)
    programme: str  = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel:str = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts: str = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation: str = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    localisation_interministerielle: str = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    groupe_marchandise: str = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    compte_general: str = Column(String, db.ForeignKey('ref_compte_general.code'), nullable=False)
    fournisseur_titulaire: str = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=False)

    # autre colonnes
    date_modification_ej: datetime = Column(DateTime, nullable=False) #date issue du fichier Chorus
    compte_budgetaire: str = Column(String(255), nullable= False)
    contrat_etat_region: str = Column(String(255))
    montant: float = Column(Float)
    annee: int = Column(Integer, nullable= False) # annee de l'AE chorus





