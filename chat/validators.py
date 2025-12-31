
import re
from django.core.exceptions import ValidationError

class ExactlySixAlnumPasswordValidator:
    def validate(self, password, user=None):
        if not re.fullmatch(r'[A-Za-z0-9]{6}', password or ''):
            raise ValidationError(
                'Password must be exactly 6 characters (letters or digits only).'
            )

    def get_help_text(self):
        return 'Your password must be exactly 6 characters, letters or digits only.'


# //////////////////////////////////////////////////////////////////
