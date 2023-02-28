import json
import os
from unittest.mock import patch, call

from app.models.refs.code_programme import CodeProgramme
from app.models.refs.ministere import Ministere
from app.services import import_refs, import_line_one_ref


@patch('app.services.import_refs.subtask')
def test_import_refs_code_programme(mock_subtask):
    # DO
    import_refs(os.path.abspath(os.getcwd())+'/data/code_programme.ods', 'CodeProgramme', ['code', 'label','code_ministere'], is_csv=False, usecols=[3,5,6])


    mock_subtask.assert_has_calls([
        call().delay('CodeProgramme',
                     '{"code":"105","label":"Action de la France en Europe et dans le monde","code_ministere":"1"}'),
        call().delay('CodeProgramme',
                     '{"code":"151","label":"Fran\\u00e7ais \\u00e0 l\'\\u00e9tranger et affaires consulaires","code_ministere":"1"}'),
        call().delay('CodeProgramme',
                     '{"code":"185","label":"Diplomatie culturelle et d\'influence","code_ministere":"1"}'),
        call('import_line_one_ref'),
    ], any_order=True)


@patch('app.services.import_refs.subtask')
def test_import_refs_ministere(mock_subtask,app):
    import_refs(os.path.abspath(os.getcwd())+'/data/code_programme.ods', 'Ministere', ['code', 'label'], is_csv=False, usecols=[6,7])


    mock_subtask.assert_has_calls([
        call().delay('Ministere', '{"code":"1","label":"Europe et affaires \\u00e9trang\\u00e8res"}'),
        call('import_line_one_ref'),
    ], any_order=True)



def test_import_insert_code_programme_line(app, test_db):
    import_line_one_ref('CodeProgramme', json.dumps({"code":"185","label":"Diplomatie culturelle et d\'influence","code_ministere":"1"}))
    with app.app_context():
        d_to_update = CodeProgramme.query.filter_by(code='185').one()
        assert d_to_update.label == "Diplomatie culturelle et d\'influence"
