import json

import pytest

from app.models.refs.ministere import Ministere

@pytest.fixture(scope="module")
def add_data(test_db):
    ministere01 = {
        "code": "MIN01",
        "label": "label MIN01",
        "sigle_ministere": "MEAE",
        "description": "d"
    }
    ministere02 = {
        "code": "MIN02",
        "label": "Culture",
        "sigle_ministere": "MC",
        "description": "d2"
    }
    ministere03 = {
        "code": "MIN70",
        "label": "Armées",
        "sigle_ministere": "MINARM",
        "description": "d3"
    }
    test_db.session.add(Ministere(**ministere01))
    test_db.session.add(Ministere(**ministere02))
    test_db.session.add(Ministere(**ministere03))

    test_db.session.commit()
    return [ministere01, ministere02, ministere03]

def test_min_by_code(test_client, add_data):
    code = "MIN02"
    resp = test_client.get('/referentiels/api/v1/ministere/'+code)
    assert resp.status_code == 200
    min_return = json.loads(resp.data.decode())
    assert min_return == add_data[1]


def test_min_not_found(test_client, add_data):
    # GIVEN
    code_not_found = 'code_not_found'
    resp = test_client.get('/referentiels/api/v1/ministere/'+code_not_found)
    assert resp.status_code == 404


def test_search_min_no_content(test_client, add_data):
    test="fcode1"
    resp = test_client.get('/referentiels/api/v1/ministere?query='+test)
    assert resp.status_code == 204

def test_search_min_bycode_label(test_client, add_data):
    test="ulTUr"
    resp = test_client.get('/referentiels/api/v1/ministere?query='+test)
    assert resp.status_code == 200

    page_return = json.loads(resp.data.decode())
    assert page_return['items'].__len__() == 1
    assert page_return['pageInfo'] == {'totalRows': 1, 'page': 1, 'pageSize': 100}
    assert page_return['items'][0] == add_data[1]
