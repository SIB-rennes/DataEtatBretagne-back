import os
from datetime import date
from unittest.mock import patch, call, ANY

from app.models.financial.Ademe import Ademe
from app.models.refs.siret import Siret
from app.tasks.financial.import_financial import import_file_ademe
from app.tasks.financial.import_financial import import_line_ademe


@patch('app.tasks.financial.import_financial.subtask')
def test_import_file_ademe(mock_subtask,test_db):
    #DO
    with patch('os.remove', return_value=None): #ne pas supprimer le fichier de tests :)
        import_file_ademe(os.path.abspath(os.getcwd()) + '/data/ademe/ademe.csv')

    mock_subtask.assert_has_calls([
        call().delay(
            '{"Nom de l attribuant":"ADEME","siret_attribuant":"38529030900454","date_convention":"2021-05-05","reference_decision":"21BRD0090","nomBeneficiaire":"MEGO","siret_beneficiaire":"82815371800014","objet":"TREMPLIN pour la transition \\u00e9cologique des PME","montant":400.1,"nature":"aide en num\\u00e9raire","conditions_versement":"Echelonn\\u00e9","dates_periode_versement":"2021-05-11_2023-01-05","notification_ue":"1","pourcentage_subvention":1.0,"location_lat":48.480432,"location_lon":-4.49698,"departement":29,"naf1etlib":"Production et distribution d\'eau ; assainissement, gestion des d\\u00e9chets et d\\u00e9pollution","naf2etlib":"Collecte, traitement et \\u00e9limination des d\\u00e9chets ; r\\u00e9cup\\u00e9ration","naf3etlib":"R\\u00e9cup\\u00e9ration","naf4etlib":"R\\u00e9cup\\u00e9ration de d\\u00e9chets tri\\u00e9s","naf5etlib":"R\\u00e9cup\\u00e9ration de d\\u00e9chets tri\\u00e9s"}',
            ANY
        ),

        call().delay(
            '{"Nom de l attribuant":"ADEME","siret_attribuant":"38529030900454","date_convention":"2021-04-30","reference_decision":"21BRD0169","nomBeneficiaire":"LACTEUS","siret_beneficiaire":"49972556200023","objet":"TREMPLIN pour la transition \\u00e9cologique des PME","montant":281.2,"nature":"aide en num\\u00e9raire","conditions_versement":"Echelonn\\u00e9","dates_periode_versement":"2021-05-07_2022-09-30","notification_ue":null,"pourcentage_subvention":1.0,"location_lat":48.365607,"location_lon":-1.233353,"departement":35,"naf1etlib":"Activit\\u00e9s sp\\u00e9cialis\\u00e9es, scientifiques et techniques","naf2etlib":"Activit\\u00e9s d\'architecture et d\'ing\\u00e9nierie ; activit\\u00e9s de contr\\u00f4le et analyses techniques","naf3etlib":"Activit\\u00e9s de contr\\u00f4le et analyses techniques","naf4etlib":"Activit\\u00e9s de contr\\u00f4le et analyses techniques","naf5etlib":"Analyses, essais et inspections techniques"}',
            ANY
        ),
        call('import_line_ademe'),
    ], any_order=True)



def test_import_line_ademe(app, test_db):
    #GIVEN
    data = '{"Nom de l attribuant":"ADEME","siret_attribuant":"38529030900454","date_convention":"2021-05-05","reference_decision":"21BRD0090","nomBeneficiaire":"MEGO","siret_beneficiaire":"82815371800014","objet":"TREMPLIN pour la transition \\u00e9cologique des PME","montant":400.1,"nature":"aide en num\\u00e9raire","conditions_versement":"Echelonn\\u00e9","dates_periode_versement":"2021-05-11_2023-01-05","notification_ue":"1","pourcentage_subvention":1.0,"location_lat":48.480432,"location_lon":-4.49698,"departement":29,"naf1etlib":"Production et distribution d\'eau ; assainissement, gestion des d\\u00e9chets et d\\u00e9pollution","naf2etlib":"Collecte, traitement et \\u00e9limination des d\\u00e9chets ; r\\u00e9cup\\u00e9ration","naf3etlib":"R\\u00e9cup\\u00e9ration","naf4etlib":"R\\u00e9cup\\u00e9ration de d\\u00e9chets tri\\u00e9s","naf5etlib":"R\\u00e9cup\\u00e9ration de d\\u00e9chets tri\\u00e9s"}'

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
