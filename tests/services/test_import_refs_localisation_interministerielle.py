import json
import os
from unittest.mock import patch, call

from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.services import import_refs, import_line_one_ref


@patch('app.services.import_refs.subtask')
def test_import_refs_localisation_interministerielle(mock_subtask,test_db):
    import_refs(os.path.abspath(os.getcwd()) + '/data/LOC_INTERMIN_20230126.csv', 'LocalisationInterministerielle',
                ['code','code_departement','commune','site','label'], usecols=[0,3,5,6,10], sep=";")

    mock_subtask.assert_has_calls([
        call().delay('LocalisationInterministerielle',
                     '{"code":"B100000","code_departement":"30","commune":"N\\u00eemes","site":"CASERNE MAJOR SOLER","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}'),
        call('import_line_one_ref'),
    ], any_order=True)

def test_import_insert_localisation(app, test_db):
    import_line_one_ref('LocalisationInterministerielle', json.dumps({"code":"B100000","code_departement":"30","commune":"N\\u00eemes","site":"CASERNE MAJOR SOLER","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}))
    with app.app_context():
        d_to_update = LocalisationInterministerielle.query.filter_by(code='B100000').one()
        assert d_to_update.code_departement == "30"
        assert d_to_update.commune == "Nîmes"
        assert d_to_update.site == "CASERNE MAJOR SOLER"
