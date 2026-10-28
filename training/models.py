"""OceanStar Phase 2 training models. Add as a NEW Django app `training`.

Master content is platform-owned (no tenant FK). Tenant selections and candidate
operations are tenant-scoped. Requires existing apps accounts, professionals,
catalog, competency, experience, evidence, tenancy. See README before migrating.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

USER = 'accounts.UserTbl'
TENANT = 'tenancy.Tenant'
SCOPE = 'catalog.ScopeCatalog'
LEVEL = 'catalog.ReferenceValue'
PROFILE = 'professionals.ProfessionalProfile'
PROF_SCOPE = 'competency.ProfessionalScope'
PROJECT = 'experience.ProjectRecord'
EVIDENCE = 'evidence.EvidenceDocument'

class Stamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class TenantStamp(Stamp):
    tenant = models.ForeignKey(TENANT, on_delete=models.PROTECT)
    class Meta:
        abstract = True

class TrainingProgram(Stamp):
    """Platform-owned, versioned master program. One scope per program; duplicate for multi-scope."""
    code = models.CharField(max_length=60)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scope = models.ForeignKey(SCOPE, on_delete=models.PROTECT)
    target_qualion_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT)
    version = models.PositiveIntegerField(default=1)
    estimated_duration_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[(x,x) for x in ('DRAFT','IN_REVIEW','PUBLISHED','RETIRED')], default='DRAFT')
    created_by = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='master_training_programs')
    published_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_training_program'
        constraints = [models.UniqueConstraint(fields=['code','version'], name='p2_program_code_version')]

class TrainingModule(Stamp):
    program = models.ForeignKey(TrainingProgram, on_delete=models.PROTECT, related_name='modules')
    code = models.CharField(max_length=60)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=25, choices=[(x,x) for x in ('VIDEO','PDF','DOCUMENT','ARTICLE','EXTERNAL_LINK','PRACTICAL','SCORM')])
    content_storage_key = models.CharField(max_length=600, blank=True)
    content_url = models.URLField(blank=True)
    sequence = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(default=0)
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'phase2_training_module'
        constraints = [models.UniqueConstraint(fields=['program','code'], name='p2_module_code'),models.UniqueConstraint(fields=['program','sequence'], name='p2_module_seq')]

class QuestionBank(Stamp):
    scope = models.ForeignKey(SCOPE, on_delete=models.PROTECT)
    qualion_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT)
    question_text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[(x,x) for x in ('EASY','MEDIUM','HARD')])
    explanation = models.TextField(blank=True)
    marks = models.DecimalField(max_digits=7, decimal_places=2, default=1)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[(x,x) for x in ('DRAFT','IN_REVIEW','PUBLISHED','RETIRED')], default='DRAFT')
    created_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    class Meta:
        db_table = 'phase2_question_bank'

class QuestionOption(Stamp):
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    sequence = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField(default=False)
    class Meta:
        db_table = 'phase2_question_option'
        constraints = [models.UniqueConstraint(fields=['question','sequence'], name='p2_question_option_seq')]

class TrainingAssessment(Stamp):
    program = models.ForeignKey(TrainingProgram, on_delete=models.PROTECT, related_name='assessments')
    code = models.CharField(max_length=60)
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=30)
    passing_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=60, validators=[MinValueValidator(0),MaxValueValidator(100)])
    max_attempts = models.PositiveSmallIntegerField(default=3)
    status = models.CharField(max_length=20, choices=[(x,x) for x in ('DRAFT','PUBLISHED','RETIRED')], default='DRAFT')
    class Meta:
        db_table = 'phase2_training_assessment'
        constraints = [models.UniqueConstraint(fields=['program','code'], name='p2_assessment_program_code')]

class AssessmentQuestionConfig(Stamp):
    assessment = models.ForeignKey(TrainingAssessment, on_delete=models.CASCADE, related_name='question_configs')
    difficulty = models.CharField(max_length=10, choices=[(x,x) for x in ('EASY','MEDIUM','HARD')])
    question_count = models.PositiveIntegerField()
    marks_per_question = models.DecimalField(max_digits=7, decimal_places=2, default=1)
    class Meta:
        db_table = 'phase2_assessment_question_config'
        constraints = [models.UniqueConstraint(fields=['assessment','difficulty'], name='p2_assessment_difficulty')]

class ContentAssignment(Stamp):
    """Assigned to platform-authorized content authors, e.g. SuperAdmin mentors."""
    content_type = models.CharField(max_length=25, choices=[(x,x) for x in ('PROGRAM','QUESTION','ASSESSMENT','RULE_SET')])
    object_id = models.PositiveBigIntegerField()
    assigned_to = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='phase2_content_tasks')
    assigned_by = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='phase2_content_assignments')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='ASSIGNED')
    notes = models.TextField(blank=True)
    class Meta:
        db_table = 'phase2_content_assignment'

class ContentApproval(Stamp):
    content_type = models.CharField(max_length=25)
    object_id = models.PositiveBigIntegerField()
    reviewed_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    decision = models.CharField(max_length=20, choices=[(x,x) for x in ('APPROVED','REJECTED','RETURNED')])
    comments = models.TextField(blank=True)
    class Meta:
        db_table = 'phase2_content_approval'

class TenantTrainingProgram(TenantStamp):
    master_program = models.ForeignKey(TrainingProgram, on_delete=models.PROTECT)
    imported_version = models.PositiveIntegerField()
    imported_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    # Production: resolve immutable content through master_program version, not latest code.
    class Meta:
        db_table = 'phase2_tenant_training_program'
        constraints = [models.UniqueConstraint(fields=['tenant','master_program'], name='p2_tenant_program_unique')]

class TenantAssessment(TenantStamp):
    tenant_program = models.ForeignKey(TenantTrainingProgram, on_delete=models.PROTECT, related_name='assessments')
    master_assessment = models.ForeignKey(TrainingAssessment, on_delete=models.PROTECT)
    imported_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'phase2_tenant_assessment'
        constraints = [models.UniqueConstraint(fields=['tenant','master_assessment'], name='p2_tenant_assessment_unique')]
    def clean(self):
        if self.tenant_program_id and self.master_assessment_id and self.tenant_program.master_program_id != self.master_assessment.program_id:
            raise ValidationError('Assessment must belong to the imported program.')

class TenantContentImportHistory(TenantStamp):
    content_type = models.CharField(max_length=30)
    master_object_id = models.PositiveBigIntegerField()
    version = models.PositiveIntegerField()
    imported_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    imported_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_tenant_content_import_history'

class CandidateTraining(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT, related_name='phase2_training')
    tenant_program = models.ForeignKey(TenantTrainingProgram, on_delete=models.PROTECT)
    assigned_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='ASSIGNED')
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0),MaxValueValidator(100)])
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_candidate_training'

class CandidateModuleProgress(TenantStamp):
    candidate_training = models.ForeignKey(CandidateTraining, on_delete=models.PROTECT, related_name='module_progress')
    module = models.ForeignKey(TrainingModule, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='NOT_STARTED')
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_candidate_module_progress'
        constraints = [models.UniqueConstraint(fields=['candidate_training','module'], name='p2_module_progress_unique')]

class TrainingStaffAssignment(TenantStamp):
    candidate_training = models.ForeignKey(CandidateTraining, on_delete=models.PROTECT, related_name='staff_assignments')
    mentor = models.ForeignKey(PROFILE, on_delete=models.PROTECT)
    assignment_type = models.CharField(max_length=20, choices=[(x,x) for x in ('MENTOR','SUPERVISOR','ASSESSOR')])
    assigned_by = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='phase2_staff_assignments')
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='ACTIVE')
    class Meta:
        db_table = 'phase2_training_staff_assignment'

class CandidateAssessmentAssignment(TenantStamp):
    candidate_training = models.ForeignKey(CandidateTraining, on_delete=models.PROTECT)
    tenant_assessment = models.ForeignKey(TenantAssessment, on_delete=models.PROTECT)
    assigned_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='ASSIGNED')
    class Meta:
        db_table = 'phase2_candidate_assessment_assignment'

class TrainingAssessmentAttempt(TenantStamp):
    assignment = models.ForeignKey(CandidateAssessmentAssignment, on_delete=models.PROTECT, related_name='attempts')
    attempt_number = models.PositiveSmallIntegerField()
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    marks_awarded = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='IN_PROGRESS')
    class Meta:
        db_table = 'phase2_assessment_attempt'
        constraints = [models.UniqueConstraint(fields=['assignment','attempt_number'], name='p2_attempt_number_unique')]

class AttemptQuestion(TenantStamp):
    attempt = models.ForeignKey(TrainingAssessmentAttempt, on_delete=models.PROTECT, related_name='selected_questions')
    question = models.ForeignKey(QuestionBank, on_delete=models.PROTECT)
    sequence = models.PositiveIntegerField()
    question_snapshot = models.JSONField(default=dict)  # frozen question, options, correct answer (server-only)
    marks = models.DecimalField(max_digits=7, decimal_places=2)
    class Meta:
        db_table = 'phase2_attempt_question'
        constraints = [models.UniqueConstraint(fields=['attempt','question'], name='p2_attempt_question_unique'),models.UniqueConstraint(fields=['attempt','sequence'], name='p2_attempt_question_seq')]

class TrainingAssessmentResponse(TenantStamp):
    attempt_question = models.OneToOneField(AttemptQuestion, on_delete=models.PROTECT, related_name='response')
    selected_answer = models.JSONField(default=list)
    is_correct = models.BooleanField(null=True, blank=True)
    marks_awarded = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    answered_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_assessment_response'

class CompetencyParameter(Stamp):
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=150)
    data_type = models.CharField(max_length=20, choices=[(x,x) for x in ('NUMBER','BOOLEAN','TEXT','DATE','REFERENCE')])
    min_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    source_type = models.CharField(max_length=30, default='MENTOR_VERIFIED')
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'phase2_competency_parameter'

class ProfessionalScopeParameter(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT, related_name='phase2_parameters')
    parameter = models.ForeignKey(CompetencyParameter, on_delete=models.PROTECT)
    value = models.JSONField(null=True, blank=True)
    updated_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    verified_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_professional_scope_parameter'
        constraints = [models.UniqueConstraint(fields=['professional_scope','parameter'], name='p2_scope_parameter_unique')]

class CompetencyScoreHistory(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    parameter = models.ForeignKey(CompetencyParameter, on_delete=models.PROTECT)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    updated_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    source_reference = models.CharField(max_length=120, blank=True)
    reason = models.TextField(blank=True)
    class Meta:
        db_table = 'phase2_competency_score_history'

class DigitalLogbook(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    project_record = models.ForeignKey(PROJECT, on_delete=models.PROTECT, related_name='phase2_logbook_entries')
    candidate_training = models.ForeignKey(CandidateTraining, on_delete=models.PROTECT, null=True, blank=True)
    activity_date = models.DateField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    hours_spent = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='DRAFT')
    submitted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_digital_logbook'

class DigitalLogbookEvidence(TenantStamp):
    logbook = models.ForeignKey(DigitalLogbook, on_delete=models.PROTECT, related_name='evidence_items')
    evidence_document = models.ForeignKey(EVIDENCE, on_delete=models.PROTECT)
    evidence_type = models.CharField(max_length=15, choices=[(x,x) for x in ('DOCUMENT','IMAGE','VIDEO')])
    uploaded_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_logbook_evidence'
        constraints = [models.UniqueConstraint(fields=['logbook','evidence_document'], name='p2_logbook_evidence_unique')]

class DigitalLogbookReview(TenantStamp):
    logbook = models.ForeignKey(DigitalLogbook, on_delete=models.PROTECT, related_name='reviews')
    mentor = models.ForeignKey(USER, on_delete=models.PROTECT)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(100)])
    verification_status = models.CharField(max_length=20, choices=[(x,x) for x in ('VERIFIED','RETURNED','REJECTED')])
    comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_logbook_review'

class ClientPerformanceReview(TenantStamp):
    client = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='phase2_client_reviews')
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    project_record = models.ForeignKey(PROJECT, on_delete=models.PROTECT, null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0),MaxValueValidator(100)])
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_client_performance_review'

class ComplianceReview(TenantStamp):
    client_review = models.ForeignKey(ClientPerformanceReview, on_delete=models.PROTECT, related_name='mentor_reviews')
    mentor = models.ForeignKey(USER, on_delete=models.PROTECT)
    verified_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0),MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=[(x,x) for x in ('VERIFIED','REJECTED','RETURNED')])
    comments = models.TextField(blank=True)
    class Meta:
        db_table = 'phase2_compliance_review'

class ComplianceScoreHistory(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    compliance_review = models.ForeignKey(ComplianceReview, on_delete=models.PROTECT, null=True, blank=True)
    previous_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_score = models.DecimalField(max_digits=5, decimal_places=2)
    reviewed_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    class Meta:
        db_table = 'phase2_compliance_score_history'

class PromotionEligibilityResult(TenantStamp):
    """rule_selection_id references existing governance tenant selection via an integer until integrated."""
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    rule_selection = models.ForeignKey("governance.TenantRuleSelection", on_delete=models.PROTECT, related_name="training_eligibility_results")
    eligible = models.BooleanField(default=False)
    proposed_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT, null=True, blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    scores_snapshot = models.JSONField(default=dict)
    class Meta:
        db_table = 'phase2_promotion_eligibility_result'

class PromotionEligibilityDetail(TenantStamp):
    result = models.ForeignKey(PromotionEligibilityResult, on_delete=models.PROTECT, related_name='details')
    condition_code = models.CharField(max_length=100)
    actual_value = models.JSONField(null=True, blank=True)
    required_value = models.JSONField(null=True, blank=True)
    passed = models.BooleanField()
    class Meta:
        db_table = 'phase2_promotion_eligibility_detail'

class TrainingPromotionRecommendation(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    eligibility_result = models.ForeignKey(PromotionEligibilityResult, on_delete=models.PROTECT)
    from_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT, related_name='phase2_recommendations_from')
    to_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT, related_name='phase2_recommendations_to')
    mentor = models.ForeignKey(USER, on_delete=models.PROTECT)
    status = models.CharField(max_length=25, default='SUBMITTED')
    comments = models.TextField(blank=True)
    recommended_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_promotion_recommendation'

class PromotionDecision(TenantStamp):
    recommendation = models.OneToOneField(TrainingPromotionRecommendation, on_delete=models.PROTECT, related_name='decision')
    tenant_admin = models.ForeignKey(USER, on_delete=models.PROTECT)
    decision = models.CharField(max_length=20, choices=[(x,x) for x in ('APPROVED','REJECTED','RETURNED')])
    reason = models.TextField(blank=True)
    decided_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_promotion_decision'

class PromotionHistory(TenantStamp):
    professional_scope = models.ForeignKey(PROF_SCOPE, on_delete=models.PROTECT)
    decision = models.OneToOneField(PromotionDecision, on_delete=models.PROTECT)
    from_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT, related_name='phase2_promotions_from')
    to_level = models.ForeignKey(LEVEL, on_delete=models.PROTECT, related_name='phase2_promotions_to')
    approved_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    effective_at = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'phase2_promotion_history'

class WorkflowTicket(TenantStamp):
    ticket_no = models.CharField(max_length=50)
    request_type = models.CharField(max_length=50)
    raised_by = models.ForeignKey(USER, on_delete=models.PROTECT, related_name='phase2_tickets_raised')
    assigned_to = models.ForeignKey(USER, on_delete=models.PROTECT, null=True, blank=True, related_name='phase2_tickets_assigned')
    candidate = models.ForeignKey(PROFILE, on_delete=models.PROTECT, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=15, default='NORMAL')
    status = models.CharField(max_length=20, default='OPEN')
    closed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'phase2_workflow_ticket'
        constraints = [models.UniqueConstraint(fields=['tenant','ticket_no'], name='p2_ticket_no_tenant_unique')]

class WorkflowTicketMessage(TenantStamp):
    ticket = models.ForeignKey(WorkflowTicket, on_delete=models.PROTECT, related_name='messages')
    sender = models.ForeignKey(USER, on_delete=models.PROTECT)
    message = models.TextField()
    is_internal = models.BooleanField(default=False)
    class Meta:
        db_table = 'phase2_workflow_ticket_message'

class WorkflowTicketAttachment(TenantStamp):
    ticket = models.ForeignKey(WorkflowTicket, on_delete=models.PROTECT, related_name='attachments')
    message = models.ForeignKey(WorkflowTicketMessage, on_delete=models.PROTECT, null=True, blank=True)
    evidence_document = models.ForeignKey(EVIDENCE, on_delete=models.PROTECT)
    class Meta:
        db_table = 'phase2_workflow_ticket_attachment'

class WorkflowTicketAction(TenantStamp):
    ticket = models.ForeignKey(WorkflowTicket, on_delete=models.PROTECT, related_name='actions')
    action_by = models.ForeignKey(USER, on_delete=models.PROTECT)
    action = models.CharField(max_length=40)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    comments = models.TextField(blank=True)
    class Meta:
        db_table = 'phase2_workflow_ticket_action'


class ProfessionalScopeScoreSnapshot(TenantStamp):
    """One consolidated promotion-parameter snapshot per ProfessionalScope.

    Does not replace existing ProfessionalScope calculated fields. Use a verified
    service to synchronize those fields and this snapshot atomically.
    """
    professional_scope = models.OneToOneField(PROF_SCOPE, on_delete=models.PROTECT, related_name='phase2_score_snapshot')
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    verified_logbook_count = models.PositiveIntegerField(default=0)
    logbook_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    assessment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_verified_at = models.DateTimeField(null=True, blank=True)
    last_verified_by = models.ForeignKey(USER, on_delete=models.PROTECT, null=True, blank=True)
    class Meta:
        db_table = 'phase2_professional_scope_score_snapshot'
