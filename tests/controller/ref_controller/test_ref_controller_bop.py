import json

import pytest

from app.models.refs.code_programme import CodeProgramme
from app.models.refs.ministere import Ministere
from app.models.refs.theme import Theme

ministere01 = {
    "code": "MIN01",
    "label": "label MIN01"
}
ministere02 = {
    "code": "MIN02",
    "label": "label MIN02"
}

theme01 = {
    "id": 1,
    "label": "theme 01"
}
theme02 = {
    "id": 2,
    "label": "theme 02"
}


@pytest.fixture(scope="module")
def add_data(test_db):
    data = []
    test_db.session.add(Ministere(**ministere01))
    test_db.session.add(Ministere(**ministere02))
    test_db.session.add(Theme(**theme01))
    test_db.session.add(Theme(**theme02))

    for i in range(10):
        bop = {
            "code": f"BOP{i + 1}",
            "code_ministere": "MIN01" if i % 5 == 0 else "MIN02",
            "theme": 1 if i%2 ==0 else 2,
            "label": f'label programme {i + 1}',
            "description": f"description du bop {i + 1}"
        }
        test_db.session.add(CodeProgramme(**bop))
        data.append(bop)
    test_db.session.commit()
    return data

def test_bop_by_code(test_client, add_data):
    code = "BOP2"
    resp = test_client.get('/referentiels/api/v1/programme/'+code)
    assert resp.status_code == 200
    bop_return = json.loads(resp.data.decode())
    assert bop_return == {
        "code": "BOP2",
        "code_ministere": "MIN02",
        "label_theme": "theme 02",
        "description": "description du bop 2",
        "label": "label programme 2"
    }


def test_bop_not_found(test_client, add_data):
    # GIVEN
    code_not_found = 'code_not_found'
    resp = test_client.get('/referentiels/api/v1/programme/'+code_not_found)
    assert resp.status_code == 404


def test_search_bop_no_content(test_client, add_data):
    test="fcode1"
    resp = test_client.get('/referentiels/api/v1/programme?query='+test)
    assert resp.status_code == 204

def test_search_bop_bycode_label(test_client, add_data):
    test="programme 1"
    resp = test_client.get('/referentiels/api/v1/programme?query='+test)
    assert resp.status_code == 200

    page_return = json.loads(resp.data.decode())
    assert page_return['items'].__len__() == 2
    assert page_return['pageInfo'] == {'totalRows': 2, 'page': 1, 'pageSize': 100}
