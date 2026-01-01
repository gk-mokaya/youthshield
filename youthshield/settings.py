import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = 'http://ysfdemo.pythonanywhere.com'

SECRET_KEY = 'your-secret-key-here'

# settings.py
import os

# Check if running on PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ

if ON_PYTHONANYWHERE:
    ALLOWED_HOSTS = [
        'ysfdemo.pythonanywhere.com',
        'www.ysfdemo.pythonanywhere.com',
    ]
    DEBUG = False
else:
    ALLOWED_HOSTS = ['ysfdemo.pythonanywhere.com','localhost', '127.0.0.1']
    DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django.contrib.humanize',
    'django_bootstrap5',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'ckeditor',
    # Local apps
    'core',
    'users',
    'testimonials',
    'programs',
    'donations',
    'api',
    'staff_dashboard',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'users.middleware.TabIndependentSessionMiddleware',  # Temporarily disabled
]

ROOT_URLCONF = 'youthshield.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.website_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'youthshield.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

AUTH_USER_MODEL = 'users.CustomUser'

# Session Security Settings
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True  # Use HTTPS in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/staticfiles/'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles']

# Messages framework
MESSAGE_TAGS = {
    10: 'debug',
    20: 'info',
    25: 'success',
    30: 'warning',
    40: 'error',
}


MEDIA_URL = '/media-files/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'users:redirect_based_on_role'
LOGOUT_REDIRECT_URL = 'core:home'
LOGIN_URL = '/login/'

# M-Pesa Configuration
MPESA_CONSUMER_KEY = 'vQOmjSWljQZEwiVBf8MpESCLx0CVjXBs2WyaCOmSTpBr8YHZ'
MPESA_CONSUMER_SECRET = 'KDKst58uEjltXTfyGYiJgULpTl1DvtWi19maKrM8aOQKGtRN1Yy0FwXDJZRsCkH7'
MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'


# PayPal Credentials (Sandbox)
PAYPAL_CLIENT_ID = 'ATt70YGX7aupA2_8AFYdkxJctcb2v3Y_neV8aqM-qUYRXz-jF8Hr2oGijE06hac90pPgiWbEO-OOVQVb'
PAYPAL_SECRET = 'EB3scqsN6VWO_IHvjppWXLcYlwTxsH0_sOXGqysXroBwvMu2O1_-VPulw_J12U8Wbrwmij7g3M6ntzKK'

# Stripe Credentials (Test)
STRIPE_PUBLIC_KEY ='pk_test_51RiodlPYv6mEP2LtcRvzftulO8ch8h9EOp9Nx91pFcsJnSJpfMOUzpk2uBPiSnksoDQBcZeHgKWZsQgZR7IqIM0Q00i6sDeILE'

STRIPE_SECRET_KEY = 'sk_test_51RiodlPYv6mEP2Lt8ZYMd8yP3eajUwxzVtu25496yEZTvV7GHW1UBzd5z7uljlQjtgDasU7ypAvGefTU3NrEAuM000Hb2jl4g0'

STRIPE_WEBHOOK_SECRET = 'whsec_test_your_webhook_secret_here'  # Replace with actual webhook secret from Stripe dashboard
