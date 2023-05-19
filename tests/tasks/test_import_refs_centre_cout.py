import json
import os
import pytest
from unittest.mock import patch, call

from app.models.refs.centre_couts import CentreCouts
from app.tasks import import_refs_task
from app.tasks.refs import import_line_one_ref_default


@patch('app.tasks.import_refs_tasks.subtask')
def test_import_refs_centre_cout(mock_subtask,test_db):
    import_refs_task(os.path.abspath(os.getcwd())+'/data/centre_cout.xlsx', 'CentreCouts', ['code', 'description','label', 'code_postal','ville'], is_csv=False, skiprows=6,usecols=[1,2,3,4,5])


    mock_subtask.assert_has_calls([
        call().delay(model_name='CentreCouts',
                     data='{"code":"AAIACNU075","description":"ACNUSA","label":"ACNUSA","code_postal":"75006","ville":"PARIS"}'),
        call().delay(model_name='CentreCouts',
                     data='{"code":"AAIAC00075","description":"AC","label":"AC","code_postal":"75001","ville":"PARIS"}'),
        call().delay(model_name='CentreCouts',
                     data='{"code":"3070ATE012","description":"Centre de cout mutualise","label":"PRF0ATE012","code_postal":null,"ville":null}'),
        call('import_line_one_ref_default'),
    ], any_order=True)


def test_import_line_ref_with_attribute_error(app):
    # Given
    code = '3070ATE012'
    row = json.dumps({"code":code,"description":"Centre de cout mutualise","labeld":"PRF0ATE012"})
    # When
    with pytest.raises(TypeError):
        import_line_one_ref_default(cls='CentreCouts', data=row)


def test_import_new_line_centre_cout(app):
    # Given
    code = '00001123'
    row = json.dumps({"code":code,"description":"Centre de cout mutualise","label":"PRF0ATE012","code_postal":"75001","ville":"PARIS"})
    # When
    import_line_one_ref_default(model_name='CentreCouts', data=row)

    # Then
    with app.app_context():
        r = CentreCouts.query.filter_by(code=code).one()
        assert r.code == code
        assert r.label == "PRF0ATE012"
        assert r.description == "Centre de cout mutualise"
        assert r.code_postal == "75001"
        assert r.ville == "PARIS"
