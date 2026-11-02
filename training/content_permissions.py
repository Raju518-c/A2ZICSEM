"""Server-side scoped authorization; call from EVERY content CRUD endpoint.
This is an assignment constraint, not a replacement for your role permission system.
"""
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import ContentAssignment

ACTION_FIELDS = {'create':'can_create', 'update':'can_edit', 'delete':'can_edit', 'submit':'can_submit', 'read':'can_create'}

def require_content_access(user, content_type, action, *, industry_ids=(), scope_ids=(), scope_industry_ids=None, role_allowed=False):
    if not getattr(user, 'is_authenticated', False):
        raise PermissionDenied('Authentication required.')
    if not role_allowed:
        raise PermissionDenied('Your role does not permit this action.')
    field = ACTION_FIELDS.get(action)
    if not field:
        raise PermissionDenied('Unsupported action.')
    industry_ids = set(map(int, industry_ids or []))
    scope_ids = set(map(int, scope_ids or []))
    if not industry_ids and not scope_ids:
        raise PermissionDenied('Content industry/scope coverage is required.')
    qs = ContentAssignment.objects.filter(assigned_to=user, content_type=content_type,
         status='ASSIGNED', revoked_at__isnull=True, **{field:True}).prefetch_related('industries','scopes')
    covered_industries = set()
    covered_scopes = set()
    for assignment in qs:
        if assignment.target_type == 'INDUSTRY':
            covered_industries.update(assignment.industries.values_list('pk',flat=True))
        elif assignment.target_type == 'SCOPE':
            covered_scopes.update(assignment.scopes.values_list('pk',flat=True))
    # Scope-specific grants never imply access to an entire industry.
    # For industry grants, resolve scope -> industry using the real ScopeCatalog FK
    # in the calling view; pass each content scope's industry ID alongside its scope ID.
    if industry_ids and not industry_ids.issubset(covered_industries):
        raise PermissionDenied('Industry outside your assigned coverage.')
    if scope_ids:
        # Mapping {scope_id: industry_id} must be resolved from ScopeCatalog by the view.
        if scope_industry_ids is None:
            raise PermissionDenied('Scope industry mapping required for authorization.')
        for scope_id in scope_ids:
            parent_industry = scope_industry_ids.get(scope_id)
            if scope_id not in covered_scopes and (parent_industry is None or int(parent_industry) not in covered_industries):
                raise PermissionDenied('Scope outside your assigned coverage.')
    return True
