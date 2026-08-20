from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from accounts.models import UserTbl

from .models import (
    CapabilityRecord,
    ContactRecord,
    CredentialRecord,
    ProfessionalProfile,
    ProfessionalReview,
)
from .serializers import (
    CapabilityRecordSerializer,
    ContactRecordSerializer,
    CredentialRecordSerializer,
    ProfessionalProfileSerializer,
    ProfessionalReviewSerializer,
    CombinedCredentialRecordSerializer,
    Stage2SubmitSerializer,
    ProfessionalReviewDecisionSerializer,
    ProfessionalReviewResubmitSerializer,
)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalProfileListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        profiles = ProfessionalProfile.objects.all().order_by("-created_at")
        serializer = ProfessionalProfileSerializer(profiles, many=True)
        return Response(
            {"success": True, "message": "Professional profiles fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ProfessionalProfileSerializer)
    def post(self, request):
        serializer = ProfessionalProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Professional profile created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalProfileRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProfessionalProfile.objects.get(pk=pk)
        except ProfessionalProfile.DoesNotExist:
            return None

    def get(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalProfileSerializer(profile)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ProfessionalProfileSerializer)
    def put(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Professional profile updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)
        profile.delete()
        return Response({"success": True, "message": "Professional profile deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = ProfessionalReview.objects.all().order_by("-created_at")
        serializer = ProfessionalReviewSerializer(reviews, many=True)
        return Response(
            {"success": True, "message": "Professional reviews fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ProfessionalReviewSerializer)
    def post(self, request):
        serializer = ProfessionalReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Professional review created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ProfessionalReview.objects.get(pk=pk)
        except ProfessionalReview.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalReviewSerializer(review)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ProfessionalReviewSerializer)
    def put(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionalReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Professional review updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"success": False, "message": "Professional review not found."}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"success": True, "message": "Professional review deleted successfully."}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class Stage2SubmitAPIView(APIView):
    """
    POST : Candidate submits Stage 2 for review, via the standalone
    "Submit for Review" button — never triggered by any individual
    section's save.

    Validates all required sections are complete before creating
    anything. If incomplete, returns which sections are missing so
    frontend can route the candidate back to the right one, instead of
    a generic error.

    On success: creates one ProfessionalReview row (review_type=
    PROFILE_APPROVAL, decision=PENDING), and moves
    ProfessionalProfile.profile_status to STAGE2_SUBMITTED (added to
    ProfileStatus for this — distinct from the pre-existing, still-
    unused generic SUBMITTED value, and from Stage 1's own SUBMITTED on
    RegistrationApplication.status, a different field entirely). No fields
    are accepted from the request body — profile_version,
    previous_classification and submitted_by are all read/derived
    server-side, matching how RegistrationApplicationDecisionAPIView
    never trusts frontend for values that already exist on the row
    being acted on. submitted_by is the profile's own owner
    (professional.user) rather than request.user — this app's auth
    isn't wired to UserTbl yet (AUTH_USER_MODEL still points elsewhere),
    and ProfessionalReview.submitted_by is a required FK to UserTbl, so
    request.user could never satisfy it anyway; the profile owner is
    also the only correct submitter here regardless.

    Blocked once profile_status is already STAGE2_SUBMITTED, APPROVED,
    or REJECTED — resubmission after RETURNED goes through a separate
    Stage2ResubmitAPIView instead (creates a new ProfessionalReview row,
    per its append-only design — not built here).

    STAGE2_INCOMPLETE is deliberately left out of the allowed-starting-
    states below: nothing in this codebase sets that value yet, so the
    only real starting states in practice are STAGE1_COMPLETE and
    RETURNED. Add it back in once something actually writes it.

    Metrics recalculation (calendar experience, verified field days,
    Qualion level, etc.) is intentionally NOT called here — that
    calculation engine doesn't exist yet anywhere in this codebase
    (confirmed: no recalculate_professional_metrics or equivalent).
    Wire it in here, before the ProfessionalReview is created, once it's
    built.
    """

    permission_classes = [AllowAny]
    serializer_class = Stage2SubmitSerializer

    def _check_required_sections(self, professional):
        missing = []

        # A candidate who declared zero prior experience at Stage 1 (a
        # fresher/graduate) can legitimately have no EmploymentRecord or
        # ProjectRecord — the platform's own L0 "Aspirant/Graduate" level
        # is evidenced by identity + education alone, never by employment
        # history. initial_experience_band exists on ProfessionalProfile
        # precisely "for initial routing" (its own help_text) — this is
        # that routing. Only an explicit NONE waives the two checks;
        # leaving the field blank still requires them, so this only
        # relaxes the gate for candidates who actually said "no experience
        # yet," not for anyone who simply skipped the question.
        is_fresher = professional.initial_experience_band == ProfessionalProfile.ExperienceBand.NONE

        if not professional.credentials.filter(record_type="EDUCATION").exists():
            missing.append("education")
        if not is_fresher and not professional.employment_records.exists():
            missing.append("employment")
        if not is_fresher and not professional.project_records.exists():
            missing.append("project_experience")
        if not professional.capabilities.filter(capability_type="LANGUAGE").exists():
            missing.append("languages")
        if not professional.availability_status:
            missing.append("availability")
        if not professional.consent_records.filter(
            consent_type__in=["PROFILE_ACCURACY", "CONFLICT_OF_INTEREST"],
            is_granted=True,
        ).count() >= 2:
            missing.append("declarations")

        return {"ok": not missing, "missing": missing}

    @extend_schema(request=Stage2SubmitSerializer)
    def post(self, request, prof_id):
        try:
            professional = ProfessionalProfile.objects.select_related("tenant", "user").get(pk=prof_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if professional.profile_status not in (
            ProfessionalProfile.ProfileStatus.STAGE1_COMPLETE,
            ProfessionalProfile.ProfileStatus.RETURNED,
        ):
            return Response(
                {
                    "success": False,
                    "message": f"Cannot submit Stage 2 from status={professional.profile_status}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        completeness = self._check_required_sections(professional)
        if not completeness["ok"]:
            return Response(
                {
                    "success": False,
                    "message": "Stage 2 incomplete.",
                    "missing_sections": completeness["missing"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        with transaction.atomic():
            review = ProfessionalReview.objects.create(
                tenant=professional.tenant,
                professional=professional,
                review_type=ProfessionalReview.ReviewType.PROFILE_APPROVAL,
                profile_version=professional.profile_version,
                submitted_by=professional.user,
                submitted_at=now,
                previous_classification=professional.current_classification,
            )

            professional.profile_status = ProfessionalProfile.ProfileStatus.STAGE2_SUBMITTED
            professional.save(update_fields=["profile_status", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Stage 2 submitted for review.",
                "data": {
                    "review_id": review.id,
                    "profile_status": professional.profile_status,
                    "submitted_at": review.submitted_at,
                },
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewDecisionAPIView(APIView):
    """
    POST : Reviewer approves, rejects, or returns a submitted
    ProfessionalReview (Stage 2 profile approval + classification,
    decided together per the DB constraint).

    Approving is the ONE action that finally flips UserTbl.approval_status
    to APPROVED — Stage 1 deliberately leaves it PENDING_APPROVAL, so this
    is where the account becomes fully active. final_classification is
    required and is copied onto ProfessionalProfile.current_classification.
    Approving also confirms classification on the profile itself
    (classification_status -> CONFIRMED, classified_by/classified_at set)
    — this decision IS the classification confirmation the profile fields
    exist to record; leaving them at NOT_ASSESSED after a real decision
    was made would be a stale, misleading state. classified_by is left
    NULL when reviewed_by wasn't resolvable, same as reviewed_by itself.

    Rejecting is terminal for this review: UserTbl.approval_status =
    REJECTED, but is_active is left untouched, same as Stage 1's reject
    branch — a rejected candidate can still log in.

    Returning requires a reason. profile_status = RETURNED so the
    candidate can correct and resubmit via ProfessionalReviewResubmitAPIView
    — UserTbl.approval_status stays PENDING_APPROVAL, untouched, same
    pattern as Stage 1's return branch.

    Blocked once decision is no longer PENDING — covers APPROVED/REJECTED
    (terminal) and RETURNED (that specific review row is done; a decision
    on the corrected content happens on the NEW row a resubmit creates,
    never by re-deciding this one).
    """

    permission_classes = [AllowAny]
    serializer_class = ProfessionalReviewDecisionSerializer

    def _resolve_reviewer(self, value):
        if not value:
            return None
        value = str(value).strip()
        if not value:
            return None
        for lookup in ("public_id", "id"):
            try:
                return UserTbl.objects.get(**{lookup: value})
            except (UserTbl.DoesNotExist, ValueError, ValidationError):
                continue
        return None

    @extend_schema(request=ProfessionalReviewDecisionSerializer)
    def post(self, request, professional_id):
        review = ProfessionalReview.objects.select_related(
            "professional", "professional__user"
        ).filter(
            professional_id=professional_id,
            review_type=ProfessionalReview.ReviewType.PROFILE_APPROVAL,
            decision=ProfessionalReview.Decision.PENDING,
        ).order_by("-created_at").first()
        if review is None:
            return Response(
                {"success": False, "message": "No pending professional review found for this profile."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.validated_data["decision"]
        final_classification = serializer.validated_data.get("final_classification", "")
        reason = serializer.validated_data.get("reason", "")
        reviewer_notes = serializer.validated_data.get("reviewer_notes", "")
        reviewed_by = self._resolve_reviewer(serializer.validated_data.get("reviewed_by"))

        if review.decision != ProfessionalReview.Decision.PENDING:
            return Response(
                {
                    "success": False,
                    "message": f"Review is not pending decision (decision={review.decision}).",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision_verbs = {"REJECTED": "reject", "RETURNED": "return"}
        if decision in decision_verbs and not reason:
            return Response(
                {"success": False, "message": f"A reason is required to {decision_verbs[decision]} a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if decision == "APPROVED" and not final_classification:
            return Response(
                {"success": False, "message": "final_classification is required to approve."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        professional = review.professional
        user = professional.user

        with transaction.atomic():
            review.reviewed_by = reviewed_by
            review.reviewer_notes = reviewer_notes
            review.decided_at = now

            if decision == "APPROVED":
                review.decision = ProfessionalReview.Decision.APPROVED
                review.final_classification = final_classification
                review.save(update_fields=[
                    "decision", "final_classification", "reviewed_by",
                    "reviewer_notes", "decided_at",
                ])

                professional.profile_status = ProfessionalProfile.ProfileStatus.APPROVED
                professional.current_classification = final_classification
                professional.classification_status = ProfessionalProfile.ClassificationStatus.CONFIRMED
                professional.classified_by = reviewed_by
                professional.classified_at = now
                professional.save(update_fields=[
                    "profile_status", "current_classification", "classification_status",
                    "classified_by", "classified_at", "updated_at",
                ])

                # chk_user_approved_at_required_when_approved requires
                # approved_at whenever approval_status=APPROVED — must be
                # set together, in the same save, or the DB rejects it.
                user.approval_status = UserTbl.ApprovalStatus.APPROVED
                user.approved_by = reviewed_by
                user.approved_at = now
                user.save(update_fields=["approval_status", "approved_by", "approved_at", "updated_at"])

            elif decision == "RETURNED":
                review.decision = ProfessionalReview.Decision.RETURNED
                review.decision_reason = reason
                review.save(update_fields=[
                    "decision", "decision_reason", "reviewed_by",
                    "reviewer_notes", "decided_at",
                ])

                professional.profile_status = ProfessionalProfile.ProfileStatus.RETURNED
                professional.save(update_fields=["profile_status", "updated_at"])

            else:  # REJECTED
                review.decision = ProfessionalReview.Decision.REJECTED
                review.decision_reason = reason
                review.save(update_fields=[
                    "decision", "decision_reason", "reviewed_by",
                    "reviewer_notes", "decided_at",
                ])

                professional.profile_status = ProfessionalProfile.ProfileStatus.REJECTED
                professional.save(update_fields=["profile_status", "updated_at"])

                user.approval_status = UserTbl.ApprovalStatus.REJECTED
                user.rejection_reason = reason
                user.save(update_fields=[
                    "approval_status", "rejection_reason", "updated_at",
                ])

        return Response(
            {
                "success": True,
                "message": f"Professional review {decision.lower()}.",
                "data": {
                    "review_id": review.id,
                    "decision": review.decision,
                    "profile_status": professional.profile_status,
                    "user_approval_status": user.approval_status,
                    "user_is_active": user.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalReviewResubmitAPIView(APIView):
    """
    POST : Candidate resubmits Stage 2 after a RETURNED decision.

    Allowed only when profile_status=RETURNED. Unlike Stage 1's resubmit
    (which mutates the same RegistrationApplication row in place),
    ProfessionalReview is append-only — this creates a NEW row rather
    than editing the returned one, preserving the original decision,
    reason and criteria_snapshot as permanent history. (ProfessionalReview
    has no updated_at field at all — that absence is the model's own
    signal that rows are never meant to be edited after creation.)

    profile_version is incremented first so the new review is tagged
    against the corrected version, not the one that was returned.

    submitted_by is the profile's own owner (professional.user), not
    request.user — same reasoning as Stage2SubmitAPIView: this app's
    auth isn't wired to UserTbl yet, and submitted_by is a required FK
    to UserTbl that request.user could never satisfy.

    Metrics recalculation is intentionally NOT called here, same as
    Stage2SubmitAPIView — that calculation engine doesn't exist yet.
    """

    permission_classes = [AllowAny]
    serializer_class = ProfessionalReviewResubmitSerializer

    def post(self, request, prof_id):
        try:
            professional = ProfessionalProfile.objects.select_related("tenant", "user").get(pk=prof_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if professional.profile_status != ProfessionalProfile.ProfileStatus.RETURNED:
            return Response(
                {
                    "success": False,
                    "message": f"Cannot resubmit from status={professional.profile_status}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        completeness = Stage2SubmitAPIView()._check_required_sections(professional)
        if not completeness["ok"]:
            return Response(
                {
                    "success": False,
                    "message": "Stage 2 still incomplete.",
                    "missing_sections": completeness["missing"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        with transaction.atomic():
            professional.profile_version += 1
            professional.profile_status = ProfessionalProfile.ProfileStatus.STAGE2_SUBMITTED
            professional.save(update_fields=["profile_version", "profile_status", "updated_at"])

            review = ProfessionalReview.objects.create(
                tenant=professional.tenant,
                professional=professional,
                review_type=ProfessionalReview.ReviewType.PROFILE_APPROVAL,
                profile_version=professional.profile_version,
                submitted_by=professional.user,
                submitted_at=now,
                previous_classification=professional.current_classification,
            )

        return Response(
            {
                "success": True,
                "message": "Stage 2 resubmitted for review.",
                "data": {
                    "review_id": review.id,
                    "profile_version": professional.profile_version,
                    "profile_status": professional.profile_status,
                },
            },
            status=status.HTTP_200_OK,
        )


class ProfessionalReviewStatusAPIView(APIView):
    """
    GET : Lightweight Stage 2 status summary, mirroring
    RegistrationStatusAPIView. Returns the latest ProfessionalReview's
    decision (if any) plus profile_status, so frontend doesn't need to
    query ProfessionalReview directly or walk its append-only history
    itself.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, prof_id):
        try:
            professional = ProfessionalProfile.objects.select_related("user").get(pk=prof_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        latest_review = professional.reviews.filter(
            review_type=ProfessionalReview.ReviewType.PROFILE_APPROVAL
        ).order_by("-created_at").first()

        return Response(
            {
                "success": True,
                "message": "Stage 2 status fetched successfully.",
                "data": {
                    "profile_status": professional.profile_status,
                    "user_approval_status": professional.user.approval_status,
                    "current_classification": professional.current_classification,
                    "latest_review_decision": latest_review.decision if latest_review else None,
                    "latest_review_reason": latest_review.decision_reason if latest_review else None,
                    "latest_review_version": latest_review.profile_version if latest_review else None,
                },
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class CredentialRecordListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        credentials = CredentialRecord.objects.all().order_by("-created_at")
        serializer = CredentialRecordSerializer(credentials, many=True)
        return Response(
            {"success": True, "message": "Credential records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=CredentialRecordSerializer)
    def post(self, request):
        serializer = CredentialRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Credential record created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CredentialRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CredentialRecord.objects.get(pk=pk)
        except CredentialRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CredentialRecordSerializer(credential)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=CredentialRecordSerializer)
    def put(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CredentialRecordSerializer(credential, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Credential record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        credential = self.get_object(pk)
        if not credential:
            return Response({"success": False, "message": "Credential record not found."}, status=status.HTTP_404_NOT_FOUND)
        credential.delete()
        return Response({"success": True, "message": "Credential record deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CapabilityRecordListCreateAPIView(APIView):
    """
    GET  : Get all capability records. Optional ?professional=<id> filters
    to one professional's records.
    POST : Create capability records in bulk. Body: {"professional_id": X,
    "records": [ {...}, {...} ]}. professional_id is applied to every
    record; tenant is derived from the professional's own tenant and must
    not be sent. Saved atomically — if any record is invalid, none are
    created.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        capabilities = CapabilityRecord.objects.all().order_by("-created_at")

        professional_id = request.query_params.get("professional")
        if professional_id:
            try:
                professional_id = int(professional_id)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "message": "professional query parameter must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            capabilities = capabilities.filter(professional_id=professional_id)

        serializer = CapabilityRecordSerializer(capabilities, many=True)
        return Response(
            {"success": True, "message": "Capability records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=CapabilityRecordSerializer(many=True))
    def post(self, request):
        professional_id = request.data.get("professional_id")
        records = request.data.get("records")

        if not professional_id or not isinstance(records, list):
            return Response(
                {
                    "success": False,
                    "message": "professional_id and records (list) are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional_id = int(professional_id)
        except (TypeError, ValueError):
            return Response(
                {"success": False, "message": "professional_id must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            professional = ProfessionalProfile.objects.get(id=professional_id)
        except ProfessionalProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Professional not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        for record in records:
            record["professional"] = professional_id
            record["tenant"] = professional.tenant_id

        serializer = CapabilityRecordSerializer(data=records, many=True)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(
                {"success": True, "message": "Capability records created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CapabilityRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CapabilityRecord.objects.get(pk=pk)
        except CapabilityRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CapabilityRecordSerializer(capability)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=CapabilityRecordSerializer)
    def put(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        professional_id = data.get("professional")
        if professional_id:
            try:
                professional_id = int(professional_id)
            except (TypeError, ValueError):
                return Response(
                    {"success": False, "message": "professional must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                professional = ProfessionalProfile.objects.get(id=professional_id)
            except ProfessionalProfile.DoesNotExist:
                return Response({"success": False, "message": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
            if hasattr(data, "_mutable"):
                data._mutable = True
            data["tenant"] = professional.tenant_id

        serializer = CapabilityRecordSerializer(capability, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Capability record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        capability = self.get_object(pk)
        if not capability:
            return Response({"success": False, "message": "Capability record not found."}, status=status.HTTP_404_NOT_FOUND)
        capability.delete()
        return Response({"success": True, "message": "Capability record deleted successfully."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ContactRecordListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        contacts = ContactRecord.objects.all().order_by("-created_at")
        serializer = ContactRecordSerializer(contacts, many=True)
        return Response(
            {"success": True, "message": "Contact records fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(request=ContactRecordSerializer(many=True))
    def post(self, request):
        many = isinstance(request.data, list)
        items = request.data if many else [request.data]

        created = []
        failed = []
        for index, item in enumerate(items):
            serializer = ContactRecordSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                failed.append({"index": index, "errors": serializer.errors})

        if not many:
            if created:
                return Response(
                    {"success": True, "message": "Contact record created successfully.", "data": created[0]},
                    status=status.HTTP_201_CREATED,
                )
            return Response({"success": False, "errors": failed[0]["errors"]}, status=status.HTTP_400_BAD_REQUEST)

        status_code = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response(
            {
                "success": bool(created),
                "message": f"{len(created)} of {len(items)} contact record(s) created successfully.",
                "data": created,
                "errors": failed,
            },
            status=status_code,
        )

@method_decorator(csrf_exempt, name='dispatch')
class ContactRecordRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ContactRecord.objects.get(pk=pk)
        except ContactRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactRecordSerializer(contact)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    @extend_schema(request=ContactRecordSerializer)
    def put(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactRecordSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Contact record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({"success": False, "message": "Contact record not found."}, status=status.HTTP_404_NOT_FOUND)
        contact.delete()
        return Response({"success": True, "message": "Contact record deleted successfully."}, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name="dispatch")
class CombinedCredentialRecordAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=CombinedCredentialRecordSerializer(many=True),
        responses={201: CombinedCredentialRecordSerializer(many=True)},
        description="Create multiple Credential Records with multiple Credential Record Items."
    )
    def post(self, request):

        serializer = CombinedCredentialRecordSerializer(
            data=request.data,
            many=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    @extend_schema(
        request=CombinedCredentialRecordSerializer,
        responses={200: CombinedCredentialRecordSerializer},
        description="Update Credential Record and Credential Record Items."
    )
    def put(self, request, pk):

        credential = get_object_or_404(
            CredentialRecord,
            pk=pk
        )

        serializer = CombinedCredentialRecordSerializer(
            credential,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProfessionalCredentialListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, professional_id):
        credentials = CredentialRecord.objects.filter(
            professional_id=professional_id
        ).prefetch_related("items")

        serializer = CredentialRecordSerializer(credentials, many=True)

        return Response(
            {
                "success": True,
                "count": credentials.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )