# A2Z_ICSEM

Django backend for the QUALION platform — a shared-database, shared-schema
multi-tenant system for professional competency management, built against
the `QUALION_Updated_Django_Backend_Database_Architecture` (v1.0, 30 Jul 2026).

## Stack

- Python 3.13+, Django 5.x, Django REST Framework
- PostgreSQL (psycopg 3) for staging/production; SQLite available for
  zero-setup local development (`DATABASE_ENGINE` in `.env`)
- JWT auth via `djangorestframework-simplejwt`
- API docs via `drf-spectacular`

## Apps

| App | Models |
|---|---|
| `core` | Reusable abstract base models / managers / validators — no tables |
| `tenancy` | Tenant, TenantOperation, Organization |
| `accounts` | User, RegistrationApplication, ConsentRecord |
| `professionals` | ProfessionalProfile, ProfessionalReview, CredentialRecord, CapabilityRecord, ContactRecord |
| `catalog` | ReferenceValue, ScopeCatalog, FormModule, ScopeModule, FormField |
| `experience` | EmploymentRecord, ProjectRecord, ProjectScope, ScopeResponse, ExposureLog, ProfessionalAssignment |
| `evidence` | EvidenceDocument |
| `competency` | ProfessionalScope, CompetencyAssessment |
| `resumes` | ResumeTemplate, ResumeGeneration |
| `governance` | AuditEvent |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`.env.example` defaults `DATABASE_ENGINE=sqlite`, so the steps above work
with no database server installed — `db.sqlite3` is created next to
`manage.py`. To point at PostgreSQL instead, set `DATABASE_ENGINE=postgresql`
and fill in the `POSTGRES_*` values before running `migrate`.
