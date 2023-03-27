import os
from unittest.mock import patch, call
import json

from app.models.financial.Chorus import Chorus
from app.models.refs.siret import Siret
from app.tasks import import_file_ae_chorus, import_line_chorus_ae


@patch('app.tasks.import_chorus_tasks.subtask')
def test_import_import_file_ae_chorus(mock_subtask):
    #DO
    import_file_ae_chorus(os.path.abspath(os.getcwd())+'/data/chorus/chorue_ae.csv', "35", 2023, False)

    for in_call in mock_subtask.mock_calls:
        if in_call[0] == '().delay' and json.loads(in_call[1][0])['siret'] == '#' :
            raise AssertionError("Siret # non reconnu")

    mock_subtask.assert_has_calls([
        call().delay(
            '{"programme_code":"103","domaine_code":"0103-01-01","centre_cout_code":"BG00\\/DREETS0035","ref_programmation_code":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":5,"date_modif":"10.01.2023","Fournisseur_code":"1001465507","Fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise_code":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle_code":"N53","montant":22500}',
            0, '35', 2023, False),
        call().delay(
            '{"programme_code":"103","domaine_code":"0103-01-01","centre_cout_code":"BG00\\/DREETS0035","ref_programmation_code":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":6,"date_modif":"10.01.2023","Fournisseur_code":"1001465507","Fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise_code":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle_code":"N53","montant":15000}',
            1, '35', 2023, False),
        call('import_line_chorus_ae'),
    ], any_order=True)



@patch('app.tasks.import_chorus_tasks.update_siret_from_api_entreprise', return_value=10)
def test_import_line_chorus(app, test_db):
    data = '{"programme_code":"103","domaine_code":"0103-01-01","centre_cout_code":"BG00\\/DREETS0035","ref_programmation_code":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":5,"date_modif":"10.01.2023","Fournisseur_code":"1001465507","Fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise_code":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle_code":"N53","montant":22500}'

    #DO
    with patch('app.tasks.import_chorus_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'85129663200017', 'code_commune':"35099"})):
        import_line_chorus_ae(data, 0,"35",2023, False)

    with app.app_context():
        data = Chorus.query.filter_by(n_ej="2103105755").one()
        assert data.annee == 2023
        assert data.n_poste_ej == 5
        assert data.centre_couts == "DREETS0035"
        assert data.referentiel_programmation == "010300000108"

