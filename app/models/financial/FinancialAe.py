import datetime
import logging
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app import db
from app.models.financial import FinancialData
from app.models.financial.MontantFinancialAe import MontantFinancialAe

COLUMN_MONTANT_NAME= 'montant'

@dataclass
class FinancialAe(FinancialData, db.Model):
    __tablename__ = 'financial_ae'
    # PK
    id: int = Column(Integer, primary_key=True)

    # UNIQUE
    n_ej: str = Column(String, nullable=False)
    n_poste_ej: int = Column(Integer, nullable=False)
    UniqueConstraint("n_ej", "n_poste_ej", name="n_ej_n_poste_ej"),

    # liens vers les référentiels
    source_region: str = Column(String, ForeignKey('ref_region.code'), nullable=True)
    programme: str  = Column(String, ForeignKey('ref_code_programme.code'), nullable=False)
    domaine_fonctionnel:str = Column(String, db.ForeignKey('ref_domaine_fonctionnel.code'), nullable=False)
    centre_couts: str = Column(String, db.ForeignKey('ref_centre_couts.code'), nullable=False)
    referentiel_programmation: str = Column(String, db.ForeignKey('ref_programmation.code'), nullable=False)
    localisation_interministerielle: str = Column(String, db.ForeignKey('ref_localisation_interministerielle.code'), nullable=False)
    groupe_marchandise: str = Column(String, db.ForeignKey('ref_groupe_marchandise.code'), nullable=False)
    fournisseur_titulaire: str = Column(String, db.ForeignKey('ref_fournisseur_titulaire.code'), nullable=False)
    siret: str = Column(String, db.ForeignKey('ref_siret.code'), nullable=True)

    # autre colonnes
    date_modification_ej: datetime = Column(DateTime, nullable=False) #date issue du fichier Chorus
    compte_budgetaire: str = Column(String(255), nullable= False)
    contrat_etat_region: str = Column(String(255))
    annee: int = Column(Integer, nullable= False) # annee de l'AE chorus

    montant_ae = relationship("MontantFinancialAe", uselist=True)


    def __init__(self, **kwargs):
        """
        init à partir d'une ligne issue d'un fichier chorus
        """
        self.update_attribute(kwargs)

    def __setattr__(self, key, value):
        if key == "date_modification_ej" and isinstance(value, str):
            value = datetime.strptime(value, '%d.%m.%Y')

        super().__setattr__(key, value)


    def __post_init__(self):
       #self.montant = float(str(self.montant).replace('\U00002013', '-').replace(',', '.'))

       if isinstance(self.date_modification_ej, str):
            self.date_modification_ej = datetime.strptime(self.date_modification_ej, '%d.%m.%Y')
       if self.centre_couts.startswith('BG00/') :
            self.centre_couts =  self.centre_couts[5:]

       if self.referentiel_programmation.startswith('BG00/') :
            self.referentiel_programmation = self.referentiel_programmation[5:]

       #Cas si le siret a moins de caractères
       self.siret = self._fix_siret(self.siret)

    def update_attribute(self, new_financial: dict):
        # Applicatin montant négatif
        if (self._update_montant_ae(new_financial)):
            self.add_or_update_montant_ae(new_financial[COLUMN_MONTANT_NAME], new_financial[FinancialAe.annee.key])

        super().update_attribute(new_financial)


    def should_update(self, new_financial: dict)-> bool:
        '''
        Indique si MAJ ou non l'objet
        :param new_financial:
        :return:
        '''

        if (self._update_montant_ae(new_financial)):
            logging.debug(f"[FINANCIAL AE] Montant negatif détecté, application sur ancien montant {self.n_poste_ej}, {self.n_ej}")
            return True
        else :
            return datetime.strptime(new_financial['date_modification_ej'], '%d.%m.%Y') > self.date_modification_ej


    def _update_montant_ae(self, new_financial: dict):
        '''
        ajoute ou maj un montant dans montant_ae
        :param new_financial:
        :return:
        '''
        if(new_financial[FinancialAe.source_region.key] != self.source_region):
            return False

        nouveau_montant = new_financial[COLUMN_MONTANT_NAME]
        annee = new_financial[FinancialAe.annee.key]

        if any(montant_ae.montant == nouveau_montant and montant_ae.annee == annee for montant_ae in self.montant_ae):
            return False

        return True


    def add_or_update_montant_ae(self, montant, annee):
        '''
        Ajoute un montant à une ligne AE
        :param montant:
        :param annee:
        :return:
        '''
        if (self.montant_ae is None):
            self.montant_ae = [MontantFinancialAe(montant=montant, annee=annee)]
        elif montant > 0:
            for montant_ae in self.montant_ae:
                if (montant_ae.annee == annee):
                    montant_ae.montant = montant
        else :
            self.montant_ae.append(MontantFinancialAe(montant=montant, annee=annee))

    @staticmethod
    def get_columns_files_ae():
        return ['programme', 'domaine_fonctionnel', 'centre_couts',
                              'referentiel_programmation', 'n_ej', 'n_poste_ej', 'date_modification_ej',
                              'fournisseur_titulaire', 'fournisseur_label', 'siret', 'compte_code',
                              'compte_budgetaire', 'groupe_marchandise', 'contrat_etat_region',
                              'contrat_etat_region_2','localisation_interministerielle', COLUMN_MONTANT_NAME]



