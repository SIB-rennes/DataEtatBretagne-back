from .import_ref_default_taks import import_line_one_ref_default
from .import_ref_localisation_interministerielle_task import import_line_ref_localisation_interministerielle

'''
package contenant les task spécifique d'import des referentiel. 
Par défaut, les référentiels sont importés via la task 'import_line_one_ref_default'.
Pour spécifier une task, il faut créer dans ce module une task sous le nom 'import_line_one_ref_<CLASS_NAME>'
Ou Class_Name est le nom de la classe du model du référentiel.
'''

__all__ = ('import_line_one_ref_default','import_line_ref_localisation_interministerielle',)
