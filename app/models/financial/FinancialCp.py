from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from app import db
from app.models.common.Audit import Audit

@dataclass
class FinancialAe(Audit, db.Model):
    __tablename__ = 'financial_cp'
    # PK
    n_dp: str = Column(String, primary_key=True)
    # liens vers les AE
    n_ej: str = Column(String, ForeignKey('financial_ae.n_ej'), nullable=True)
    n_poste_ej: int = Column(Integer, ForeignKey('financial_ae.n_poste_ej') , nullable=True)

    #FK
    source_region: str = Column(String, ForeignKey('ref_region.code'), nullable=False)
    programme: str = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel:str = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts: str = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation: str = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=False)
    groupe_marchandise: str = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    localisation_interministerielle: str = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    fournisseur_paye: str = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)


    # Autre colonne
    date_base_dp: datetime = Column(DateTime, nullable=False)
    date_derniere_operation_dp: datetime = Column(DateTime, nullable=False)

    compte_budgetaire: str = Column(String(255), nullable= True)
    contrat_etat_region: str = Column(String(255), nullable= True)
    montant: float = Column(Float)
    annee: int = Column(Integer, nullable= False)

