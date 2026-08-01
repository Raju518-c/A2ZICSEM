import logging
from django.contrib.auth.models import User as AuthUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from core.choices import DataClassification, ResumeVisibility, VerificationStatus
from evidence.models import EvidenceDocument
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from accounts.models import (
    ConsentRecord,
    OTPCooldownError,
    OTPVerification,
    RegistrationApplication,
    UserTbl,
)
from catalog.models import ReferenceValue, ScopeCatalog
from professionals.models import ProfessionalProfile
from tenancy.models import Tenant

from .serializers import (
    CheckUserExistsRequestSerializer,
    ConsentRecordSerializer,
    LoginSerializer,
    LogoutSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    RegisterRequestSerializer,
    RegistrationApplicationSerializer,
    UserTblSerializer,
)

logger = logging.getLogger(__name__)


def _deliver_otp(sent_to, raw_otp):
    """Sends the OTP by email. Returns True if a real send was attempted,
    False if sent_to is a mobile number — no SMS gateway is wired up in
    this project yet, so the code is only logged (still usable for
    development/testing, but never reaches a real phone).
    """
    if "@" not in sent_to:
        logger.info("OTP for %s: %s (SMS gateway not configured)", sent_to, raw_otp)
        return False

    try:
        send_mail(
            subject="Your verification code",
            message=(
                f"Your verification code is {raw_otp}. It expires in "
                f"{OTPVerification.OTP_TTL_MINUTES} minutes."
            ),
            from_email=None,
            recipient_list=[sent_to],
            fail_silently=False,
        )
    except Exception:
        # Never surface delivery failures to the client (same response
        # either way — the OTP row still exists and can be resent), but
        # make sure they're visible in logs instead of silently dropped.
        logger.exception("Failed to send OTP email to %s", sent_to)

    return True



@method_decorator(csrf_exempt, name='dispatch')
class UserTblListCreateAPIView(APIView):
    """
    GET  : Get all users
    POST : Create a new user
    """

    def get(self, request):
        users = UserTbl.objects.all().order_by("email")
        serializer = UserTblSerializer(users, many=True)
        return Response(
            {"success": True, "message": "Users fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=UserTblSerializer)
    def post(self, request):
        serializer = UserTblSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class UserTblRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get user by ID
    PUT    : Update user (partial)
    DELETE : Delete user
    """

    def get_object(self, pk):
        try:
            return UserTbl.objects.get(pk=pk)
        except UserTbl.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserTblSerializer(user)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=UserTblSerializer)
    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserTblSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "User updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"success": True, "message": "User deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class RegistrationApplicationListCreateAPIView(APIView):
    """
    GET  : Get all registration applications
    POST : Create a new registration application
    """

    def get(self, request):
        applications = RegistrationApplication.objects.all().order_by("-created_at")
        serializer = RegistrationApplicationSerializer(applications, many=True)
        return Response(
            {"success": True, "message": "Registration applications fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=RegistrationApplicationSerializer)
    def post(self, request):
        serializer = RegistrationApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Registration application created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class RegistrationApplicationRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get registration application by ID
    PUT    : Update registration application (partial)
    DELETE : Delete registration application
    """

    def get_object(self, pk):
        try:
            return RegistrationApplication.objects.get(pk=pk)
        except RegistrationApplication.DoesNotExist:
            return None

    def get(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response({"success": False, "message": "Registration application not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegistrationApplicationSerializer(application)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=RegistrationApplicationSerializer)
    def put(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response({"success": False, "message": "Registration application not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegistrationApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Registration application updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response({"success": False, "message": "Registration application not found."}, status=status.HTTP_404_NOT_FOUND)
        application.delete()
        return Response({"success": True, "message": "Registration application deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ConsentRecordListCreateAPIView(APIView):
    """
    GET  : Get all consent records
    POST : Create a new consent record
    """

    def get(self, request):
        consent_records = ConsentRecord.objects.all().order_by("-created_at")
        serializer = ConsentRecordSerializer(consent_records, many=True)
        return Response(
            {"success": True, "message": "Consent records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=ConsentRecordSerializer)
    def post(self, request):
        serializer = ConsentRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Consent record created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ConsentRecordRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get consent record by ID
    PUT    : Update consent record (partial)
    DELETE : Delete consent record
    """

    def get_object(self, pk):
        try:
            return ConsentRecord.objects.get(pk=pk)
        except ConsentRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        consent_record = self.get_object(pk)
        if not consent_record:
            return Response({"success": False, "message": "Consent record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConsentRecordSerializer(consent_record)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(request=ConsentRecordSerializer)
    def put(self, request, pk):
        consent_record = self.get_object(pk)
        if not consent_record:
            return Response({"success": False, "message": "Consent record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConsentRecordSerializer(consent_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Consent record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        consent_record = self.get_object(pk)
        if not consent_record:
            return Response({"success": False, "message": "Consent record not found."}, status=status.HTTP_404_NOT_FOUND)
        consent_record.delete()
        return Response({"success": True, "message": "Consent record deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    # serializer_class = RegisterRequestSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _resolve_tenant(self, tenant_value):
        if not tenant_value:
            return None

        tenant_value = str(tenant_value).strip()

        if not tenant_value:
            return None

        # Integer DB ID
        if tenant_value.isdigit():
            tenant = Tenant.objects.filter(id=int(tenant_value)).first()
            if tenant:
                return tenant

        # UUID
        try:
            tenant = Tenant.objects.filter(public_id=tenant_value).first()
            if tenant:
                return tenant
        except (ValueError, ValidationError):
            pass

        # Portal slug
        return Tenant.objects.filter(portal_slug=tenant_value).first()

    def _resolve_reference_value(self, value):
        if not value:
            return None
        if isinstance(value, ReferenceValue):
            return value
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return None

        for lookup in ("public_id", "id", "code"):
            try:
                instance = ReferenceValue.objects.get(**{lookup: value})
            except (ReferenceValue.DoesNotExist, ValueError, FieldError):
                continue
            return instance
        return None

    def _resolve_scope_catalog(self, value):
        if not value:
            return None
        if isinstance(value, ScopeCatalog):
            return value
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return None

        for lookup in ("public_id", "id", "code"):
            try:
                instance = ScopeCatalog.objects.get(**{lookup: value})
            except (ScopeCatalog.DoesNotExist, ValueError, FieldError):
                continue
            return instance
        return None

    def _coerce_bool(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y"}:
                return True
            if normalized in {"false", "0", "no", "n", "none", "null", ""}:
                return False
        return bool(value)
    
    def _get_or_create_resume_evidence_type(self, user):
        try:
            return ReferenceValue.objects.get(option_set="EVIDENCE_TYPE", code="RESUME")
        except ReferenceValue.DoesNotExist:
            creator = UserTbl.objects.filter(pk__in=AuthUser.objects.values("pk")).first()
            if creator is None:
                creator = UserTbl.objects.filter(is_superuser=True).first()
            if creator is None:
                creator = UserTbl.objects.order_by("pk").first()
            if creator is None:
                creator = user

            return ReferenceValue.objects.create(
                option_set="EVIDENCE_TYPE",
                code="RESUME",
                label="Resume",
                created_by=creator,
                is_system=True,
                is_active=True,
            )

    def _get_or_create_profile_photo_evidence_type(self, user):
        try:
            return ReferenceValue.objects.get(option_set="EVIDENCE_TYPE", code="PHOTOGRAPH")
        except ReferenceValue.DoesNotExist:
            creator = UserTbl.objects.filter(pk__in=AuthUser.objects.values("pk")).first()
            if creator is None:
                creator = UserTbl.objects.filter(is_superuser=True).first()
            if creator is None:
                creator = UserTbl.objects.order_by("pk").first()
            if creator is None:
                creator = user

            return ReferenceValue.objects.create(
                option_set="EVIDENCE_TYPE",
                code="PHOTOGRAPH",
                label="Photograph",
                created_by=creator,
                is_system=True,
                is_active=True,
            )

    def _create_resume_evidence(self, tenant, profile, user, resume_file):
        if not resume_file:
            return None

        evidence_type = self._get_or_create_resume_evidence_type(user)
        content_type = ContentType.objects.get_for_model(ProfessionalProfile)
        evidence_document = EvidenceDocument.objects.create(
            tenant=tenant,
            professional=profile,
            content_type=content_type,
            object_id=profile.pk,
            evidence_type=evidence_type,
            file=resume_file,
            data_classification=DataClassification.PROFESSIONAL,
            resume_visibility=ResumeVisibility.CLIENT_SPECIFIC,
            verification_status=VerificationStatus.EVIDENCE_UPLOADED,
            processing_status=EvidenceDocument.ProcessingStatus.UPLOADED,
        )
        return evidence_document

    def _create_profile_photo_evidence(self, tenant, profile, user, profile_photo_file):
        if not profile_photo_file:
            return None

        evidence_type = self._get_or_create_profile_photo_evidence_type(user)
        content_type = ContentType.objects.get_for_model(ProfessionalProfile)
        evidence_document = EvidenceDocument.objects.create(
            tenant=tenant,
            professional=profile,
            content_type=content_type,
            object_id=profile.pk,
            evidence_type=evidence_type,
            file=profile_photo_file,
            data_classification=DataClassification.PROFESSIONAL,
            resume_visibility=ResumeVisibility.CLIENT_SPECIFIC,
            verification_status=VerificationStatus.EVIDENCE_UPLOADED,
            processing_status=EvidenceDocument.ProcessingStatus.UPLOADED,
        )
        return evidence_document


    def _build_profile_payload(self, profile_payload, profile):
        field_map = {
            "first_name": "first_name",
            "middle_name": "middle_name",
            "last_name": "last_name",
            "preferred_name": "preferred_name",
            "country_of_residence": "country_of_residence",
            "city": "city",
            "time_zone": "timezone",
            "timezone": "timezone",
            "primary_industry": "primary_industry",
            "primary_scope": "primary_scope",
            "self_declared_career_stage": "self_declared_career_stage",
            "current_job_title": "current_job_title",
            "initial_experience_band": "initial_experience_band",
            "highest_qualification_level": "highest_qualification_level",
            "name_display_order": "name_display_order",
        }

        for source_key, target_key in field_map.items():
            if source_key not in profile_payload:
                continue
            value = profile_payload[source_key]
            if value in (None, ""):
                continue
            if target_key in {"primary_industry", "primary_scope", "self_declared_career_stage", "highest_qualification_level"}:
                if target_key == "primary_industry":
                    resolved = self._resolve_reference_value(value)
                elif target_key == "primary_scope":
                    resolved = self._resolve_scope_catalog(value)
                else:
                    resolved = self._resolve_reference_value(value)
                if resolved:
                    setattr(profile, target_key, resolved)
                continue

            setattr(profile, target_key, value)

        if getattr(profile, "first_name", "") and getattr(profile, "last_name", ""):
            profile.display_name = f"{profile.first_name} {profile.last_name}".strip()

    @extend_schema(request=RegisterRequestSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        resume_file = payload.get("existing_resume")
        profile_photo_file = payload.get("profile_photo")

        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        mobile_country_code = (payload.get("mobile_country_code") or "").strip()
        mobile_number = (payload.get("mobile_number") or "").strip()

        if not email or not password or not mobile_country_code or not mobile_number:
            return Response(
                {"success": False, "message": "Email, password, mobile country code, and mobile number are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant = self._resolve_tenant(payload.get("tenant"))
        if not tenant:
            return Response({"success": False, "message": "Tenant not found."}, status=status.HTTP_400_BAD_REQUEST)

        if UserTbl.objects.filter(tenant=tenant, email__iexact=email).exists():
            return Response(
                {"success": False, "message": "A user with this email already exists for the tenant."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user = UserTbl.objects.create(
                    tenant=tenant,
                    email=email,
                    mobile_country_code=mobile_country_code,
                    mobile_number=mobile_number,
                    password=password,
                    approval_status=UserTbl.ApprovalStatus.APPROVED,
                    approved_at=timezone.now(),
                    is_active=True,
                    is_candidate=False,
                    is_mentor=False,
                    referral_source=payload.get("referral_source") or None,
                    referral_code=payload.get("referral_code") or None,
                )

                if payload.get("mfa_method"):
                    normalized_method = str(payload.get("mfa_method")).upper()
                    mfa_map = {
                        "NONE": UserTbl.MfaMethod.NONE,
                        "AUTHENTICATOR": UserTbl.MfaMethod.AUTHENTICATOR,
                        "SMS": UserTbl.MfaMethod.SMS,
                        "EMAIL": UserTbl.MfaMethod.EMAIL,
                    }
                    user.mfa_method = mfa_map.get(normalized_method, user.mfa_method)
                    user.save(update_fields=["mfa_method", "updated_at"])

                industry = self._resolve_reference_value(payload.get("primary_industry"))
                scope = self._resolve_scope_catalog(payload.get("primary_scope"))
                if not industry or not scope:
                    raise ValueError("Primary industry and primary scope are required.")

                stage1_snapshot = {
                    key: (value.name if hasattr(value, "name") else value)
                    for key, value in payload.items()
                    if key not in {"existing_resume", "profile_photo"}
                }

                application = RegistrationApplication.objects.create(
                    tenant=tenant,
                    user=user,
                    selected_industry=industry,
                    selected_scope=scope,
                    selected_operating_country=(payload.get("country_of_residence") or "")[:2],
                    status=RegistrationApplication.Status.SUBMITTED,
                    submitted_at=timezone.now(),
                    stage1_snapshot=stage1_snapshot,
                )

                profile = ProfessionalProfile.objects.create(
                    tenant=tenant,
                    user=user,
                    registration_application=application,
                    profile_status=ProfessionalProfile.ProfileStatus.STAGE1_COMPLETE,
                )
                self._build_profile_payload(payload, profile)
                profile.save()

                consent_records = []
                consent_map = {
                    "terms": ConsentRecord.ConsentType.TERMS,
                    "privacy": ConsentRecord.ConsentType.PRIVACY,
                    "resume_processing": ConsentRecord.ConsentType.RESUME_PROCESSING,
                    "marketing": ConsentRecord.ConsentType.MARKETING,                    
                }
                for input_key, consent_type in consent_map.items():
                    if input_key not in payload:
                        continue
                    granted = self._coerce_bool(payload.get(input_key))
                    consent_records.append(
                        ConsentRecord(
                            tenant=tenant,
                            user=user,
                            professional=profile,
                            consent_type=consent_type,
                            document_version="v1",
                            jurisdiction=(payload.get("country_of_residence") or "")[:2],
                            is_granted=granted,
                            granted_at=timezone.now() if granted else None,
                            source=ConsentRecord.Source.WEB,
                        )
                    )
                if consent_records:
                    ConsentRecord.objects.bulk_create(consent_records)

                resume_evidence = self._create_resume_evidence(tenant, profile, user, resume_file)
                photo_evidence = self._create_profile_photo_evidence(tenant, profile, user, profile_photo_file)
                if resume_evidence:
                    profile.existing_resume = resume_evidence
                if photo_evidence:
                    profile.profile_photo_evidence = photo_evidence
                if resume_evidence or photo_evidence:
                    profile.save(update_fields=[field for field in ["existing_resume", "profile_photo_evidence", "updated_at"] if getattr(profile, field) is not None])

                return Response(
                    {
                        "success": True,
                        "message": "Registration completed successfully.",
                        "data": {
                            "tenant_id": str(tenant.public_id),
                            "user_id": str(user.public_id),
                            "application_id": str(application.public_id),
                            "profile_id": str(profile.public_id),
                            "resume_evidence_document_id": str(resume_evidence.public_id) if resume_evidence else None,
                            "photo_evidence_document_id": str(photo_evidence.public_id) if photo_evidence else None,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
        except ValueError as exc:
            return Response({"success": False, "message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "updated_at"])

        request.session.flush()
        request.session["user_id"] = user.id
        request.session["tenant_id"] = str(user.tenant.id) if user.tenant else None
        request.session["is_authenticated"] = True
        request.session.save()

        tenant_payload = None
        if user.tenant:
            tenant_payload = {
                "id": str(user.tenant.public_id),
                "name": user.tenant.name,
                "portal_slug": user.tenant.portal_slug,
                "status": user.tenant.status,
            }

        professional_profile = ProfessionalProfile.objects.filter(user=user).first()
        profile_payload = {
            "id": user.id,
            "public_id": str(user.public_id),
            "first_name": professional_profile.first_name if professional_profile else "",
            "last_name": professional_profile.last_name if professional_profile else "",
        }

        return Response(
            {
                "status": "success",
                "tenant": tenant_payload,
                "role": [role.name for role in user.role.all()],
                "is_candidate": user.is_candidate,
                "is_mentor": user.is_mentor,
                "user": profile_payload,
            },
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    @extend_schema(request=LogoutSerializer)
    def post(self, request, *args, **kwargs):
        request.session.flush()
        return Response(
            {"status": "success", "message": "Logout successful."},
            status=status.HTTP_200_OK,
        )




class CheckUserExistsAPIView(APIView):
    """Return whether a tenant+email combination already exists."""

    permission_classes = [AllowAny]

    @extend_schema(request=CheckUserExistsRequestSerializer)
    def post(self, request, *args, **kwargs):
        serializer = CheckUserExistsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        tenant_value = validated_data.get("tenant") or validated_data.get("tenant_id")
        email = (validated_data.get("email") or "").strip().lower()

        if not tenant_value or not email:
            return Response(
                {"success": False, "message": "tenant and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tenant = None
        if tenant_value:
            tenant_value = str(tenant_value).strip()
            if tenant_value.isdigit():
                tenant = Tenant.objects.filter(id=int(tenant_value)).first()
            else:
                tenant = (
                    Tenant.objects.filter(public_id=tenant_value).first()
                    or Tenant.objects.filter(portal_slug=tenant_value).first()
                )

        if tenant is None:
            return Response(
                {"success": False, "message": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        exists = UserTbl.objects.filter(tenant=tenant, email__iexact=email).exists()
        return Response(
            {
                "success": True,
                "status": "exist" if exists else "new",
                "tenant": str(tenant.public_id),
                "email": email,
            },
            status=status.HTTP_200_OK,
        )


class OTPRequestAPIView(APIView):
    """
    POST : Issue an OTP for otp_type in {EMAIL, MOBILE, LOGIN, PASSWORD_RESET}.
    EMAIL/MOBILE also cover re-verifying a changed address via new_value.
    LOGIN validates the password and requires MFA to be enabled first.
    """

    permission_classes = [AllowAny]
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = serializer.validated_data.get("tenant")
        otp_type = serializer.validated_data["otp_type"]
        sent_to = serializer.validated_data.get("sent_to")

        generic_message = "If the details are valid, a verification code has been sent."
        generic_response = Response(
            {"success": True, "message": generic_message},
            status=status.HTTP_200_OK,
        )

        # sent_to is None only for PASSWORD_RESET against a non-existent
        # account (anti-enumeration); every other otp_type always has one,
        # including pre-registration EMAIL/MOBILE with no account yet.
        if sent_to is None:
            return generic_response

        try:
            _, raw_otp = OTPVerification.issue(tenant=tenant, otp_type=otp_type, sent_to=sent_to)
        except OTPCooldownError as exc:
            # PASSWORD_RESET keeps the generic response even on cooldown,
            # otherwise a 429 vs 200 becomes an account-existence oracle.
            if otp_type == OTPVerification.OTPType.PASSWORD_RESET:
                return generic_response
            return Response(
                {"success": False, "message": str(exc)},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        delivered_by_email = _deliver_otp(sent_to, raw_otp)
        if delivered_by_email:
            return generic_response

        # sent_to was a mobile number: no SMS gateway exists yet, so no
        # message actually reached the user. Say so instead of falsely
        # claiming success on a channel that doesn't work — this only
        # happens for MOBILE verification, or LOGIN when mfa_method=SMS,
        # never PASSWORD_RESET (always emailed) or an anonymous request
        # (both already returned above).
        return Response(
            {
                "success": True,
                "message": (
                    "Verification code generated, but SMS delivery is not "
                    "available in this environment yet. Use email "
                    "verification instead, or check server logs for the code."
                ),
            },
            status=status.HTTP_200_OK,
        )


class OTPVerifyAPIView(APIView):
    """
    POST : Verify an OTP and apply its effect.
    EMAIL/MOBILE mark the address verified (and apply new_value if this
    was a change). PASSWORD_RESET sets new_password. LOGIN completes the
    session, mirroring LoginAPIView's response shape.
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        row = serializer.validated_data["otp_row"]
        otp_type = serializer.validated_data["otp_type"]

        # is_used is committed together with the side effect below: if the
        # user update fails, the OTP stays valid instead of being burned.
        with transaction.atomic():
            row.is_used = True
            row.save(update_fields=["is_used"])

            if user is None:
                # Pre-registration EMAIL/MOBILE: no account exists yet to
                # mutate. The registration endpoint is expected to check
                # OTPVerification directly for (tenant, sent_to, otp_type,
                # is_used=True) before creating the account.
                message = (
                    "Email verified."
                    if otp_type == OTPVerification.OTPType.EMAIL
                    else "Mobile number verified."
                )
                return Response(
                    {"success": True, "message": message},
                    status=status.HTTP_200_OK,
                )

            if otp_type == OTPVerification.OTPType.EMAIL:
                user.email = row.sent_to
                user.email_verified_at = timezone.now()
                user.save(update_fields=["email", "email_verified_at", "updated_at"])
                return Response(
                    {"success": True, "message": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )

            if otp_type == OTPVerification.OTPType.MOBILE:
                prefix = user.mobile_country_code
                number = row.sent_to[len(prefix):] if row.sent_to.startswith(prefix) else row.sent_to
                user.mobile_number = number
                user.mobile_verified_at = timezone.now()
                user.save(update_fields=["mobile_number", "mobile_verified_at", "updated_at"])
                return Response(
                    {"success": True, "message": "Mobile number verified successfully."},
                    status=status.HTTP_200_OK,
                )

            if otp_type == OTPVerification.OTPType.PASSWORD_RESET:
                user.password = serializer.validated_data["new_password"]
                user.save(update_fields=["password", "updated_at"])
                return Response(
                    {"success": True, "message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )

            # LOGIN — same session bootstrap and response shape as LoginAPIView.
            user.last_login = timezone.now()
            user.save(update_fields=["last_login", "updated_at"])

            request.session.flush()
            request.session["user_id"] = user.id
            request.session["tenant_id"] = str(user.tenant.id) if user.tenant else None
            request.session["is_authenticated"] = True
            request.session.save()

            tenant_payload = None
            if user.tenant:
                tenant_payload = {
                    "id": str(user.tenant.public_id),
                    "name": user.tenant.name,
                    "portal_slug": user.tenant.portal_slug,
                    "status": user.tenant.status,
                }

            professional_profile = ProfessionalProfile.objects.filter(user=user).first()
            profile_payload = {
                "id": user.id,
                "public_id": str(user.public_id),
                "first_name": professional_profile.first_name if professional_profile else "",
                "last_name": professional_profile.last_name if professional_profile else "",
            }

            return Response(
                {
                    "status": "success",
                    "tenant": tenant_payload,
                    "role": [role.name for role in user.role.all()],
                    "is_candidate": user.is_candidate,
                    "is_mentor": user.is_mentor,
                    "user": profile_payload,
                },
                status=status.HTTP_200_OK,
            )



