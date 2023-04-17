import datetime
from abc import abstractmethod
from datetime import datetime
from app.models.common.Audit import Audit


class FinancialData(Audit):


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


    def update_attribute(self,  data: dict):
        """
        update instance chorus avec les infos d'une ligne issue d'un fichier chorus
        :param data:
        :return:
        """

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @abstractmethod
    def do_update(self, new_financial: dict):
        pass

    @staticmethod
    def _fix_siret(value: str) -> str:
        if len(value) < 14 :
            nb_zeros_a_ajouter = 14 - len(value)
            value = '0' * nb_zeros_a_ajouter + str(value)

        return value