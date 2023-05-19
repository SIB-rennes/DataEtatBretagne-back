import json
import os
from unittest.mock import patch, call

import pytest

from app.models.refs.commune import Commune
from app.models.refs.localisation_interministerielle import LocalisationInterministerielle
from app.tasks.import_refs_tasks import import_refs_task
from app.tasks.refs import import_line_ref_localisation_interministerielle


@pytest.fixture(scope="module")
def add_comune_belley(test_db):

    commune_belley = Commune(**{
            "code": "01034",
            "label_commune": "Belley",
            "code_departement": "01"
        })
    test_db.session.add(commune_belley)
    test_db.session.commit()
    test_db.session.flush()
    return commune_belley

@pytest.fixture(scope="module")
def add_comune_angers(test_db):

    commune = Commune(**{
            "code": "0000",
            "label_commune": "Angers",
            "code_departement": "49"
        })
    test_db.session.add(commune)
    test_db.session.commit()
    test_db.session.flush()
    return commune



@patch('app.tasks.import_refs_tasks.subtask')
def test_import_refs_localisation_interministerielle(mock_subtask,test_db):
    import_refs_task(os.path.abspath(os.getcwd()) + '/data/LOC_INTERMIN_20230126.csv', 'LocalisationInterministerielle',
                ['code','niveau','code_departement','commune','site','code_parent','label'], usecols=[0,1,3,5,6,9,10], sep=";")

    mock_subtask.assert_has_calls([
        call().delay(model_name='LocalisationInterministerielle',
                     data='{"code":"B100000","niveau":"BATIMENT","code_departement":"30","commune":"N\\u00eemes","site":"CASERNE MAJOR SOLER","code_parent":"S120594","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}'),
        call('import_line_one_ref_LocalisationInterministerielle'),
    ], any_order=True)

def test_import_insert_localisation(app, test_db, add_comune_belley):
    import_line_ref_localisation_interministerielle(data=json.dumps({"code":"B100000","niveau":"NATIONAL","code_departement":"01","commune":"Belley","site":"CASERNE MAJOR SOLER","code_parent":"S120594","label":"ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}))
    with app.app_context():
        d_to_update = LocalisationInterministerielle.query.filter_by(code='B100000').one()
        assert d_to_update.commune.label_commune == "Belley"
        assert d_to_update.commune_id == add_comune_belley.id
        assert d_to_update.site == "CASERNE MAJOR SOLER"
        assert d_to_update.niveau == "NATIONAL"
        assert d_to_update.code_parent == "S120594"


def test_import_insert_localisation_inter_exist(app, test_db, add_comune_belley, add_comune_angers):
    #WHEN Insert loc inter à Belley

    loc = LocalisationInterministerielle(**{
            "code": "B215151",
            "niveau": "to_update",
            "label": "to_update",
        })
    loc.commune = add_comune_belley
    test_db.session.add(loc)
    test_db.session.commit()

    #DO
    import_line_ref_localisation_interministerielle(data=json.dumps({"code":loc.code,"niveau":"NATIONAL","code_departement":"49","commune":"Angers","site":"CASERNE SOLER","code_parent":"XXXX","label":"TEST ATELIER DE REPARATION ET D\'ENTRETIEN BAT 3"}))

    # ASSERT
    with app.app_context():
        d_to_update = LocalisationInterministerielle.query.filter_by(code=loc.code).one()
        assert d_to_update.commune.label_commune == "Angers"
        assert d_to_update.commune_id == add_comune_angers.id
        assert d_to_update.site == "CASERNE SOLER"
        assert d_to_update.niveau == "NATIONAL"
        assert d_to_update.code_parent == "XXXX"

