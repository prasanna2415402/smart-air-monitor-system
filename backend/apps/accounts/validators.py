import re

from django.core.exceptions import ValidationError


class ComplexPasswordValidator:
    """
    Mirrors the exact password policy enforced by the original Next.js
    signup form's zod schema: at least 8 chars, one uppercase, one
    lowercase, one digit, one special character.
    """

    def validate(self, password, user=None):
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one number.")
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            "Your password must be at least 8 characters and include an uppercase "
            "letter, a lowercase letter, a number, and a special character."
        )
