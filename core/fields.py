"""Application-level field encryption for restricted PII / commercial /
health columns the architecture document types as "Encrypted CharField /
VARCHAR" or "Encrypted JSON/Text" (e.g. ProfessionalProfile.address_line_1,
CredentialRecord.credential_number, CredentialRecord.secure_details).

Encryption uses Fernet (symmetric, authenticated) from `cryptography`,
keyed by settings.FIELD_ENCRYPTION_KEY. Ciphertext is base64 text and
significantly longer than the plaintext, so the underlying database column
is always TEXT regardless of `max_length` — `max_length` is kept purely as
a plaintext-side validator so the documented length limits still apply.
"""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _get_fernet():
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY must be set to use encrypted fields."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedFieldMixin:
    """Stores ciphertext in a TEXT column no matter what `max_length` is
    declared for plaintext validation purposes.
    """

    def db_type(self, connection):
        return "text"

    def get_internal_type(self):
        return "TextField"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return _get_fernet().encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            return value


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    """Encrypted single-line value; `max_length` validates plaintext only."""

    pass


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    """Encrypted free-text / JSON-as-text value (e.g. secure_details)."""

    pass
