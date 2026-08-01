import json
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as AuthUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from accounts.models import ConsentRecord, OTPVerification, RegistrationApplication, UserTbl, roles
from accounts.views import RegisterAPIView
from catalog.models import ReferenceValue, ScopeCatalog
from evidence.models import EvidenceDocument
from professionals.models import ProfessionalProfile
from tenancy.models import Tenant


class LoginAPIViewTests(TestCase):
    def setUp(self):
        self.auth_user = AuthUser.objects.create_user(username="platform-user", password="PlatformPass123")
        self.platform_user = UserTbl.objects.create(
            id=self.auth_user.pk,
            email="platform@example.com",
            mobile_country_code="+91",
            mobile_number="9999999999",
            password="unused",
            approval_status=UserTbl.ApprovalStatus.APPROVED,
            approved_at=timezone.now(),
            is_active=True,
            is_superuser=True,
            is_staff=True,
        )
        self.platform_user.password = make_password("PlatformPass123")
        self.platform_user.save(update_fields=["password", "updated_at"])

        self.tenant = Tenant.objects.create(
            name="Demo Tenant",
            legal_name="Demo Tenant",
            code="DEMO",
            portal_slug="demo",
            default_timezone="UTC",
            default_currency="USD",
            contact_email="tenant@example.com",
            created_by=self.platform_user,
        )

        self.role = roles.objects.create(
            code="PROFESSIONAL",
            name="Professional",
            roles_for="tenant admin",
            tenant=self.tenant,
        )

        self.user = UserTbl.objects.create(
            tenant=self.tenant,
            email="user@example.com",
            mobile_country_code="+91",
            mobile_number="8888888888",
            password="unused",
            approval_status=UserTbl.ApprovalStatus.APPROVED,
            approved_at=timezone.now(),
            is_active=True,
            is_superuser=False,
            is_staff=False,
        )
        self.user.password = make_password("StrongPass123")
        self.user.save(update_fields=["password", "updated_at"])
        self.user.role.add(self.role)

    def test_login_returns_profile_and_tokens(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "tenant": "demo",
                "email": "user@example.com",
                "password": "StrongPass123",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["tenant"]["portal_slug"], "demo")
        self.assertEqual(payload["role"], ["Professional"])
        self.assertFalse(payload["is_candidate"])
        self.assertFalse(payload["is_mentor"])
        self.assertEqual(self.client.session["user_id"], self.user.id)
        self.assertEqual(self.client.session["tenant_id"], str(self.tenant.id))

    def test_register_creates_user_profile_application_and_consent(self):
        industry = ReferenceValue.objects.create(
            option_set="INDUSTRY",
            code="MARINE",
            label="Marine",
            created_by=self.platform_user,
        )
        scope = ScopeCatalog.objects.create(
            code="OG-LPM",
            industry=industry,
            scope_name="Line Pipe Marine",
            created_by=self.platform_user,
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "tenant_id": str(self.tenant.public_id),
                "account": {
                    "email": "newcandidate@example.com",
                    "mobile_country_code": "+61",
                    "mobile_number": "412345678",
                    "password": "NewPassword123!",
                    "two_factor_preference": "EMAIL",
                },
                "profile": {
                    "first_name": "Jane",
                    "middle_name": "M",
                    "last_name": "Doe",
                    "preferred_name": "Jane",
                    "country_of_residence": "AU",
                    "city": "Sydney",
                    "time_zone": "Australia/Sydney",
                    "primary_industry": str(industry.pk),
                    "primary_scope": str(scope.pk),
                    "career_stage": "EARLY_CAREER",
                    "current_job_title": "Marine Engineer",
                    "total_experience_band": "3_TO_6",
                    "highest_qualification": "BACHELOR",
                    "existing_resume": False,
                },
                "consent": {
                    "terms": True,
                    "privacy": True,
                    "resume_processing": False,
                    "marketing": False,
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.json())
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Registration completed successfully.")

        user = UserTbl.objects.get(email="newcandidate@example.com")
        self.assertEqual(user.tenant, self.tenant)
        self.assertTrue(user.is_active)

        application = RegistrationApplication.objects.get(user=user)
        self.assertEqual(application.tenant, self.tenant)
        self.assertEqual(application.selected_industry, industry)
        self.assertEqual(application.selected_scope, scope)

        profile = ProfessionalProfile.objects.get(user=user)
        self.assertEqual(profile.first_name, "Jane")
        self.assertEqual(profile.last_name, "Doe")
        self.assertEqual(profile.primary_industry, industry)
        self.assertEqual(profile.primary_scope, scope)

        consent_records = ConsentRecord.objects.filter(user=user)
        self.assertTrue(consent_records.filter(consent_type="TERMS", is_granted=True).exists())
        self.assertTrue(consent_records.filter(consent_type="PRIVACY", is_granted=True).exists())
        self.assertTrue(consent_records.filter(consent_type="MARKETING", is_granted=False).exists())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_otp_request_and_verify_with_tenant_id_and_email(self):
        with patch("accounts.views._deliver_otp") as mock_deliver_otp:
            response = self.client.post(
                reverse("accounts:otp-request"),
                {
                    "tenant_id": str(self.tenant.public_id),
                    "otp_type": "EMAIL",
                    "email": "user@example.com",
                },
                content_type="application/json",
            )

            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["success"])
            self.assertTrue(mock_deliver_otp.called)
            sent_to, raw_otp = mock_deliver_otp.call_args[0]
            self.assertEqual(sent_to, "user@example.com")
            self.assertEqual(len(raw_otp), 6)

        response = self.client.post(
            reverse("accounts:otp-verify"),
            {
                "tenant_id": str(self.tenant.public_id),
                "otp_type": "EMAIL",
                "email": "user@example.com",
                "otp": raw_otp,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Email verified successfully.")

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)

    def test_register_saves_resume_to_evidence_document(self):
        industry = ReferenceValue.objects.create(
            option_set="INDUSTRY",
            code="MARINE",
            label="Marine",
            created_by=self.platform_user,
        )
        scope = ScopeCatalog.objects.create(
            code="OG-LPM",
            industry=industry,
            scope_name="Line Pipe Marine",
            created_by=self.platform_user,
        )

        payload = {
            "tenant_id": str(self.tenant.public_id),
            "account": json.dumps({
                "email": "resumeuser@example.com",
                "mobile_country_code": "+61",
                "mobile_number": "412345678",
                "password": "ResumePassword123!",
                "two_factor_preference": "EMAIL",
            }),
            "profile": json.dumps({
                "first_name": "Resume",
                "last_name": "User",
                "existing_resume": True,
                "primary_industry": str(industry.pk),
                "primary_scope": str(scope.pk),
            }),
            "consent": json.dumps({
                "terms": True,
                "privacy": True,
                "resume_processing": True,
                "marketing": False,
            }),
            "resume": SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
        }

        factory = APIRequestFactory()
        request = factory.post("/register/", data=payload, format="multipart")
        response = RegisterAPIView.as_view()(request)

        self.assertEqual(response.status_code, 201, response.data if hasattr(response, "data") else response.content)
        user = UserTbl.objects.get(email="resumeuser@example.com")
        profile = ProfessionalProfile.objects.get(user=user)
        evidence_document = EvidenceDocument.objects.filter(professional=profile).first()
        self.assertIsNotNone(evidence_document)
        self.assertEqual(evidence_document.original_file_name, "resume.pdf")
        self.assertTrue(evidence_document.file.name)

    def test_register_saves_profile_photo_to_professional_profile(self):
        industry = ReferenceValue.objects.create(
            option_set="INDUSTRY",
            code="MARINE",
            label="Marine",
            created_by=self.platform_user,
        )
        scope = ScopeCatalog.objects.create(
            code="OG-LPM",
            industry=industry,
            scope_name="Line Pipe Marine",
            created_by=self.platform_user,
        )

        payload = {
            "tenant_id": str(self.tenant.public_id),
            "account": json.dumps({
                "email": "photouser@example.com",
                "mobile_country_code": "+61",
                "mobile_number": "412345678",
                "password": "PhotoPassword123!",
                "two_factor_preference": "EMAIL",
            }),
            "profile": json.dumps({
                "first_name": "Photo",
                "last_name": "User",
                "existing_resume": False,
                "primary_industry": str(industry.pk),
                "primary_scope": str(scope.pk),
            }),
            "consent": json.dumps({
                "terms": True,
                "privacy": True,
                "resume_processing": False,
                "marketing": False,
            }),
            "profile_photo": SimpleUploadedFile("photo.jpg", b"JPEGIMAGE", content_type="image/jpeg"),
        }

        factory = APIRequestFactory()
        request = factory.post("/register/", data=payload, format="multipart")
        response = RegisterAPIView.as_view()(request)

        self.assertEqual(response.status_code, 201, response.data if hasattr(response, "data") else response.content)
        user = UserTbl.objects.get(email="photouser@example.com")
        profile = ProfessionalProfile.objects.get(user=user)
        self.assertIsNotNone(profile.profile_photo_evidence)
        self.assertEqual(profile.profile_photo_evidence.original_file_name, "photo.jpg")
        self.assertTrue(profile.profile_photo_evidence.file.name)
        self.assertEqual(profile.profile_photo_evidence.evidence_type.code, "PHOTOGRAPH")

