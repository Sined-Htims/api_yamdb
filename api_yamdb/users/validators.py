from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

username_validator = UnicodeUsernameValidator()


def username_not_me(username):
    if username.lower() == 'me':
        raise ValidationError('Данное имя нельзя использовать')
