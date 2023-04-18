import os
from unittest.mock import patch, call

from app.models.financial.FinancialCp import FinancialCp
from app.models.refs.siret import Siret
from app.tasks.import_financial_tasks import import_file_cp_financial, import_line_financial_cp


@patch('app.tasks.import_financial_tasks.subtask')
def test_import_import_file_cp(mock_subtask):
    # DO
    with patch('os.remove', return_value=None):  # ne pas supprimer le fichier de tests :)
        import_file_cp_financial(os.path.abspath(os.getcwd()) + '/data/chorus/financial_cp.csv', "35", 2023, False)

    mock_subtask.assert_has_calls([
        call().delay(
            '{"programme":"101","domaine_fonctionnel":"0101-01","centre_couts":"BG00\\/DSJCARE035","referentiel_programmation":"BG00\\/010101010113","n_ej":"#","n_poste_ej":"#","n_dp":500043027,"date_base_dp":"31.12.2022","date_derniere_operation_dp":"25.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1001477845","fournisseur_paye_label":"SANS AE","siret":"84442098400016","compte_code":"PCE\\/6512300000","compte_budgetaire":"Transferts aux m\\u00e9nag","groupe_marchandise":"#","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N","montant":"28,26"}',
            0, '35', 2023, False),
        call().delay(
            '{"programme":"101","domaine_fonctionnel":"0101-01","centre_couts":"BG00\\/DSJCARE035","referentiel_programmation":"BG00\\/010101010113","n_ej":"#","n_poste_ej":"#","n_dp":500043030,"date_base_dp":"31.12.2022","date_derniere_operation_dp":"25.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1001273578","fournisseur_paye_label":"SANS AE","siret":"41867744900054","compte_code":"PCE\\/6512300000","compte_budgetaire":"Transferts aux m\\u00e9nag","groupe_marchandise":"#","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N","montant":"27,96"}',
            1, '35', 2023, False),
        call().delay(
            '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"2103105755","n_poste_ej":"5","n_dp":100011636,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"18.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1400875965","fournisseur_paye_label":"AE EXIST","siret":"#","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"S198063","montant":"252"}',
            2, '35', 2023, False),
        call().delay(
            '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"2103105755","n_poste_ej":"5","n_dp":100011636,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"18.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1400875965","fournisseur_paye_label":"AE EXIST 2","siret":"#","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"S198063","montant":"150"}',
            3, '35', 2023, False),
        call().delay(
            '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"2103105755","n_poste_ej":"1","n_dp":100011552,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"18.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1001246979","fournisseur_paye_label":"AE NOT EXIST","siret":"45228173600010","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N5244215","montant":"807,28"}',
                4, '35', 2023, False),
        call('import_line_financial_cp')
    ], any_order=True)


def test_import_new_line_cp_without_ae(app, test_db):
    #GIVEN
    data = '{"programme":"101","domaine_fonctionnel":"0101-01","centre_couts":"BG00\\/DSJCARE035","referentiel_programmation":"BG00\\/010101010113","n_ej":"#","n_poste_ej":"#","n_dp":500043027,"date_base_dp":"31.12.2022","date_derniere_operation_dp":"25.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":1001477845,"fournisseur_paye_label":"SANS AE","siret":"84442098400016","compte_code":"PCE\\/6512300000","compte_budgetaire":"Transferts aux m\\u00e9nag","groupe_marchandise":"#","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N","montant":"28,26"}'

    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'84442098400016', 'code_commune':"35099"})):
        import_line_financial_cp(data, 0,"35",2023, False)

        # ASSERT
    with app.app_context():
        data = FinancialCp.query.filter_by(n_dp="500043027").one()
        assert data.id_ae is None
        assert data.annee == 2023
        assert data.programme == "101"
        assert data.n_poste_ej == None
        assert data.n_ej == None
        assert data.centre_couts == "DSJCARE035"
        assert data.referentiel_programmation == "010101010113"
        assert data.montant == 28.26