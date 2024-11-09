from django.core.exceptions import ValidationError


class NotValidInstance(ValidationError):
    pass