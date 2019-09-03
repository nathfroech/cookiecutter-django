#!/usr/bin/env python

import os
import pathlib
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

    try:
        from django.core.management import execute_from_command_line  # noqa: WPS433 Nested import is intended
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?',
        ) from exc

    # This allows easy placement of apps within the interior
    # {{ cookiecutter.project_slug }} directory.
    current_path = pathlib.Path(__file__).parent
    sys.path.append(current_path.joinpath('{{ cookiecutter.project_slug }}'))

    execute_from_command_line(sys.argv)
