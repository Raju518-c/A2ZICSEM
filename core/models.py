"""Composable abstract base models used across every domain app.

Per the architecture's common database conventions:
  - BigAutoField primary keys (via DEFAULT_AUTO_FIELD).
  - UUID public_id on externally exposed aggregate records.
  - Timezone-aware created_at/updated_at on every table.
  - tenant_id on every tenant-owned record; the request tenant is
    server-derived and never trusted from client payload.

Not every table needs every mixin — e.g. some history tables have no
public_id, and platform-level tables (ReferenceValue, ScopeCatalog,
FormModule) carry no tenant. Each app composes only what its model row in
the architecture document actually specifies.

This app defines no concrete models and therefore has no migrations.
"""

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Adds an immutable, globally unique external identifier."""

    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Safe external identifier used in APIs and integrations.",
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Adds timezone-aware creation/update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatedOnlyModel(models.Model):
    """For append-only / immutable-after-write tables that carry only a
    creation timestamp (e.g. ConsentRecord, CompetencyAssessment,
    AuditEvent).
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True


class TenantOwnedModel(models.Model):
    """Adds the tenant foreign key shared by every tenant-owned row.

    Default on_delete is PROTECT, matching the documented case for the
    majority of tenant-owned tables (ProfessionalProfile, CredentialRecord,
    EmploymentRecord, etc). The handful of tables that CASCADE with their
    tenant (TenantOperation, Organization) declare their own `tenant` field
    directly instead of using this mixin.
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
        help_text="Tenant that owns this record. Server-derived; never "
        "trusted from client payload.",
    )

    class Meta:
        abstract = True


class ArchivableModel(models.Model):
    """Adds an optional archive timestamp for records that are archived
    rather than hard-deleted (CredentialRecord, EvidenceDocument, ...).
    """

    archived_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

