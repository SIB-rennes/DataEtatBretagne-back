import json
import os
import pytest
from unittest.mock import patch, call

from app.models.refs.referentiel_programmation import ReferentielProgrammation
from app.services import import_refs, import_line_one_ref




@patch('app.services.import_refs.subtask')
def test_import_refs_programme_financement(mock_subtask,test_db):
    import_refs(os.path.abspath(os.getcwd())+'/data/programme_financement.xls', 'ReferentielProgrammation', ['code', 'label', 'description'], skiprows=8, sep="\t",usecols=[1,2,3])
    mock_subtask.assert_has_calls([
        call().delay('ReferentielProgrammation', '{"code":"010101010103","label":"R#trib AJ CCass","description":"r#tribuer avocats CC auxil.missions AJ"}'),
        call().delay('ReferentielProgrammation', '{"code":"010101010105","label":"AJ EXPERTS","description":"RETRIBUER EXPERTS MISSIONS AJ"}'),
        call('import_line_one_ref'),
    ], any_order=True)


def test_import_line_ref_with_attribute_error(app):
    # Given
    code = '123'
    row = json.dumps({'code': code, 'name': 'Test', 'description':'toto'})
    # When
    with pytest.raises(TypeError):
        import_line_one_ref('ReferentielProgrammation', row)


def test_import_new_line_programme_financement(app):
    # Given
    code = '00001123'
    row = json.dumps({'code': code, 'label': 'Test', 'description':"test description"})
    # When
    import_line_one_ref('ReferentielProgrammation', row)

    # Then
    with app.app_context():
        r = ReferentielProgrammation.query.filter_by(code=code).one()
        assert r.code == code
        assert r.label == "Test"
        assert r.description == "test description"


