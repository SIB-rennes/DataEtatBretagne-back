import os
import re
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from app.models.audit.AuditUpdateData import AuditUpdateData
from app.models.enums.DataType import DataType
from app.exceptions.exceptions import InvalidFile, FileNotAllowedException
from app.services.financial_data import import_cp


def test_import_import_file_cp_file_not_allowed():
    # DO
    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.pdf', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] le fichier n\'est pas un csv')):
            import_cp(FileStorage(f), "35", 2023)

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.csv', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] Erreur de lecture du fichier')):
            import_cp(FileStorage(f), "35", 2023)


def test_import_file_cp_with_file_ae():

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/chorus_ae.csv', 'rb') as f:
        with pytest.raises(InvalidFile):
            import_cp(FileStorage(f), "35", 2023)

def test_import_file_cp_ok(app,test_db):
    filename = os.path.abspath(os.getcwd()) + '/data/chorus/financial_cp.csv'
    with patch('app.tasks.financial.import_financial.import_file_cp_financial', return_value=None):  # ne pas supprimer le fichier de tests :)
        with open(filename, 'rb') as f:
            import_cp(FileStorage(f), "35", 2023)

    #ASSERT
    with app.app_context():
        r = AuditUpdateData.query.filter_by(data_type=DataType.FINANCIAL_DATA_CP).one()
        assert r.filename == filename