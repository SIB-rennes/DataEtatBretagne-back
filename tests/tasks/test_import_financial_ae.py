import os
from unittest.mock import patch, call
import json

from app.models.financial.FinancialAe import FinancialAe
from app.models.financial.FinancialCp import FinancialCp
from app.models.refs.siret import Siret
from app.tasks import import_file_ae_financial, import_line_financial_ae


@patch('app.tasks.import_financial_tasks.subtask')
def test_import_import_file_ae(mock_subtask):
    #DO
    with patch('os.remove', return_value=None): #ne pas supprimer le fichier de tests :)
        import_file_ae_financial(os.path.abspath(os.getcwd()) + '/data/chorus/chorus_ae.csv', "35", 2023, False)

    mock_subtask.assert_has_calls([
        call().delay(
            '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500,"annee":2023,"source_region":"35"}',
            0, False),
        call().delay(
            '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":6,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":15000,"annee":2023,"source_region":"35"}',
              1, False),
        call('import_line_financial_ae'),
    ], any_order=True)



def test_import_new_line_ae(app, test_db):
    # AJout Somme positive
    data = '{"montant":22500,"annee":2023,"source_region":"35","n_ej":"2103105755","n_poste_ej":5,"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'

    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'85129663200017', 'code_commune':"35099"})):
        import_line_financial_ae(data, 0, False)

    #ASSERT
    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="2103105755").one()
        assert data.id is not None
        assert data.annee == 2023
        assert data.n_poste_ej == 5
        assert data.centre_couts == "DREETS0035"
        assert data.referentiel_programmation == "010300000108"
        assert len(data.montant_ae) == 1
        assert data.montant_ae[0].montant == 22500
        assert data.montant_ae[0].annee == 2023


def test_import_update_line_montant_positive_ae(app, test_db):
    #WHEN
    data = '{"annee":2020,"montant":22500,"source_region":"35","n_ej":"ej_to_update","n_poste_ej":5,"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, same n_ej n_poste_ej
    data_update = '{"annee":2021,"montant":10000,"source_region":"35","n_ej":"ej_to_update","n_poste_ej":5,"programme":"NEW","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.02.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000171","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"UPDATE","localisation_interministerielle":"N53"}'

    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'851296632000171', 'code_commune':"35099"})):
        import_line_financial_ae(data_update,0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="ej_to_update").all()
        assert len(data) == 1
        assert data[0].id == chorus.id
        assert data[0].annee == 2021
        assert data[0].n_poste_ej == 5
        assert data[0].centre_couts == "DREETS0035"
        assert data[0].programme == "NEW"
        assert data[0].referentiel_programmation == "010300000108"
        assert len(data[0].montant_ae) == 1
        assert data[0].montant_ae[0].annee == 2021
        assert data[0].montant_ae[0].montant == 10000


def test_import_montant_negatif(app, test_db):
    #WHEN - ligne AE sur année n-1 avec montant > 0
    data = '{"annee":2021,"source_region":"35","montant":22500,"n_ej":"ej_negatif","n_poste_ej":6,"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000172","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, avec montant < 0
    data_update = '{"annee":2022,"montant":-105.50,"n_ej":"ej_negatif","n_poste_ej":6,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000172","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'

    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'851296632000172', 'code_commune':"35099"})):
        import_line_financial_ae(data_update,0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="ej_negatif").all()
        assert len(data) == 1
        assert data[0].id == chorus.id
        assert data[0].annee == 2021
        assert data[0].n_poste_ej == 6
        assert len(data[0].montant_ae) == 2
        assert data[0].montant_ae[0].montant == 22500
        assert data[0].montant_ae[1].montant == -105.50


def test_import_montant_negatif_sur_annee_antérieur(app, test_db):
    #WHEN - ligne AE sur année 2024 avec montant > 0
    data = '{"annee":2024,"montant":22500,"n_ej":"ej_negatif_2024","n_poste_ej":7,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000173","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, avec montant < 0 sur année antérieur (normalement cas pas possible)
    data_update = '{"annee":2022,"montant":-105.50,"n_ej":"ej_negatif_2024","n_poste_ej":7,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000173","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'

    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'851296632000173', 'code_commune':"35099"})):
        import_line_financial_ae(data_update,0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="ej_negatif_2024").all()
        assert len(data) == 1
        assert data[0].id == chorus.id
        assert data[0].annee == 2024
        assert data[0].n_poste_ej == 7
        assert len(data[0].montant_ae) == 2
        assert data[0].montant_ae[0].montant == 22500
        assert data[0].montant_ae[1].montant == -105.50


def test_import_deux_montant_negatif(app, test_db):
    #WHEN - ligne AE sur année 2024 avec montant > 0
    data = '{"annee":2020,"montant":100,"n_ej":"init_positif","n_poste_ej":7,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000174","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, avec montant < 0 sur année antérieur (normalement cas pas possible)
    data_montant_2021 = '{"annee":2021,"montant":-5.50,"n_ej":"init_positif","n_poste_ej":7,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000174","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    data_montant_2022 = '{"annee":2022,"montant":-2.50,"n_ej":"init_positif","n_poste_ej":7,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000175","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'


    #DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'851296632000174', 'code_commune':"35099"})):
        import_line_financial_ae(data_montant_2021,0, False)
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise',
               return_value=Siret(**{'code': '851296632000175', 'code_commune': "35099"})):
        import_line_financial_ae(data_montant_2022, 0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="init_positif").first()
        assert data
        assert data.id == chorus.id
        assert data.annee == 2020
        assert data.n_poste_ej == 7
        assert len(data.montant_ae) == 3
        montant_100, montant_moins_5, mointant_moins_2 = data.montant_ae
        assert montant_100.montant == 100
        assert montant_moins_5.montant == -5.50
        assert mointant_moins_2.montant == -2.50


def test_import_montant_positif_apres_negatif_meme_annee(app, test_db):
    # WHEN - ligne AE sur année 2024 avec montant > 0
    data = '{"annee":2021,"montant":-102,"n_ej":"ej_negatif_2021","n_poste_ej":2,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000180","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, avec montant > 0 sur année antérieur
    data_update = '{"annee":2021,"montant":500,"n_ej":"ej_negatif_2021","n_poste_ej":2,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000180","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'

    # DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise',
               return_value=Siret(**{'code': '851296632000180', 'code_commune': "35099"})):
        import_line_financial_ae(data_update, 0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="ej_negatif_2021").first()
        assert data
        assert data.id == chorus.id
        assert data.annee == 2021
        assert data.n_poste_ej == 2
        assert len(data.montant_ae) == 1
        assert data.montant_ae[0].montant == 500 # on ne conserve que le positif


def test_import_montant_positif_apres_negatif_annee_differente(app, test_db):
    # WHEN - ligne AE sur année 2020 avec montant < 0
    data = '{"annee":2020,"montant":-0.1,"n_ej":"ej_negatif_2020","n_poste_ej":1,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000181","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'
    chorus = FinancialAe(**json.loads(data))
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, avec montant > 0
    data_update = '{"annee":2021,"montant":500,"n_ej":"ej_negatif_2020","n_poste_ej":1,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"851296632000181","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53"}'

    # DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise',
               return_value=Siret(**{'code': '851296632000181', 'code_commune': "35099"})):
        import_line_financial_ae(data_update, 0, False)

    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="ej_negatif_2020").first()
        assert data
        assert data.id == chorus.id
        assert data.annee == 2021
        assert data.n_poste_ej == 1
        assert len(data.montant_ae) == 2
        montant_ae_2020, montant_ae_2021 = data.montant_ae
        assert montant_ae_2020.montant == -0.1
        assert montant_ae_2020.annee == 2020
        assert montant_ae_2021.montant == 500
        assert montant_ae_2021.annee == 2021




def test_import_line_missing_zero_siret(app, test_db):
    data = '{"annee":2023,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"siret_ej","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"6380341500023","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}'

    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise',
               return_value=Siret(**{'code': '06380341500023', 'code_commune': "35099"})):
        import_line_financial_ae(data, 0, False)

    # ASSERT
    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="siret_ej").one()
        assert data.siret == "06380341500023"


def test_import_new_line_ae_with_siret_empty(app, test_db):
    #GIVEN
    data = '{"annee":2023,"source_region":"35","programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"siret_empty","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"#","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}'

    #DO
    import_line_financial_ae(data, 0, False)

    # ASSERT
    with app.app_context():
        data = FinancialAe.query.filter_by(n_ej="siret_empty").one()
        assert data.siret is None

def test_import_new_line_ae_with_cp(app, test_db):
    # GIVEN
    n_ej="11548315"
    data_cp_1 = '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"'+n_ej+'","n_poste_ej":"5","n_dp":1,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"18.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1400875965","fournisseur_paye_label":"AE EXIST","siret":"#","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"S198063","montant":"252"}'
    data_cp_2 = '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"'+n_ej+'","n_poste_ej":"5","n_dp":2,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"20.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1400875965","fournisseur_paye_label":"AE EXIST","siret":"#","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"S198063","montant":"100"}'
    data_cp_not_link = '{"programme":"152","domaine_fonctionnel":"0152-04-01","centre_couts":"BG00\\/GN5GDPL044","referentiel_programmation":"BG00\\/015234300101","n_ej":"not_link","n_poste_ej":"6","n_dp":3,"date_base_dp":"25.12.2022","date_derniere_operation_dp":"18.01.2023","n_sf":"#","data_sf":"#","fournisseur_paye":"1400875965","fournisseur_paye_label":"AE EXIST","siret":"#","compte_code":"PCE\\/6113110000","compte_budgetaire":"D\\u00e9penses de fonction","groupe_marchandise":"36.01.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"S198063","montant":"65"}'
    data_ae = '{"annee":2023,"source_region":"35","programme":"152","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"'+n_ej+'","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}'
    financial_cp_1 = FinancialCp(json.loads(data_cp_1), annee=2023, source_region="53")
    financial_cp_2 = FinancialCp(json.loads(data_cp_2), annee=2022, source_region="53")
    financial_cp_not_link = FinancialCp(json.loads(data_cp_not_link), annee=2022, source_region="53")
    test_db.session.add(financial_cp_1)
    test_db.session.add(financial_cp_2)
    test_db.session.add(financial_cp_not_link)
    test_db.session.commit()

    # DO
    with patch('app.tasks.import_financial_tasks.update_siret_from_api_entreprise',
               return_value=Siret(**{'code': '84442098400016', 'code_commune': "35099"})):
        import_line_financial_ae(data_ae, 0,False)

    with app.app_context():
        #Check lien ae <-> cp
        financial_ae = FinancialAe.query.filter_by(n_ej=n_ej, n_poste_ej=5).one()

        assert financial_cp_1.id_ae == financial_ae.id
        assert financial_cp_2.id_ae == financial_ae.id
        assert financial_cp_not_link.id_ae is None
