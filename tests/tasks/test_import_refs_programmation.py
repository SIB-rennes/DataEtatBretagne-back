import json
import os
import pytest
from unittest.mock import patch, call

from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.tasks.import_refs_tasks import import_refs_task
from app.tasks.refs import import_line_one_ref_default


@patch('app.tasks.import_refs_tasks.subtask')
def test_import_refs_programme_financement(mock_subtask,test_db):
    import_refs_task(os.path.abspath(os.getcwd())+'/data/Calculette_Chorus_test.xlsx', 'ReferentielProgrammation',  ['code','label'], is_csv=False, usecols=[9,10],
                sheet_name="08 - Activités (OS,OP,OB,ACT)", skiprows=8)
    mock_subtask.assert_has_calls([
        call().delay(model_name='ReferentielProgrammation', data='{"code":"010101010101","label":"DOTATIONS CARPA AJ ET AUTRES INTERVENTIONS"}'),
        call().delay(model_name='ReferentielProgrammation', data='{"code":"010101010106","label":"RETRIBUER AVOCATS CE CCASS MISSIONS AJ"}'),
        call('import_line_one_ref_default'),
    ], any_order=True)


def test_import_line_ref_with_attribute_error(app):
    # Given
    code = '123'
    row = json.dumps({'code': code, 'name': 'Test', 'description':'toto'})
    # When
    with pytest.raises(TypeError):
        import_line_one_ref_default('ReferentielProgrammation', row)


def test_import_new_line_programme_financement(app):
    # Given
    code = '00001123'
    row = json.dumps({'code': code, 'label': 'Test', 'description':"test description"})
    # When
    import_line_one_ref_default('ReferentielProgrammation', row)

    # Then
    with app.app_context():
        r = ReferentielProgrammation.query.filter_by(code=code).one()
        assert r.code == code
        assert r.label == "Test"
        assert r.description == "test description"


