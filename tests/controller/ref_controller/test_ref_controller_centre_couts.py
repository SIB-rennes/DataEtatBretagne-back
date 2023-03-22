import json
from unittest import mock
from unittest.mock import patch

import pytest

from app.models.refs.centre_couts import CentreCouts


@pytest.fixture(scope="module")
def add_data(test_db):
    data = []
    for i in range(20):
        cc = {
            "code": f"code{i + 1}",
            "label": f"Test code{i * 10}",
            "description": "description du code",
            "code_postal": f'3540{i + 1}',
            "ville": f"Rennes {i + 1}"
        }
        test_db.session.add(CentreCouts(**cc))
        data.append(cc)
    test_db.session.commit()
    return data

def test_centre_cout_by_code(test_client, add_data):
    code = add_data[0]['code']
    resp = test_client.get('/referentiels/api/v1/centre_couts/'+code)
    assert resp.status_code == 200
    cc_return = json.loads(resp.data.decode())
    assert cc_return == add_data[0]


def test_centre_cout_by_code_not_found(test_client, add_data):
    # GIVEN
    code_not_found = 'code_not_found'
    resp = test_client.get('/referentiels/api/v1/centre_couts/'+code_not_found)
    assert resp.status_code == 404


def test_search_centre_cout_no_content(test_client, add_data):
    test="fcode1"
    resp = test_client.get('/referentiels/api/v1/centre_couts?query='+test)
    assert resp.status_code == 204

def test_search_centre_cout_bycode_label(test_client, add_data):
    test="code12"
    resp = test_client.get('/referentiels/api/v1/centre_couts?query='+test)
    assert resp.status_code == 200

    page_return = json.loads(resp.data.decode())
    assert page_return['items'].__len__() == 2
    assert add_data[11] in  page_return['items']
    assert add_data[12] in page_return['items']
    assert page_return['pageInfo'] == {'totalRows': 2, 'page': 1, 'pageSize': 100}


def test_search_centre_cout_bycode(test_client, add_data):
    test="code1"
    resp = test_client.get('/referentiels/api/v1/centre_couts?query='+test+'&limit=5&pageNumber=0')
    resp_page2 = test_client.get('/referentiels/api/v1/centre_couts?query=' + test + '&limit=5&pageNumber=2')

    assert resp.status_code == 200
    assert resp_page2.status_code == 200

    page1_return = json.loads(resp.data.decode())
    page2_return = json.loads(resp_page2.data.decode())
    assert page1_return['items'].__len__() == 5
    assert page2_return['items'].__len__() == 5

    assert add_data[0] in page1_return['items'] #code1
    assert add_data[9] in page1_return['items'] #code10
    assert add_data[10] in page1_return['items'] #code11
    assert add_data[11] in page1_return['items'] #code12
    assert add_data[12] in page1_return['items'] #code13

    assert add_data[13] in page2_return['items']  # code14
    assert add_data[14] in page2_return['items']  # code15
    assert add_data[15] in page2_return['items']  # code16
    assert add_data[16] in page2_return['items']  # code17

    assert page1_return['pageInfo'] == {'totalRows': 13, 'page': 1, 'pageSize': 5}
    assert page2_return['pageInfo'] == {'totalRows': 13, 'page': 2, 'pageSize': 5}

