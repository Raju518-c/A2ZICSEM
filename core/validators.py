"""Reusable field validators shared across every domain app."""

import zoneinfo

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

from core.constants import (
    CALLING_CODE_REGEX,
    E164_PHONE_REGEX,
    ISO_ALPHA2_REGEX,
    ISO_CURRENCY_REGEX,
    LOWERCASE_SLUG_REGEX,
    UPPERCASE_CODE_REGEX,
)

validate_uppercase_code = RegexValidator(
    regex=UPPERCASE_CODE_REGEX,
    message="Use uppercase letters, numbers and underscores only.",
    code="invalid_code",
)

validate_lowercase_slug = RegexValidator(
    regex=LOWERCASE_SLUG_REGEX,
    message="Use lowercase letters, numbers and hyphens only.",
    code="invalid_slug",
)

validate_e164_phone = RegexValidator(
    regex=E164_PHONE_REGEX,
    message="Enter a phone number in E.164 format, e.g. +14155552671.",
    code="invalid_phone",
)

validate_calling_code = RegexValidator(
    regex=CALLING_CODE_REGEX,
    message="Enter a valid international calling code, e.g. +1 or +971.",
    code="invalid_calling_code",
)

validate_iso_country_code = RegexValidator(
    regex=ISO_ALPHA2_REGEX,
    message="Enter a valid ISO 3166-1 alpha-2 country code, e.g. AE.",
    code="invalid_country_code",
)

validate_iso_currency_code = RegexValidator(
    regex=ISO_CURRENCY_REGEX,
    message="Enter a valid ISO 4217 currency code, e.g. USD.",
    code="invalid_currency_code",
)


def validate_iana_timezone(value):
    try:
        zoneinfo.ZoneInfo(value)
    except (zoneinfo.ZoneInfoNotFoundError, ValueError) as exc:
        raise ValidationError(
            "%(value)s is not a valid IANA timezone.",
            code="invalid_timezone",
            params={"value": value},
        ) from exc


def validate_not_future_date(value):
    from django.utils import timezone

    if value and value > timezone.localdate():
        raise ValidationError("Date cannot be in the future.", code="date_in_future")


def validate_past_date(value):
    from django.utils import timezone

    if value and value >= timezone.localdate():
        raise ValidationError("Date must be in the past.", code="date_not_past")


@deconstructible
class MaxFileSizeValidator:
    """Rejects an uploaded file above ``max_bytes`` (used by evidence-type
    specific size limits on EvidenceDocument).
    """

    def __init__(self, max_bytes):
        self.max_bytes = max_bytes

    def __call__(self, file_obj):
        size = getattr(file_obj, "size", None)
        if size is not None and size > self.max_bytes:
            raise ValidationError(
                "File exceeds the maximum allowed size of %(max_mb)s MB.",
                code="file_too_large",
                params={"max_mb": round(self.max_bytes / (1024 * 1024), 1)},
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_bytes == other.max_bytes
