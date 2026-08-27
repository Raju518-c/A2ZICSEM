"""
Django settings for the A2Z_ICSEM (QUALION) project.

Architecture: shared database, shared schema, multi-tenant.
Source of truth: QUALION_Updated_Django_Backend_Database_Architecture (v1.0, 30 Jul 2026).
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(key, default=""):
    value = os.environ.get(key, default)
    return [item.strip() for item in value.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------

SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-development-key-change-me")
# DEBUG = env_bool("DJANGO_DEBUG", False)
DEBUG = True

ALLOWED_HOSTS = [
    "145.79.0.94",
    "localhost",
    "127.0.0.1",
    ".localhost",
    "qualion.com",
    ".qualion.com",
    "145.79.0.94:83",
    "145.79.0.94:81",
]

CSRF_TRUSTED_ORIGINS = [
    "http://145.79.0.94:82",
    "http://localhost:3000",
    "http://*.localhost:3000",
    "http://localhost:5173",
    "http://*.localhost:5173",
    "http://qualion.com",
    "https://qualion.com",
    "https://*.qualion.com",
    "http://145.79.0.94:83",
    "http://145.79.0.94:81",
]


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",    
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "core",
    "tenancy",
    "accounts",
    "professionals",
    "catalog",
    "experience",
    "evidence",
    "competency",
    "resumes",
    "governance",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
#
# Production/staging target: PostgreSQL (shared database, shared schema,
# tenant_id per row — see architecture doc). SQLite is offered purely as a
# zero-setup local development option; switch with DATABASE_ENGINE in .env.
# ---------------------------------------------------------------------------
# DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite")

# if DATABASE_ENGINE == "mysql":
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.mysql",
#             "NAME": "a2znewpython",
#             "USER": "root",
#             "PASSWORD": "Root@1234",
#             "HOST": "localhost",
#             "PORT": "3306",
#             "OPTIONS": {
#                 "charset": "utf8mb4",
#             },
#         }
#     }
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": BASE_DIR / "db.sqlite3",
#         }
#     }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "a2znewpython",
        "USER": "root",
        "PASSWORD": "Root@1234",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

LOGIN_URL = "/admin/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

# AUTH_USER_MODEL = "accounts.User"
# SILENCED_SYSTEM_CHECKS = ["auth.E003"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / media files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Field-level encryption (restricted PII / credential secure_details)
# ---------------------------------------------------------------------------

FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", "")

# ---------------------------------------------------------------------------
# Email (OTP delivery, notifications)
# ---------------------------------------------------------------------------
# Defaults to the console backend in DEBUG so OTP emails are visible in the
# runserver output with zero setup. Set real values in .env — never hardcode
# credentials here. EMAIL_HOST_PASSWORD is a Gmail App Password, not the
# account password (Gmail SMTP requires 2FA + an App Password).

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(env("EMAIL_PORT", 587))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@qualion.local")

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT": "iso-8601",
}

# ---------------------------------------------------------------------------
# Simple JWT
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(env("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 30))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(env("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY") or SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "public_id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
}

# ---------------------------------------------------------------------------
# drf-spectacular (Swagger / ReDoc)
# ---------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "QUALION API (A2Z_ICSEM)",
    "DESCRIPTION": (
        "Shared-database, shared-schema multi-tenant API for the QUALION "
        "professional competency platform."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    [
        "http://localhost:3000",
        "http://145.79.0.94:83",
        "http://localhost:5173",     
        "http://145.79.0.94:81"
              
    ]
)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://localhost:3000$",
    r"^https?://localhost:5173$",
    r"^https?://([a-z0-9-]+\.)?qualion\.com$",
    r"^https?://145\.79\.0\.94:83$",
    r"^https?://145\.79\.0\.94:81$",
]
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {module}:{lineno} — {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "a2z_icsem.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}



