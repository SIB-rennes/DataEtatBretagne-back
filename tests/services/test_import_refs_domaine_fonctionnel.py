import json
import os
import pytest
from unittest.mock import patch, call

from app.models.refs.domaine_fonctionnel import DomaineFonctionnel
from app.services import MissingCodeColumns, import_refs, ReferentielNotFound, import_line_one_ref


def test_import_refs_with_missing_code_column(app):
    """Test that import_refs raises MissingCodeColumns exception when 'Code' column is missing."""
    with pytest.raises(MissingCodeColumns):
        import_refs('tests/data/domaine_fonctionnel.xls', 'MyModel', ['Name', 'Description', 'Value'])

def test_import_refs_with_referential_not_found(app):
    """Test that import_refs raises ReferentielNotFound exception when the referential file is not found."""
    with pytest.raises(ReferentielNotFound):
        import_refs('tests/data/non_existing.csv', 'MyModel', ['code', 'Name', 'Description', 'Value'])

def test_import_line_ref_with_referential_not_found(app):
    """Test that import_refs raises ReferentielNotFound exception when the referential file is not found."""
    with pytest.raises(ReferentielNotFound):
        import_line_one_ref('NotModel', '')

@patch('app.services.import_refs.subtask')
def test_import_refs_domaine_fonctionnel(mock_subtask,test_db):
    import_refs(os.path.abspath(os.getcwd())+'/data/domaine_fonctionnel.xls', 'DomaineFonctionnel', ['code', 'label'], sep="\t",usecols=[1, 2], skiprows=8)
    mock_subtask.assert_has_calls([
        call().delay('DomaineFonctionnel', '{"code":"X101","label":"AccesDroitJustice"}'),
        call().delay('DomaineFonctionnel', '{"code":"X0101-01","label":"Aide juridictionnelle"}'),
        call('import_line_one_ref'),
    ], any_order=True)


def test_import_line_ref_with_attribute_error(app):
    # Given
    code = '123'
    row = json.dumps({'code': code, 'name': 'Test'})
    # When
    with pytest.raises(TypeError):
        import_line_one_ref('DomaineFonctionnel', row)

def test_import_new_line_domaine_fonctionnel(app):
    # Given
    code = '123'
    row = json.dumps({'code': code, 'label': 'Test'})
    # When
    import_line_one_ref('DomaineFonctionnel', row)

    # Then
    with app.app_context():
        d = DomaineFonctionnel.query.filter_by(code=code).one()
        assert d.code == code
        assert d.label == "Test"

def test_import_update_domaine_fonctionnel_line(app, test_db):
    #Given
    update_dommaine = DomaineFonctionnel(code="xxx", label="to_update")
    with app.app_context():
        test_db.session.add(update_dommaine)

    # When
    import_line_one_ref('DomaineFonctionnel', json.dumps({'code': 'xxx', 'label': 'label_updating'}))
    import_line_one_ref('DomaineFonctionnel', json.dumps({'code': 'yyy', 'label': 'new_label'}))
    with app.app_context():
        d_to_update = DomaineFonctionnel.query.filter_by(code='xxx').one()
        assert d_to_update.label == "label_updating"
        d_new = DomaineFonctionnel.query.filter_by(code='yyy').one()
        assert d_new.label == "new_label"



