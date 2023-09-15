from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .schema import JSONSchemaValidator  # pyright: ignore

PHONE_REGEX = RegexValidator(regex=r"^\+?1?\d{9,15}$", message=_("PHONE_REGEX_ERROR"))
