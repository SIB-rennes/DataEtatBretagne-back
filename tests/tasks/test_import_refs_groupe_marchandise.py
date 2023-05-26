import os
from unittest.mock import patch, call

from app.tasks.import_refs_tasks import import_refs_task


@patch('app.tasks.import_refs_tasks.subtask')
def test_import_refs_groupe_marchandise_pce(mock_subtask,test_db):
    import_refs_task(os.path.abspath(os.getcwd()) + '/data/Calculette_Chorus_test.xlsx', 'GroupeMarchandise',
                ['domaine','segment','code', 'label', 'description','code_pce','label_pce'], is_csv=False, usecols=[1,3,4,5,7,10,11],
                sheet_name="19 - Groupe Marchandise", skiprows=8)


    mock_subtask.assert_has_calls([
        call().delay(model_name='GroupeMarchandise',
                     data='{"domaine":"Affranchissement et impression","segment":"Affranchissement","code":"01.01.01","label":"EX-AI EXP\\u00c9DITION","description":"EX-FRAIS POSTAUX YC VALIISE DIPLOMATIQUE","code_pce":"6161000000","label_pce":"FRAIS POSTAUX"}'),
        call('import_line_one_ref_default'),
    ], any_order=True)

