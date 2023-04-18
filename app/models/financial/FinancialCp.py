from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from app import db
from app.models.financial import FinancialData


@dataclass
class FinancialCp(FinancialData, db.Model):
    __tablename__ = 'financial_cp'
    # PK
    n_dp: str = Column(String, primary_key=True)

    # FK AE
    id_ae: str = Column(String, ForeignKey('financial_ae.id'), nullable=True)

    # liens vers les AE
    n_ej: str = Column(String, nullable=True)
    n_poste_ej: int = Column(Integer, nullable=True)

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


    def __init__(self, line_chorus: dict,source_region:str,annee: int):
        """
        init à partir d'une ligne issue d'un fichier chorus

        :param line_chorus: dict contenant les valeurs d'une ligne issue d'un fichier chorus
        :param source_region:
        :param annee:
        """

        self.source_region = source_region
        self.annee = annee

        self.update_attribute(line_chorus)

    def do_update(self, new_financial):
        return datetime.strptime(new_financial['date_derniere_operation_dp'], '%d.%m.%Y') > self.date_derniere_operation_dp

    def __setattr__(self, key, value):
        if (key == 'n_ej' or key == 'n_poste_ej') and value == '#' :
            value = None

        if (key == "date_base_dp" or key == "date_derniere_operation_dp") and isinstance(value, str) :
            value = datetime.strptime(value, '%d.%m.%Y')

        super().__setattr__(key, value)


    @staticmethod
    def get_columns_files_cp():
        return ['programme', 'domaine_fonctionnel', 'centre_couts',
                              'referentiel_programmation', 'n_ej', 'n_poste_ej', 'n_dp',
                             'date_base_dp','date_derniere_operation_dp','n_sf','data_sf',
                             'fournisseur_paye','fournisseur_paye_label',
                             'siret','compte_code','compte_budgetaire','groupe_marchandise','contrat_etat_region',
                              'contrat_etat_region_2','localisation_interministerielle', 'montant']