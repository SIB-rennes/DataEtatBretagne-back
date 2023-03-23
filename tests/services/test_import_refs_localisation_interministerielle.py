import json
import os
from unittest.mock import patch, call

from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.services import import_refs, import_line_one_ref


@patch('app.services.import_refs.subtask')
def test_import_refs_localisation_interministerielle(mock_subtask,test_db):
    import_refs(os.path.abspath(os.getcwd()) + '/data/LOC_INTERMIN_20230126.csv', 'LocalisationInterministerielle',
                ['code','niveau','code_departement','commune','site','code_parent','label'], usecols=[0,1,3,5,6,9,10], sep=";")

    mock_subtask.assert_has_calls([
        call().delay('LocalisationInterministerielle',
                     '{"code":"B100000","niveau":"BATIMENT","code_departement":"30","commune":"N\\u00eemes","site":"CASERNE MAJOR SOLER","code_parent":"S120594","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}'),
        call('import_line_one_ref'),
    ], any_order=True)

def test_import_insert_localisation(app, test_db):
    import_line_one_ref('LocalisationInterministerielle', json.dumps({"code":"B100000","niveau":"NATIONAL","code_departement":"30","commune":"N\\u00eemes","site":"CASERNE MAJOR SOLER","code_parent":"S120594","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}))
    with app.app_context():
        d_to_update = LocalisationInterministerielle.query.filter_by(code='B100000').one()
        assert d_to_update.code_departement == "30"
        assert d_to_update.commune == "Nîmes"
        assert d_to_update.site == "CASERNE MAJOR SOLER"
        assert d_to_update.niveau == "NATIONAL"
        assert d_to_update.code_parent == "S120594"

