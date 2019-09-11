"""Base settings to build other settings files upon."""
{% if cookiecutter.use_sentry == 'y' -%}
import logging
{%- endif %}
import pathlib

import environs
{%- if cookiecutter.use_sentry == 'y' %}
import sentry_sdk
{%- endif %}
from marshmallow.validate import OneOf
{%- if cookiecutter.use_sentry == 'y' -%}
{%- if cookiecutter.use_celery == 'y' %}
from sentry_sdk.integrations.celery import CeleryIntegration
{%- endif %}
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
{%- endif %}

env = environs.Env()
env.read_env()

# ('{{ cookiecutter.project_slug }}/config/settings.py'.parents[1] = '{{ cookiecutter.project_slug }}/')
ROOT_DIR = pathlib.Path(__file__).parents[1]
APPS_DIR = ROOT_DIR / '{{ cookiecutter.project_slug }}'

# GENERAL
# ------------------------------------------------------------------------------
# Setting is not intended to be used as is - only as a single point to toggle some environment-related values.
ENVIRONMENT_DEBUG = 'debug'
ENVIRONMENT_TEST = 'test'
ENVIRONMENT_PRODUCTION = 'production'
PROJECT_ENVIRONMENT = env(
    'PROJECT_ENVIRONMENT',
    ENVIRONMENT_PRODUCTION,
    validate=OneOf([ENVIRONMENT_DEBUG, ENVIRONMENT_TEST, ENVIRONMENT_PRODUCTION]),
)

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', PROJECT_ENVIRONMENT == ENVIRONMENT_DEBUG)
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['{{ cookiecutter.domain_name }}'])

# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = env('DJANGO_TIMEZONE', 'UTC')
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                # Mimicing memcache behavior.
                # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
                'IGNORE_EXCEPTIONS': True,
            },
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': '',
        },
    }

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
]
THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    {%- if cookiecutter.use_whitenoise == 'n' %}
    # https://github.com/antonagestam/collectfast#installation
    'collectfast',
    {%- endif %}
    {% if cookiecutter.use_compressor == 'y' %}
    # https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
    'compressor',
    {%- endif %}
    'rest_framework',
]
if PROJECT_ENVIRONMENT == ENVIRONMENT_DEBUG:
    THIRD_PARTY_APPS += [
        # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
        'debug_toolbar',
        # https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
        'django_extensions',
    ]
elif PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    THIRD_PARTY_APPS += [
        # https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
        'anymail',
        'gunicorn',
        # https://django-storages.readthedocs.io/en/latest/#installation
        'storages',
    ]
LOCAL_APPS = [
    '{{ cookiecutter.project_slug }}.users.apps.UsersAppConfig',
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'users.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = 'users:redirect'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = 'account_login'

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
if PROJECT_ENVIRONMENT == ENVIRONMENT_TEST:
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
else:
    PASSWORD_HASHERS = [
        # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
if PROJECT_ENVIRONMENT in {ENVIRONMENT_DEBUG, ENVIRONMENT_TEST}:
    AUTH_PASSWORD_VALIDATORS = []
else:
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    {%- if cookiecutter.use_whitenoise == 'y' %}
    # http://whitenoise.evans.io/en/latest/django.html#enable-whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',
    {%- endif %}
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if PROJECT_ENVIRONMENT == ENVIRONMENT_DEBUG:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']


# SECURITY
# ------------------------------------------------------------------------------
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
    SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
    # https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
    SESSION_COOKIE_SECURE = True
    # https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
    CSRF_COOKIE_SECURE = True
    # https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
    # TODO: set this to 60 seconds first and then to 518400 once you prove the former works
    SECURE_HSTS_SECONDS = 60
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
    SECURE_HSTS_PRELOAD = env.bool('DJANGO_SECURE_HSTS_PRELOAD', default=True)
    # https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
    SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)

{% if cookiecutter.cloud_provider == 'AWS' %}
# STORAGES
# ------------------------------------------------------------------------------
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_QUERYSTRING_AUTH = False
    # DO NOT change these unless you know what you're doing.
    _AWS_EXPIRY = 60 * 60 * 24 * 7
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age={0}, s-maxage={0}, must-revalidate'.format(_AWS_EXPIRY)}
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_DEFAULT_ACL = None
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_S3_REGION_NAME = env('DJANGO_AWS_S3_REGION_NAME', default=None)
{% elif cookiecutter.cloud_provider == 'GCE' %}
# STORAGES
# ------------------------------------------------------------------------------
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = env('DJANGO_GCE_STORAGE_BUCKET_NAME')
    GS_DEFAULT_ACL = 'publicRead'
{% endif %}

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR.joinpath('staticfiles'))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
{%- if cookiecutter.cloud_provider == 'AWS' %}
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    STATIC_URL = 'https://{0}.s3.amazonaws.com/static/'.format(AWS_STORAGE_BUCKET_NAME)
{%- elif cookiecutter.cloud_provider == 'GCE' %}
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    STATIC_URL = 'https://storage.googleapis.com/{0}/static/'.format(GS_BUCKET_NAME)
{%- endif %}
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.joinpath('static'))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    {%- if cookiecutter.use_compressor == 'y' %}
    # https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
    'compressor.finders.CompressorFinder',

    {%- endif %}
]
{%- if cookiecutter.cloud_provider == 'AWS' %}
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    STATICFILES_STORAGE = 'config.custom_storages.StaticRootS3Boto3Storage'
{%- elif cookiecutter.use_whitenoise == 'y' %}
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
{%- endif %}

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR.joinpath('media'))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
{%- if cookiecutter.cloud_provider == 'AWS' %}
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    MEDIA_URL = 'https://{0}.s3.amazonaws.com/media/'.format(AWS_STORAGE_BUCKET_NAME)
DEFAULT_FILE_STORAGE = 'config.custom_storages.MediaRootS3Boto3Storage'
{%- elif cookiecutter.cloud_provider == 'GCE' %}
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    MEDIA_URL = 'https://storage.googleapis.com/{0}/media/'.format(GS_BUCKET_NAME)
    MEDIA_ROOT = 'https://storage.googleapis.com/{0}/media/'.format(GS_BUCKET_NAME)
{%- endif %}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
loaders = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]
if PROJECT_ENVIRONMENT != ENVIRONMENT_DEBUG:
    loaders = (
        'django.template.loaders.cached.Loader',
        loaders,
    )
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [str(APPS_DIR.joinpath('templates'))],
        'OPTIONS': {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': loaders,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.joinpath('fixtures')),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = 'DENY'

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
if PROJECT_ENVIRONMENT == ENVIRONMENT_DEBUG:
    {% if cookiecutter.use_mailhog == 'y' -%}
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-host
    EMAIL_HOST = env('EMAIL_HOST', default='mailhog')
    {%- else -%}
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
    EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-host
    EMAIL_HOST = 'localhost'
    {%- endif %}
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-port
    EMAIL_PORT = 1025
elif PROJECT_ENVIRONMENT == ENVIRONMENT_TEST:
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-host
    EMAIL_HOST = 'localhost'
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-port
    EMAIL_PORT = 1025
elif PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    # https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
    DEFAULT_FROM_EMAIL = env(
        'DJANGO_DEFAULT_FROM_EMAIL', default='{{cookiecutter.project_name}} <noreply@{{cookiecutter.domain_name}}>',
    )
    # https://docs.djangoproject.com/en/dev/ref/settings/#server-email
    SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
    # https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
    EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[{{cookiecutter.project_name}}]')

    # Anymail (Mailgun)
    # ------------------------------------------------------------------------------
    # https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    # https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
    ANYMAIL = {
        'MAILGUN_API_KEY': env('MAILGUN_API_KEY'),
        'MAILGUN_SENDER_DOMAIN': env('MAILGUN_DOMAIN'),
    }
else:
    EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = env('DJANGO_ADMIN_URL', 'admin/')
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = []
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

{% if cookiecutter.use_celery == 'y' -%}
# Celery
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['{{cookiecutter.project_slug}}.taskapp.celery.CeleryAppConfig']
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ['json']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_SOFT_TIME_LIMIT = 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = DEBUG
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = DEBUG

{%- endif %}
# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)  # noqa: WPS425
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = 'username'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = '{{cookiecutter.project_slug}}.users.adapters.AccountAdapter'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = '{{cookiecutter.project_slug}}.users.adapters.SocialAccountAdapter'

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
    'SHOW_TEMPLATE_CONTEXT': True,
}
if PROJECT_ENVIRONMENT == ENVIRONMENT_DEBUG:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
if env('USE_DOCKER') == 'yes':
    import socket  # noqa: WPS433

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]

{%- if cookiecutter.use_compressor == 'y' %}
# django-compressor
# ------------------------------------------------------------------------------
if PROJECT_ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    # https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
    COMPRESS_ENABLED = env.bool('COMPRESS_ENABLED', default=True)
    # https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
    COMPRESS_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_URL
    COMPRESS_URL = STATIC_URL
{% endif %}
{%- if cookiecutter.use_whitenoise == 'n' %}

# Collectfast
# ------------------------------------------------------------------------------
# https://github.com/antonagestam/collectfast#installation
AWS_PRELOAD_METADATA = True
{% endif %}


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
{% if cookiecutter.use_sentry == 'n' -%}
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}
{% else %}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # Errors logged by the SDK itself
        'sentry_sdk': {'level': 'ERROR', 'handlers': ['console'], 'propagate': False},
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN')
SENTRY_LOG_LEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)

sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
    event_level=None,  # Send no events from log messages
)

{%- if cookiecutter.use_celery == 'y' %}
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[sentry_logging, DjangoIntegration(), CeleryIntegration()],
)
{% else %}
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging, DjangoIntegration()])
{% endif -%}
{% endif %}
