import json
import os
from unittest.mock import patch, call

from app.models.refs.code_programme import CodeProgramme
from app.models.refs.ministere import Ministere
from app.services import import_refs, import_line_one_ref


@patch('app.services.import_refs.subtask')
def test_import_refs_code_programme(mock_subtask):
    # DO
    import_refs(os.path.abspath(os.getcwd())+'/data/Calculette_Chorus_test.xlsx', 'CodeProgramme',  ['code_ministere','code','label'], is_csv=False, usecols=[0,2,3],
                sheet_name="03 - Programmes", skiprows=8)

    mock_subtask.assert_has_calls([
        call().delay('CodeProgramme',
                     '{"code_ministere":"MIN01","code":"0105","label":"Action de la France en Europe et dans le monde"}'),
        call().delay('CodeProgramme',
                     '{"code_ministere":"MIN01","code":"0151","label":"Fran\\u00e7ais \\u00e0 l\'\\u00e9tranger et affaires consulaires"}'),
        call().delay('CodeProgramme',
                     '{"code_ministere":"MIN01","code":"0185","label":"Diplomatie culturelle et d\'influence"}'),
        call('import_line_one_ref'),
    ], any_order=True)


@patch('app.services.import_refs.subtask')
def test_import_refs_ministere(mock_subtask,app):
    import_refs(os.path.abspath(os.getcwd())+'/data/Calculette_Chorus_test.xlsx', 'Ministere', ['code', 'sigle_ministere','label'], is_csv=False, usecols=[0,1,2],
                sheet_name="02 - Ministères" ,skiprows=8)


    mock_subtask.assert_has_calls([
        call().delay('Ministere', '{"code":"MIN01","sigle_ministere":"MEAE","label":"Europe&Aff.\\u00c9trang\\u00e8res"}'),
        call('import_line_one_ref'),
    ], any_order=True)



def test_import_insert_code_programme_line(app, test_db):
    import_line_one_ref('CodeProgramme', json.dumps({"code":"0185","label":"Diplomatie culturelle et d\'influence","code_ministere":"MIN01"}))
    import_line_one_ref('CodeProgramme', json.dumps(
        {"code_ministere":"MIN01","code":"151","label":"TEST"}))
    with app.app_context():
        d_to_update = CodeProgramme.query.filter_by(code='185').one()
        assert d_to_update.label == "Diplomatie culturelle et d\'influence"

        d_to_update = CodeProgramme.query.filter_by(code='151').one()
        assert d_to_update.label == "TEST"
