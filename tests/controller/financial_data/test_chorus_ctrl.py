import io
import os
from unittest.mock import patch

import pytest


def test_missing_arguments(test_client):
    file_content = b'test content'
    file = io.BytesIO(file_content)
    file.filename = 'fake_file.csv'

    data = {}
    data['fichier'] = (file, file.filename)
    with patch('app.controller.Decorators._get_user_permissions',return_value='ADMIN'):
        response = test_client.post('/financial-data/api/v1/ae', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 400
        assert {'message': 'Missing Argument code_region or annee', 'type': 'error'} == response.json

        response_missing_file = test_client.post('/financial-data/api/v1/ae', data={},content_type='multipart/form-data', follow_redirects=True)
        assert response_missing_file.status_code == 400
        assert {'message': 'Missing File', 'type': 'error'} == response_missing_file.json


def test_not_role(test_client):
    #WITH
    file_content = b'test content'
    file = io.BytesIO(file_content)
    file.filename = 'fake_file.csv'

    data = {}
    data['fichier'] = (file, file.filename)
    with patch('app.controller.Decorators._get_user_permissions', return_value=None):
        response = test_client.post('/financial-data/api/v1/ae', data=data,
                                    content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 403
        assert {'message': 'Vous n`avez pas les droits', 'type':'error'} == response.json




def test_bad_file(test_client):
    data = {'code_region':'35', 'annee':2023}
    with patch('app.controller.Decorators._get_user_permissions', return_value='ADMIN'):
        with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.pdf', 'rb') as f:
            data['fichier'] = (f, 'filename.csv')
            response = test_client.post('/financial-data/api/v1/ae', data=data,
                                        content_type='multipart/form-data', follow_redirects=True)

            assert response.status_code == 400
            assert {'message': 'Erreur de lecture du fichier', 'type': 'error'} == response.json


def test_file_missing_column(test_client):
    data = {'code_region':'35', 'annee':2023}
    with patch('app.controller.Decorators._get_user_permissions', return_value='ADMIN'):
        with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/chorue_ae_missing_column.csv', 'rb') as f:
            data['fichier'] = (f, f.name)
            response = test_client.post('/financial-data/api/v1/ae', data=data,
                                        content_type='multipart/form-data', follow_redirects=True)

            assert response.status_code == 400
            assert {'message': 'Le fichier contient des valeurs vides', 'type': 'error'} == response.json