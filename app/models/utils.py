from flask_restx import Namespace
import marshmallow
import marshmallow_dataclass as ma
from marshmallow_jsonschema import JSONSchema


class _BaseSchemaExcludingUnknown(marshmallow.Schema):
    """Schema marshmallow avec l'option d'exclure les champs unknown lors du load par défaut"""

    class Meta:
        unknown = marshmallow.EXCLUDE


class _AddMarshmallowSchema(type):
    """Metaclass qui génère le schema marshmallow pour une dataclass."""

    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        ma_schema_class = ma.class_schema(cls, base_schema=_BaseSchemaExcludingUnknown)

        cls.MarshmallowSchema = ma_schema_class


class _InstrumentForFlaskRestx(_AddMarshmallowSchema):
    """Metaclass qui génère le schema marshmallow, le json schema, et le support pour la documentation flask_restx.

    class A(metaclass=_InstrumentForFlaskRestx):
      pass
    """

    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        ma_schema = cls.MarshmallowSchema()
        ma_schema_many = cls.MarshmallowSchema(many=True)

        definitions_json_schemas = JSONSchema().dump(ma_schema)["definitions"]
        definition_jsonschema = definitions_json_schemas[name]

        def schema_model(api: Namespace):
            """Crée le schema_model depuis le json schema pour cette dataclasse"""
            return api.schema_model(name, definition_jsonschema)

        def _register_schemamodels(api: Namespace):
            models = {
                name: api.schema_model(name, json_schema)
                for name, json_schema in definitions_json_schemas.items()
            }
            return models

        def schema_model(api: Namespace):
            """Crée le schema_model depuis le json schema pour cette dataclasse.
            Enregistre aussi les la grappe auprès de l'API

            Exemple:
              @api.response(200, 'Success', model = A.schema_model(api))

            Returns:
                SchemaModel: SchemaModel flask-restx pour être enregistrer avec @api.doc ou @marshall_with
            """
            models = _register_schemamodels(api)
            return models[name]

        cls.ma_schema = ma_schema
        """Schema marshmallow. Exemple: A.ma_schema.dump(a)"""
        cls.ma_schema_many = ma_schema_many
        """Schema marshmallow (many = True). Exemple: A.ma_schema.dump(a)"""
        cls.definition_jsonschema = definition_jsonschema
        """Définition JSON schema pour le dataclass"""
        cls.definitions_jsonschemas = definitions_json_schemas
        """Dictionnaire des définitions en format JSON schema de la grappe d'objet pour la dataclass"""
        cls.schema_model = schema_model
