import marshmallow
import marshmallow_dataclass as ma
from marshmallow_jsonschema import JSONSchema

def _dict_get_nested(dict, *keys, default = None):
    """Récupère les valeurs imbriquées dans un dictionnaire

    Exemple:

    d = { 'a': { 'b': { 'c': 'foo' }  } }
    nested = _get_nested(d, 'a', 'b', 'c') # nested == 'foo'
    nested = _get_nested(d, 'does', 'not', 'exist') # nested == None


    Args:
        dict (_type_): Structure à parcourir
        default (_type_, optional): Valeur par défaut en cas de clef inexistante. Defaults to None.
    """

    v = dict
    for key in keys:
        try:
            v = v.get(key, default)
        except AttributeError:
            v = default
            break
    return v

class _BaseSchemaExcludingUnknown(marshmallow.Schema):
    """Schema marshmallow avec l'option d'exclure les champs unknown lors du load par défaut"""
    class Meta:
        unknown = marshmallow.EXCLUDE

class _AddMarshmallowSchema(type):
    """Metaclass qui génère le schema marshmallow pour une dataclass.
    """
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)
    
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        ma_schema_class = ma.class_schema(cls, base_schema=_BaseSchemaExcludingUnknown)
        
        cls.MarshmallowSchema = ma_schema_class

class _AddMarshmallowAndJsonSchema(_AddMarshmallowSchema):
    """Metaclass qui génère le schema marshmallow et le json schema pour la classe cible.

    Lorsque une dataclass est instanciée avec WithSchemaGen:

    class A(metaclass=WithSchemaGen):
      pass

    Elle aura deux proprietés de classe:

    - A.MarshmallowSchema: la classe représentant le schema marshmallow. 
      `schema = A.MarshmallowSchema()`
    
    - A.jsonschema: une structure native python serialisable qui représente la structure de donnée
      sous format json schema.
      `A.jsonschema`
    """
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)
    
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        ma_schema = cls.MarshmallowSchema()
        json_schema = JSONSchema().dump(ma_schema)['definitions'][name]

        cls.jsonschema = json_schema