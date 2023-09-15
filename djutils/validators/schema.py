from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.deconstruct import deconstructible
from jsonschema import Draft7Validator, validate


@deconstructible
class JSONSchemaValidator:
    _schema = None

    def __init__(self, schema=None):
        if schema:
            Draft7Validator.check_schema(schema)
        self._schema = schema

    def __call__(self, value):
        if self._schema is not None:
            try:
                validate(value, self._schema)
                return
            except ValueError as error:
                raise ValidationError(message=error)
        raise ImproperlyConfigured()
