#!/usr/bin/env python

"""
Script for .env file generating.

Usage:
`python helpers/generate_env_file.py`

If you need to add a new setting, update `TEMPLATE` constant with line that looks like `SETTING_NAME = setting_value`.
In `TEMPLATE` you may use `{base_dir}` placeholder to substitute base project path. If you want to add more
substitutions - update the returning dict of the function `create_context`.
"""

import argparse
import hashlib
import pathlib
import random
import string
import time
from typing import Any, Dict

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

# TODO: Add your settings into these templates like `SETTING_NAME = setting_value`
# Note: If you are using Docker, you will need to change "localhost" to correct hosts in Redis and PostgreSQL variables
GENERAL_SETTINGS_TEMPLATE = """
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_SECRET_KEY={secret_key}
""".strip()

REDIS_SETTINGS_TEMPLATE = """
# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379/0
""".strip()

CELERY_SETTINGS_TEMPLATE = """
# Celery
# ------------------------------------------------------------------------------

# Flower
CELERY_FLOWER_USER={flower_user}
CELERY_FLOWER_PASSWORD={flower_password}
""".strip()

POSTGRESQL_SETTINGS_TEMPLATE = """
# PostgreSQL
# ------------------------------------------------------------------------------
DATABASE_URL = postgres://{project_name}:{postgres_password}@localhost:5432/{project_name}/
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB={project_name}
POSTGRES_USER={project_name}
POSTGRES_PASSWORD={postgres_password}
""".strip()

LOCAL_TEMPLATE = """
# General
# ------------------------------------------------------------------------------
USE_DOCKER=yes
IPYTHONDIR=/app/.ipython
PROJECT_ENVIRONMENT=debug
{general_settings}
ALLOWED_HOSTS = localhost,127.0.0.1

{%- if cookiecutter.use_celery == 'y' %}
{redis_settings}

{celery_settings}
{% endif -%}

{postgresql_settings}
""".format(
    general_settings=GENERAL_SETTINGS_TEMPLATE,
    {% if cookiecutter.use_celery == 'y' -%}
    redis_settings=REDIS_SETTINGS_TEMPLATE,
    celery_settings=CELERY_SETTINGS_TEMPLATE,
    {%- endif %}
    postgresql_settings=POSTGRESQL_SETTINGS_TEMPLATE,
)


PRODUCTION_TEMPLATE = """
# General
# ------------------------------------------------------------------------------
PROJECT_ENVIRONMENT = production
{general_settings}
ALLOWED_HOSTS=.{{ cookiecutter.domain_name }}

# Security
# ------------------------------------------------------------------------------
# TIP: better off using DNS, however, redirect is OK too
DJANGO_SECURE_SSL_REDIRECT=False

# Email
# ------------------------------------------------------------------------------
MAILGUN_API_KEY=
DJANGO_SERVER_EMAIL=
MAILGUN_DOMAIN=
{% if cookiecutter.cloud_provider == 'AWS' %}
# AWS
# ------------------------------------------------------------------------------
DJANGO_AWS_ACCESS_KEY_ID=
DJANGO_AWS_SECRET_ACCESS_KEY=
DJANGO_AWS_STORAGE_BUCKET_NAME=
{% elif cookiecutter.cloud_provider == 'GCE' %}
# GCE
# ------------------------------------------------------------------------------
GOOGLE_APPLICATION_CREDENTIALS=
DJANGO_GCE_STORAGE_BUCKET_NAME=
{% endif %}
# django-allauth
# ------------------------------------------------------------------------------
DJANGO_ACCOUNT_ALLOW_REGISTRATION=True
{% if cookiecutter.use_compressor == 'y' %}
# django-compressor
# ------------------------------------------------------------------------------
COMPRESS_ENABLED=
{% endif %}
# Gunicorn
# ------------------------------------------------------------------------------
WEB_CONCURRENCY=4
{% if cookiecutter.use_sentry == 'y' %}
# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN=
{% endif %}

{redis_settings}
{% if cookiecutter.use_celery == 'y' %}
{celery_settings}
{% endif %}

{postgresql_settings}
""".format(
    general_settings=GENERAL_SETTINGS_TEMPLATE,
    redis_settings=REDIS_SETTINGS_TEMPLATE,
    {% if cookiecutter.use_celery == 'y' -%}
    celery_settings=CELERY_SETTINGS_TEMPLATE,
    {%- endif %}
    postgresql_settings=POSTGRESQL_SETTINGS_TEMPLATE,
)

DEFAULT_ALLOWED_CHARS = string.ascii_letters + string.digits

Context = Dict[str, Any]


def create_arguments_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Generate .env file')
    parser.add_argument('--name', dest='file_name', action='store', default='.env')
    parser.add_argument('--rewrite', dest='rewrite', action='store_true')
    parser.add_argument('--production', dest='production', action='store_true')
    return parser


def generate_random_string(length: int = 14, allowed_chars: str = DEFAULT_ALLOWED_CHARS) -> str:
    """
    Generate random string of desired length.

    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+10)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.

        # Django uses settings.SECRET_KEY for this, but we cannot use the same strategy, because the code may be
        # executed in environment where Django has not been installed or configured yet
        temporary_secret_key = ''.join(random.choice(DEFAULT_ALLOWED_CHARS) for _ in range(length))
        new_seed = ('{0}{1}{2}'.format(random.getstate(), time.time(), temporary_secret_key)).encode()
        random.seed(hashlib.sha256(new_seed).digest())
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def create_context(base_dir: pathlib.Path) -> Context:
    symbols_to_use = string.ascii_lowercase + string.digits + '!@%^&*(-_=+)'
    return {
        'base_dir': str(base_dir),
        'project_name': '{{ cookiecutter.project_slug }}',
        'secret_key': generate_random_string(50, symbols_to_use),  # noqa: WPS432 Keep the number magic
        'postgres_password': generate_random_string(14, symbols_to_use),  # noqa: WPS432 Keep the number magic
        'flower_user': generate_random_string(8, symbols_to_use),
        'flower_password': generate_random_string(14, symbols_to_use),  # noqa: WPS432 Keep the number magic
    }


def render_to_string(template: str, context: Context) -> str:
    return template.format(**context)


def generate_dotenv_file(file_name: str, rewrite: bool = False, production: bool = False):
    project_dir = pathlib.Path(__file__).parents[1]
    file_path: pathlib.Path = project_dir / file_name
    if file_path.is_file() and not rewrite:
        raise ValueError('File {file_name} already exists!'.format(file_name=file_name))

    file_context = create_context(project_dir)
    if production:
        generated_file = PRODUCTION_TEMPLATE.format(**file_context)
    else:
        generated_file = LOCAL_TEMPLATE.format(**file_context)
    file_path.write_text(generated_file)


if __name__ == '__main__':
    arguments_parser = create_arguments_parser()
    args = arguments_parser.parse_args()
    generate_dotenv_file(args.file_name, args.rewrite, args.production)
