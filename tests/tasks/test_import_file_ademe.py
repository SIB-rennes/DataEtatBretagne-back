import os
from datetime import date
from unittest.mock import MagicMock, patch, call, ANY

from app.models.financial.Ademe import Ademe
from app.models.refs.siret import Siret
from app.tasks.financial.import_financial import import_file_ademe
from app.tasks.financial.import_financial import import_line_ademe


@patch('app.tasks.financial.import_financial.subtask')
def test_import_file_ademe(mock_subtask: MagicMock,test_db):
    #DO
    with patch('os.remove', return_value=None): #ne pas supprimer le fichier de tests :)
        import_file_ademe(os.path.abspath(os.getcwd()) + '/data/ademe/ademe.csv')

    mock_subtask.assert_has_calls([
        call().delay(
            '{"Nom de l attribuant":"ADEME","idAttribuant":"38529030900454","dateConvention":"2021-05-05","referenceDecision":"21BRD0090","nomBeneficiaire":"MEGO ! - MEGO","idBeneficiaire":"82815371800014","objet":"TREMPLIN pour la transition \\u00e9cologique des PME","montant":5000,"nature":"aide en num\\u00e9raire","conditionsVersement":"Echelonn\\u00e9","datesPeriodeVersement":"2021-05-11_2023-01-05","idRAE":null,"notificationUE":"NON","pourcentageSubvention":1.0}',
            ANY
        ),

        call('import_line_ademe'),
        call('import_line_ademe'),
    ], any_order=True)



def test_import_line_ademe(app, test_db):
    #GIVEN
    data = '{"Nom de l attribuant":"ADEME","idAttribuant":"38529030900454","dateConvention":"2021-05-05","referenceDecision":"21BRD0090","nomBeneficiaire":"MEGO ! - MEGO","idBeneficiaire":82815371800014,"objet":"TREMPLIN pour la transition \u00e9cologique des PME","montant":400.1,"nature":"aide en num\u00e9raire","conditionsVersement":"Echelonn\u00e9","datesPeriodeVersement":"2021-05-11_2023-01-05","idRAE":null,"notificationUE":"NON","pourcentageSubvention":1}'

    #DO
    with patch('app.services.siret.update_siret_from_api_entreprise', return_value=Siret(**{'code':'38529030900454', 'code_commune':"35099"})):
        import_line_ademe(data, tech_info_list=('a task id', 1))

        # ASSERT
    with app.app_context():
        data = Ademe.query.filter_by(reference_decision="21BRD0090").one()
        assert data.id is not None
        assert data.montant == 400.1
        assert data.notification_ue == True
        assert data.date_convention == date(2021, 5, 5)
        assert data.siret_beneficiaire == "82815371800014"
        assert data.siret_attribuant == "38529030900454"
        assert data.dates_periode_versement == "2021-05-11_2023-01-05"
