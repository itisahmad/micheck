"""
Django settings for miccheck project.
Production-ready with PostgreSQL and env configuration.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-secret-change-in-production",
)

DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

_allowed = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]
if "*" in _allowed:
    ALLOWED_HOSTS = ["*"]
else:
    # Vercel: allow *.vercel.app when deploying backend to Vercel
    if ".vercel.app" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".vercel.app")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "bookings",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "miccheck.urls"

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

WSGI_APPLICATION = "miccheck.wsgi.application"

# Database: PostgreSQL from env (DATABASE_URL or POSTGRES_*), fallback SQLite for local dev
import dj_database_url

_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=_db_url,
            conn_max_age=60,
        )
    }
else:
    _pg_password = os.environ.get("POSTGRES_PASSWORD") or os.environ.get("PGPASSWORD")
    if _pg_password or os.environ.get("POSTGRES_HOST") or os.environ.get("PGHOST"):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("POSTGRES_DB", os.environ.get("PGDATABASE", "miccheck")),
                "USER": os.environ.get("POSTGRES_USER", os.environ.get("PGUSER", "postgres")),
                "PASSWORD": _pg_password or "",
                "HOST": os.environ.get("POSTGRES_HOST", os.environ.get("PGHOST", "localhost")),
                "PORT": os.environ.get("POSTGRES_PORT", os.environ.get("PGPORT", "5432")),
                "CONN_MAX_AGE": 60,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS: from env in production (comma-separated origins), include localhost for dev
_cors = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True

# Optional: allow all origins in dev (set CORS_ALLOW_ALL_ORIGINS=true)
if os.environ.get("CORS_ALLOW_ALL_ORIGINS", "").lower() in ("true", "1", "yes"):
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Security in production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
