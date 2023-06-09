import os
import re

import pytest
from werkzeug.datastructures import FileStorage

from app.exceptions.exceptions import InvalidFile, FileNotAllowedException
from app.services.financial_data import import_ae


def test_import_import_file_ae_file_not_allowed():
    # DO
    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.pdf', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] le fichier n\'est pas un csv')):
            import_ae(FileStorage(f), "35", 2023, False)

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.csv', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] Erreur de lecture du fichier')):
            import_ae(FileStorage(f), "35", 2023, False)


def test_import_file_ae_not_complete():

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/chorue_ae_missing_column.csv', 'rb') as f:
        with pytest.raises(InvalidFile):
            import_ae(FileStorage(f), "35", 2023, False)