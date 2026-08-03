
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserTbl, roles
from catalog.models import ReferenceValue
from .models import Tenant, TenantOperation


class TenantCombinedCreateAPIViewTests(APITestCase):
    def test_create_tenant_with_admin_role_and_operations(self):
        creator = UserTbl.objects.create(
            email="creator@example.com",
            mobile_country_code="+1",
            mobile_number="1111111111",
            password="CreatorPass123",
            approval_status=UserTbl.ApprovalStatus.APPROVED,
            is_active=True,
            is_staff=True,
        )
        industry = ReferenceValue.objects.create(
            option_set="INDUSTRY",
            code="OIL_AND_GAS",
            label="Oil & Gas",
            created_by=creator,
        )

        payload = {
            "tenant": {
                "name": "Acme Tenant",
                "legal_name": "Acme Tenant Ltd",
                "code": "ACME",
                "portal_slug": "acme-tenant",
                "custom_domain": "",
                "status": Tenant.Status.ACTIVE,
                "registration_enabled": True,
                "login_enabled": True,
                "default_timezone": "UTC",
                "default_currency": "USD",
                "contact_email": "admin@acme.com",
                "contact_phone": "+15551234567",
            },
            "operations": [
                {
                    "industry": industry.pk,
                    "country_code": "US",
                    "region_name": "Texas",
                    "is_registration_enabled": True,
                    "is_active": True,
                    "effective_from": "2026-01-01",
                    "effective_to": None,
                }
            ],
            "role": {
                "code": "Admin",
                "name": "Admin",
                "roles_for": "tenant admin",
            },
            "user": {
                "email": "admin@acme.com",
                "mobile_country_code": "+1",
                "mobile_number": "5551234567",
                "password": "StrongPass123",
                "role": "Admin",
            },
        }

        response = self.client.post(
            reverse("tenancy:tenant-combined-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        self.assertEqual(Tenant.objects.count(), 1)
        self.assertEqual(TenantOperation.objects.count(), 1)
        self.assertEqual(roles.objects.count(), 1)

        tenant = Tenant.objects.get(code="ACME")
        admin_user = UserTbl.objects.get(email="admin@acme.com")
        self.assertEqual(admin_user.tenant, tenant)
        self.assertTrue(admin_user.role.exists())
        self.assertEqual(admin_user.role.first().code, "Admin")
        self.assertEqual(tenant.created_by, admin_user)
        
