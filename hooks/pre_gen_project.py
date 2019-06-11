"""
Make some checks before actual start of project's generation.

NOTE:
    the below code is to be maintained Python 2.x-compatible
    as the whole Cookiecutter Django project initialization
    can potentially be run in Python 2.x environment.

TODO: ? restrict Cookiecutter Django project initialization to Python 3.x environments only
"""
from __future__ import print_function  # noqa: Z422

import contextlib
import sys

TERMINATOR = '\x1b[0m'
WARNING = '\x1b[1;33m [WARNING]: '
INFO = '\x1b[1;33m [INFO]: '
HINT = '\x1b[3;33m'
SUCCESS = '\x1b[1;32m [SUCCESS]: '

project_slug = '{{ cookiecutter.project_slug }}'
with contextlib.suppress(AttributeError):
    assert (  # noqa: S101
        project_slug.isidentifier()
    ), "'{0}' project slug is not a valid Python identifier.".format(project_slug)


assert (  # noqa: S101
    '\\' not in '{{ cookiecutter.author_name }}'  # noqa: Z308
), "Don't include backslashes in author name."

if '{{ cookiecutter.use_docker }}'.lower() == 'n':
    python_major_version = sys.version_info[0]
    if python_major_version == 2:
        print(  # noqa: T001
            WARNING + "You're running cookiecutter under Python 2, but the generated "
            'project requires Python 3.6+. Do you want to proceed (y/n)? ' + TERMINATOR,
        )
        yes_options, no_options = frozenset(['y']), frozenset(['n'])
        while True:
            choice = raw_input().lower()  # noqa: F821 Fails for Python 3
            if choice in yes_options:
                break

            elif choice in no_options:
                print(INFO + 'Generation process stopped as requested.' + TERMINATOR)  # noqa: T001
                sys.exit(1)
            else:
                print(  # noqa: T001
                    HINT
                    + 'Please respond with {0} or {1}: '.format(
                        ', '.join(["'{0}'".format(opt) for opt in yes_options if opt != '']),
                        ', '.join(["'{0}'".format(opt) for opt in no_options if opt != '']),
                    )
                    + TERMINATOR,
                )
