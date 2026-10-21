from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root so OPENAI_API_KEY and others are available
import os
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass  # python-dotenv not installed; decouple will still read .env from CWD


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable or set in production settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed hosts - set via environment variable in production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'subscription',  # Subscription / billing
    'master_admin',  # Master Admin Panel (Superuser only)
    'core',
    'regions',  # Regions, Cities, Clinics, Specializations
    'doctors',
    'drugs',  # Drugs/Medicines Management
    'prescriptions',  # Prescription/Recipe Management
    'reports',
    'sales',
    'chatbot',  # AI Chatbot with n8n integration
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.DualSessionMiddleware',  # Custom: separate cookies for admin & regular site
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.AdminSuperuserRestrictionMiddleware',  # Restrict Django admin to superadmin only
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'subscription.middleware.CompanyContextMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'subscription.context_processors.notifications',
                'core.context_processors.system_branding',  # System branding (name, logo)
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'   


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Local: SQLite (default). Production: set DJANGO_SETTINGS_MODULE=config.settings_production → PostgreSQL

USE_POSTGRESQL = config('USE_POSTGRESQL', default=False, cast=bool)

if USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='medadmin'),
            'USER': config('DB_USER', default='medadmin_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'az'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication Settings
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:login'

# Session Cookie Settings
# Note: DualSessionMiddleware uses 'admin_sessionid' for /admin/ paths
# and 'sessionid' (default) for regular site paths
SESSION_COOKIE_NAME = 'sessionid'  # Default cookie for regular site
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = False

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# OpenAI Configuration for AI Chatbot (hidden until re-enabled)
CHATBOT_ENABLED = config('CHATBOT_ENABLED', default=False, cast=bool)
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-3.5-turbo')
CHATBOT_API_KEY = config('CHATBOT_API_KEY', default='20251129')

# System Branding Configuration
SYSTEM_NAME = config('SYSTEM_NAME', default='MedCore')
SYSTEM_SUBTITLE = config('SYSTEM_SUBTITLE', default='')
SYSTEM_LOGO = config('SYSTEM_LOGO', default='img/icon.png')  # Path to logo in static folder
SYSTEM_FAVICON = config('SYSTEM_FAVICON', default='img/icon.png')  # Path to favicon in static folder

