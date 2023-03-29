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
            '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}',
            0, '35', 2023, False),
        call().delay(
            '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":6,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":15000}',
              1, '35', 2023, False),
        call('import_line_chorus_ae'),
    ], any_order=True)



def test_import_new_line_chorus(app, test_db):
    data = '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"2103105755","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":"1001465507","fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}'

    #DO
    with patch('app.tasks.import_chorus_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'85129663200017', 'code_commune':"35099"})):
        import_line_chorus_ae(data, 0,"35",2023, False)

    #ASSERT
    with app.app_context():
        data = Chorus.query.filter_by(n_ej="2103105755").one()
        assert data.annee == 2023
        assert data.n_poste_ej == 5
        assert data.centre_couts == "DREETS0035"
        assert data.referentiel_programmation == "010300000108"
        assert data.montant == 22500


def test_import_update_line_chorus(app, test_db):
    #WHEN
    data = '{"programme":"103","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"ej_to_update","n_poste_ej":5,"date_modification_ej":"10.01.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"Non affect\\u00e9","localisation_interministerielle":"N53","montant":22500}'
    chorus = Chorus(json.loads(data), annee=2022, source_region="35")
    test_db.session.add(chorus)
    test_db.session.commit()

    # update data, same n_ej n_poste_ej
    data_update = '{"programme":"NEW","domaine_fonctionnel":"0103-01-01","centre_couts":"BG00\\/DREETS0035","referentiel_programmation":"BG00\\/010300000108","n_ej":"ej_to_update","n_poste_ej":5,"date_modification_ej":"10.02.2023","fournisseur_titulaire":1001465507,"fournisseur_label":"ATLAS SOUTENIR LES COMPETENCES","siret":"85129663200017","compte_code":"PCE\\/6522800000","compte_budgetaire":"Transferts aux entre","groupe_marchandise":"09.02.01","contrat_etat_region":"#","contrat_etat_region_2":"UPDATE","localisation_interministerielle":"N53","montant":25500}'

    #DO
    with patch('app.tasks.import_chorus_tasks.update_siret_from_api_entreprise', return_value=Siret(**{'code':'85129663200017', 'code_commune':"35099"})):
        import_line_chorus_ae(data_update,0,"35",2024, False)

    with app.app_context():
        data = Chorus.query.filter_by(n_ej="ej_to_update").all()
        assert len(data) == 1
        assert data[0].annee == 2024
        assert data[0].n_poste_ej == 5
        assert data[0].centre_couts == "DREETS0035"
        assert data[0].programme == "NEW"
        assert data[0].referentiel_programmation == "010300000108"
        assert data[0].montant == 25500



