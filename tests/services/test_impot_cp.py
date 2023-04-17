import os
import re

import pytest
from werkzeug.datastructures import FileStorage

from app.exceptions.exceptions import InvalidFile
from app.services import FileNotAllowedException
from app.services.financial_data import import_cp


def test_import_import_file_cp_file_not_allowed():
    # DO
    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.pdf', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] le fichier n\'est pas un csv')):
            import_cp(FileStorage(f), "35", 2023, False)

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/errors/sample.csv', 'rb') as f:
        with pytest.raises(FileNotAllowedException, match=re.escape('[FileNotAllowed] Erreur de lecture du fichier')):
            import_cp(FileStorage(f), "35", 2023, False)


def test_import_file_cp_with_file_ae():

    with open(os.path.abspath(os.getcwd()) + '/data/chorus/chorus_ae.csv', 'rb') as f:
        with pytest.raises(InvalidFile):
            import_cp(FileStorage(f), "35", 2023, False)