"""governance: cross-application audit trail for sensitive,
administrative, verification and approval actions.

Ownership and access: System-generated and append-only. Platform Super
Admin can view all; Tenant Admin views only their tenant.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AuditEvent(models.Model):
    """Append-only audit event with actor, action, target, masked
    before/after values and request context.

    Key rules: Passwords, OTPs, tokens, full passport numbers and detailed
    medical data are never stored in audit JSON. Tenant is NULL only for
    platform-level actions.
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
        db_index=True,
        help_text="Tenant context; NULL only for platform-level action.",
    )
    actor = models.ForeignKey(
        "accounts.UserTbl",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
        db_index=True,
        help_text="User performing action; NULL for system tasks; same "
        "tenant unless platform action.",
    )
    actor_role_snapshot = models.CharField(
        max_length=80, blank=True, help_text="Role/permission context of actor captured at event time."
    )
    action = models.CharField(
        max_length=80,
        help_text="Action performed; controlled action codes such as "
        "CREATE_TENANT, APPROVE_USER, VERIFY, CLASSIFY, ASSESS, GENERATE_RESUME.",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="audit_events",
        help_text="Target model; restricted allow-list.",
    )
    object_id = models.PositiveBigIntegerField(help_text="Target row identifier.")
    before_data = models.JSONField(
        null=True, blank=True, help_text="State before change; sensitive values masked; size-limited."
    )
    after_data = models.JSONField(
        null=True, blank=True, help_text="State after change; sensitive values masked; size-limited."
    )
    reason = models.TextField(
        max_length=3000,
        blank=True,
        help_text="Business reason; required for override, rejection, "
        "suspension and revocation actions.",
    )
    correlation_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text="Workflow correlation identifier; shared by events in one "
        "transaction/workflow.",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="Request IP address."
    )
    user_agent = models.TextField(
        max_length=1000, blank=True, help_text="Sanitised and length-limited "
        "request client information."
    )
    occurred_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="Event timestamp; append-only."
    )

    class Meta:
        db_table = "governance_audit_event"
        verbose_name = "AuditEvent"
        verbose_name_plural = "AuditEvent"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.action} — {self.content_type} #{self.object_id}"
