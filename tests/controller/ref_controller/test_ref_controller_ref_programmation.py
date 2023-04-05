import json

import pytest

from app.models.refs.referentiel_programmation import ReferentielProgrammation


@pytest.fixture(scope="module")
def add_data(test_db):
    data = []
    for i in range(10):
        rp = {
            "code": f"010{i + 1}012CA",
            "label": f"Test code{i * 10}",
            "description": "description du code"
        }
        test_db.session.add(ReferentielProgrammation(**rp))
        data.append(rp)
    test_db.session.commit()
    return data

def test_ref_prog_by_code(test_client, add_data):
    code = add_data[0]['code']
    resp = test_client.get('/budget/api/v1/ref-programmation/'+code)
    assert resp.status_code == 200
    cc_return = json.loads(resp.data.decode())
    assert cc_return['code'] == add_data[0]['code']
    assert cc_return['label'] == add_data[0]['label']
    assert cc_return['code_programme'] == "101"


def test_ref_prog_by_code_not_found(test_client, add_data):
    # GIVEN
    code_not_found = 'code_not_found'
    resp = test_client.get('/budget/api/v1/ref-programmation/'+code_not_found)
    assert resp.status_code == 404


def test_search_ref_prog_no_content(test_client, add_data):
    test="fcode1"
    resp = test_client.get('/budget/api/v1/ref-programmation?query='+test)
    assert resp.status_code == 204

def test_search_ref_prog_bycode_label(test_client, add_data):
    test="0101"
    resp = test_client.get('/budget/api/v1/ref-programmation?query='+test)
    assert resp.status_code == 200

    page_return = json.loads(resp.data.decode())
    assert page_return['items'].__len__() == 2

    assert page_return['items'][0]['code'] == add_data[9]['code']
    assert page_return['items'][1]['code'] == add_data[0]['code']

    assert page_return['items'][0]['label'] == add_data[9]['label']
    assert page_return['items'][1]['label'] == add_data[0]['label']
    assert page_return['items'][0]['code_programme'] == "101"
    assert page_return['items'][1]['code_programme'] == "101"

    assert page_return['pageInfo'] == {'totalRows': 2, 'page': 1, 'pageSize': 100}
