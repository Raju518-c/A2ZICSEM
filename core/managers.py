"""Reusable QuerySet/Manager base classes composed by domain-app models."""

from django.db import models


class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

    def platform_level(self):
        """Rows such as the Platform Super Admin's User where tenant is NULL."""
        return self.filter(tenant__isnull=True)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Default manager for tenant-owned models. Does not filter by tenant
    on its own — request-time tenant scoping is applied by the caller, per
    the architecture's rule that tenant context is always server-derived.
    """

    pass


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class ActiveManager(models.Manager.from_queryset(ActiveQuerySet)):
    pass


class ArchivableQuerySet(models.QuerySet):
    def not_archived(self):
        return self.filter(archived_at__isnull=True)

    def archived(self):
        return self.filter(archived_at__isnull=False)


class ArchivableManager(models.Manager.from_queryset(ArchivableQuerySet)):
    pass
