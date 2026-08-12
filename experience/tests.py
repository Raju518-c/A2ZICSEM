from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from accounts.models import RegistrationApplication, UserTbl
from catalog.models import (
    FormField,
    FormModule,
    ReferenceValue,
    ReferencevalueoptionSet,
    ScopeCatalog,
    ScopeModule,
)
from experience.models import ProjectRecord, ProjectScope, ScopeResponse
from experience.serializers import BulkProjectRecordSerializer
from professionals.models import ProfessionalProfile
from tenancy.models import Tenant


class DynamicScopeFormViewTests(TestCase):
    def setUp(self):
        self.platform_user = UserTbl.objects.create(
            email="platform-form@example.com",
            mobile_country_code="+971",
            mobile_number="500000011",
            password="very-secret",
        )
        self.tenant = Tenant.objects.create(
            name="Dynamic Form Tenant",
            legal_name="Dynamic Form Tenant LLC",
            code="DYNTENANT",
            portal_slug="dynamic-form-tenant",
            custom_domain=None,
            default_timezone="UTC",
            default_currency="AED",
            contact_email="dynamic@example.com",
            contact_phone="+971500000011",
            created_by=self.platform_user,
        )
        self.user = UserTbl.objects.create(
            tenant=self.tenant,
            email="dynamic-professional@example.com",
            mobile_country_code="+971",
            mobile_number="500000012",
            password="very-secret",
        )
        self.industry_option_set = ReferencevalueoptionSet.objects.create(option_type="INDUSTRY")
        self.industry = ReferenceValue.objects.create(
            option_set=self.industry_option_set,
            code="IND-02",
            label="Marine",
            created_by=self.platform_user,
        )
        self.scope_catalog = ScopeCatalog.objects.create(
            code="SURV-02",
            industry=self.industry,
            scope_name="Marine Warranty Survey",
            created_by=self.platform_user,
        )
        self.form_module = FormModule.objects.create(
            module_code="SM-MARINE",
            module_name="Marine Survey",
            version=1,
            status="PUBLISHED",
            created_by=self.platform_user,
            published_at=timezone.now(),
        )
        ScopeModule.objects.create(
            scope=self.scope_catalog,
            form_module=self.form_module,
            sequence=1,
            created_by=self.platform_user,
        )
        self.form_field = FormField.objects.create(
            form_module=self.form_module,
            field_code="sm_marine.survey_type",
            field_label="Survey type",
            data_type="STRING",
            ui_control="text",
            created_by=self.platform_user,
        )
        self.authority_option_set = ReferencevalueoptionSet.objects.create(option_type="AUTHORITY_ACTION")
        self.authority_action = ReferenceValue.objects.create(
            option_set=self.authority_option_set,
            code="PERFORMED",
            label="Performed",
            created_by=self.platform_user,
        )
        self.registration_application = RegistrationApplication.objects.create(
            tenant=self.tenant,
            user=self.user,
            selected_industry=self.industry,
            selected_scope=self.scope_catalog,
            selected_operating_country="AE",
            status="APPROVED",
            reviewed_by=self.user,
            reviewed_at=timezone.now(),
        )
        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
            registration_application=self.registration_application,
        )
        self.project = ProjectRecord.objects.create(
            tenant=self.tenant,
            professional=self.professional,
            project_name="Marine Project",
            client_name_snapshot="Client Marine",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            is_current=False,
            status="DRAFT",
        )
        self.project_scope = ProjectScope.objects.create(
            tenant=self.tenant,
            project=self.project,
            scope=self.scope_catalog,
            authority_action=self.authority_action,
            status="DRAFT",
        )

    def test_get_dynamic_scope_form_returns_fields_for_scope(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("experience:project-scope-dynamic-form", args=[self.project_scope.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["data"]["scope"]["id"], self.scope_catalog.pk)
        self.assertEqual(response.json()["data"]["form_fields"][0]["field_code"], self.form_field.field_code)

    def test_post_dynamic_scope_form_saves_scope_responses(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "responses": [
                {"field_code": self.form_field.field_code, "value": "GTAW"}
            ]
        }
        response = self.client.post(
            reverse("experience:project-scope-dynamic-form", args=[self.project_scope.pk]),
            payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ScopeResponse.objects.filter(project_scope=self.project_scope).count(), 1)
        self.assertEqual(
            ScopeResponse.objects.get(project_scope=self.project_scope, form_field=self.form_field).value,
            "GTAW",
        )


class BulkProjectRecordSerializerTests(TestCase):
    def setUp(self):
        self.platform_user = UserTbl.objects.create(
            email="platform@example.com",
            mobile_country_code="+971",
            mobile_number="500000001",
            password="very-secret",
        )
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            legal_name="Test Tenant LLC",
            code="TESTTENANT",
            portal_slug="test-tenant",
            custom_domain=None,
            default_timezone="UTC",
            default_currency="AED",
            contact_email="tenant@example.com",
            contact_phone="+971500000001",
            created_by=self.platform_user,
        )
        self.user = UserTbl.objects.create(
            tenant=self.tenant,
            email="professional@example.com",
            mobile_country_code="+971",
            mobile_number="500000002",
            password="very-secret",
        )
        self.option_set = ReferencevalueoptionSet.objects.create(option_type="INDUSTRY")
        self.industry = ReferenceValue.objects.create(
            option_set=self.option_set,
            code="IND-01",
            label="Oil & Gas",
            created_by=self.platform_user,
        )
        self.scope_catalog = ScopeCatalog.objects.create(
            code="WELD-01",
            industry=self.industry,
            scope_name="Welding Inspection",
            created_by=self.platform_user,
        )
        self.form_module = FormModule.objects.create(
            module_code="SM-WELD",
            module_name="Welding",
            version=1,
            status="PUBLISHED",
            created_by=self.platform_user,
            published_at=timezone.now(),
        )
        self.form_field = FormField.objects.create(
            form_module=self.form_module,
            field_code="sm_weld.welding_process",
            field_label="Welding process",
            data_type="STRING",
            ui_control="text",
            created_by=self.platform_user,
        )
        self.registration_application = RegistrationApplication.objects.create(
            tenant=self.tenant,
            user=self.user,
            selected_industry=self.industry,
            selected_scope=self.scope_catalog,
            selected_operating_country="AE",
            status="APPROVED",
            reviewed_by=self.user,
            reviewed_at=timezone.now(),
        )
        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
            registration_application=self.registration_application,
        )

    def test_bulk_serializer_creates_project_records_with_nested_scopes_and_responses(self):
        payload = {
            "project_records": [
                {
                    "project_name": "Project A",
                    "client": "Client A",
                    "project_scopes": [
                        {
                            "scope_name": "Welding Inspection",
                            "scope_responses": [
                                {
                                    "field_code": "sm_weld.welding_process",
                                    "value": "GTAW",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        serializer = BulkProjectRecordSerializer(
            data=payload,
            context={"tenant": self.tenant, "professional": self.professional},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        created_records = serializer.save()

        self.assertEqual(ProjectRecord.objects.count(), 1)
        self.assertEqual(ProjectScope.objects.count(), 1)
        self.assertEqual(ScopeResponse.objects.count(), 1)
        self.assertEqual(created_records[0].client_name_snapshot, "Client A")

    def test_bulk_api_creates_project_records_with_nested_scopes_and_responses(self):
        payload = {
            "project_records": [
                {
                    "project_name": "Project A",
                    "client": "Client A",
                    "project_scopes": [
                        {
                            "scope_name": "Welding Inspection",
                            "scope_responses": [
                                {
                                    "field_code": "sm_weld.welding_process",
                                    "value": "GTAW",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        payload["professional_profile"] = str(self.professional.pk)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("experience:bulk-project-record-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        self.assertEqual(ProjectRecord.objects.count(), 1)
        self.assertEqual(ProjectScope.objects.count(), 1)
        self.assertEqual(ScopeResponse.objects.count(), 1)
