import datetime
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float
from app import db
from app.models.common.Audit import Audit

@dataclass
class Chorus(Audit, db.Model):
    __tablename__ = 'data_chorus'
    # PK
    n_ej: str = Column(String, primary_key=True)
    n_poste_ej: int = Column(Integer, primary_key=True)
    # liens vers les référentiels
    source_region: str = Column(String, ForeignKey('ref_region.code'), nullable=True)
    programme: str  = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel:str = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts: str = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation: str = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    localisation_interministerielle: str = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    groupe_marchandise: str = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    fournisseur_titulaire: str = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=False)

    # autre colonnes
    date_modification_ej: datetime = Column(DateTime, nullable=False) #date issue du fichier Chorus
    compte_budgetaire: str = Column(String(255), nullable= False)
    contrat_etat_region: str = Column(String(255))
    montant: float = Column(Float)
    annee: int = Column(Integer, nullable= False) # annee de l'AE chorus



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


    def __post_init__(self):
       self.montant = float(str(self.montant).replace('\U00002013', '-').replace(',', '.'))

       if isinstance(self.date_modification_ej, str):
            self.date_modification_ej = datetime.strptime(self.date_modification_ej, '%d.%m.%Y')
       if self.centre_couts.startswith('BG00/') :
            self.centre_couts =  self.centre_couts[5:]

       if self.referentiel_programmation.startswith('BG00/') :
            self.referentiel_programmation = self.referentiel_programmation[5:]

       #Cas si le siret a moins de caractères
       self.siret = self._fix_siret(self.siret)


    def update_attribute(self,  line_chorus: dict):
        """
        update instance chorus avec les infos d'une ligne issue d'un fichier chorus
        :param line_chorus:
        :return:
        """

        for key, value in line_chorus.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __setattr__(self, key, value):
        if (key == "centre_couts" or key == "referentiel_programmation") and isinstance(value, str) and value.startswith("BG00/"):
            value = value[5:]

        if key == "date_modification_ej" and isinstance(value, str) :
            value = datetime.strptime(value, '%d.%m.%Y')
        if key == "montant":
            value = float(str(value).replace('\U00002013', '-').replace(',', '.'))

        if key == 'siret':
            value = self._fix_siret(value)

        super().__setattr__(key, value)


    @staticmethod
    def _fix_siret(value: str) -> str:
        if len(value) < 14 :
            nb_zeros_a_ajouter = 14 - len(value)
            value = '0' * nb_zeros_a_ajouter + str(value)

        return value


    @staticmethod
    def get_columns_files_ae():
        return ['programme', 'domaine_fonctionnel', 'centre_couts',
                              'referentiel_programmation', 'n_ej', 'n_poste_ej', 'date_modification_ej',
                              'fournisseur_titulaire', 'fournisseur_label', 'siret', 'compte_code',
                              'compte_budgetaire', 'groupe_marchandise', 'contrat_etat_region',
                              'contrat_etat_region_2','localisation_interministerielle', 'montant']
