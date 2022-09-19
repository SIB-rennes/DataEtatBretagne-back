from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from app import db

class Chorus(db.Model):
    __tablename__ = 'data_chorus'
    # PK
    n_ej = Column(String, primary_key=True)
    n_poste_ej = Column(Integer, primary_key=True)
    # liens vers les référentiels
    programme = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    localisation_interministerielle = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    groupe_marchandise = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    compte_general = Column(String, db.ForeignKey('ref_compte_general.code'), nullable=False)
    fournisseur_titulaire = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)
    siret = Column(String, db.ForeignKey('siret.siret'), nullable=False)

    # autre colonnes
    date_modification_ej = Column(DateTime, nullable=False)
    compte_budgetaire = Column(String(255), nullable= False)
    contrat_etat_region = Column(String(255))
    montant = Column(Float)






