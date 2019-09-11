#!/usr/bin/env python

import sys

from config.prepare_environment import prepare_environment

if __name__ == '__main__':
    prepare_environment()

    try:
        from django.core.management import execute_from_command_line  # noqa: WPS433 Nested import is intended
    except ImportError:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?',
        )

    execute_from_command_line(sys.argv)
