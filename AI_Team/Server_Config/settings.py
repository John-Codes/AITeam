"""
Django settings for landingpage project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import os

    

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x#@g(83fg26+c*bpz*0vepc=#eei3a&58zj3x@8z_k(2)*3n+_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# email send config
email_sender =os.environ.get('email_sender')
password_sender =os.environ.get('password_sender')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = email_sender
EMAIL_HOST_PASSWORD = password_sender

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    'django.contrib.sitemaps',
    'Server_Config.Server_Side', # path where we found it the Server config of our app
    "django_check_seo",
    'cms',
    'menus',
    'treebeard',
    'rosetta',
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    'Server_Config.Server_Side.error_middleware.ErrorHandlingMiddleware',
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR,  "locale"),
    ]

LANGUAGES = (
    ('en', _('English')),
    ('es', _('Español')),
)

ROOT_URLCONF = "Server_Config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, "Client_Side", "templates")], #path to templates files .html for the UI
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "AI_Team.Server_Config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "Server_Config/AITeam.sqlite3",
    }
}

MIGRATION_MODULES = {
    'Server_Side': 'Server_Config.Server_Side.migrations',
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 5,
        }
    }
]        

"""AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]"""


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "Client_Side", "statics")] # path django searches the static files (images, styles in css and java scripts) for loaded 
STATIC_ROOT = os.path.join(BASE_DIR, "Client_Side", "statics_deployment")
# define la carpeta mediaroot para los archivos estaticos que suben los usuarios
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "Client_Side",'media_products')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Model User for Auth
#AUTH_USER_MODEL = 'Server_Side.CustomUser'
LOGIN_REDIRECT_URL = reverse_lazy('ai-team', kwargs={'context': 'main'})

#Paypal Configuration
#PAYPAL_RECEIVER_EMAIL = 'sb-m6xzg27588130@business.example.com' # where cash is paid into
#PAYPAL_BUY_BUTTON_IMAGE = 'https://res.cloudinary.com/the-proton-guy/image/upload/v1685882223/paypal-PhotoRoom_v9pay7.png'
PCI = os.getenv('PCI')
PCS = os.getenv('PCS')

# Stripe Configuration
STRIPE_SECRET_KEY = "sk_test_51IoDMBCJRk9RYTua3odVBYUrbIJoLxUD7i14lhDAfj11oHrBaFU57DFboN76hqS6Gbsbz5OnOOd7Ey0Z3zc8zSwA00JXlvL1sq"
STRIPE_PUBLIC_KEY = "pk_test_51IoDMBCJRk9RYTualhwP2KRwI1TivJcJEcRMVQ95XaCjCp00hVVDjkSapy6NJg7trBSn5iK4dBWwVIfuNDOS97iO00LCTnGwX9"

AUTH_USER_MODEL = 'Server_Side.Client'