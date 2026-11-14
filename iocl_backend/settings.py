from datetime import timedelta
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY / ENVIRONMENT

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1,0.0.0.0",
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default="http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

# APPLICATIONS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "users",
    "equipment",
    "sensors",
    "water_quality",
    "process_monitoring",
    "alerts",
    "treatment_process",
    "mqtt",
    "warehouses",
]

AUTH_USER_MODEL = "users.User"

# MIDDLEWARE

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

# URL / WSGI

ROOT_URLCONF = "iocl_backend.urls"
WSGI_APPLICATION = "iocl_backend.wsgi.application"

# TEMPLATES

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# DATABASE

DATABASES = {
    "default": {
        "ENGINE": config(
            "DB_ENGINE",
            default="django.db.backends.postgresql",
        ),
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": config("DB_SSLMODE", default="require"),
        },
    }
}

# PASSWORD VALIDATION

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]

# INTERNATIONALIZATION

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# STATIC / MEDIA FILES

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# EMAIL

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER,
)



# REST FRAMEWORK

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# SIMPLE JWT

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# CORS

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

# PRODUCTION SECURITY

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config(
        "SECURE_SSL_REDIRECT",
        default=False,
        cast=bool,
    )

# DEFAULT PRIMARY KEY

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# Redis Configuration
# ============================================================

REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")

REDIS_URL = (
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    if REDIS_PASSWORD
    else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)



# MQTT CONFIGURATION

MQTT_BROKER = config("MQTT_BROKER")
MQTT_PORT = config("MQTT_PORT", default=1883, cast=int)
MQTT_USER = config("MQTT_USER")
MQTT_PASSWORD = config("MQTT_PASSWORD")
MQTT_CLIENT_ID = config(
    "MQTT_CLIENT_ID",
    default="AQUAPOD_DJANGO_01",
)