"""Make some checks before actual start of project's generation."""

import contextlib
import sys

WARNING_TEMPLATE = '\x1b[1;33m [WARNING]: {0} \x1b[0m'

python_major_version = sys.version_info[0]
if python_major_version == 2:
    print(WARNING_TEMPLATE.format(  # noqa: T001
        "You're running cookiecutter under Python 2, but the generation "
        'scripts require Python 3.6+. Generation process stopped.',
    ))
    sys.exit(1)
elif python_major_version == 3 and sys.version_info[1] < 6:
    print(WARNING_TEMPLATE.format(  # noqa: T001
        "You're running cookiecutter under Python 3.5 or lower, but the generation "
        'scripts require Python 3.6+. Generation process stopped.',
    ))
    sys.exit(1)

project_slug = '{{ cookiecutter.project_slug }}'
with contextlib.suppress(AttributeError):
    assert (  # noqa: S101
        project_slug.isidentifier()
    ), "'{0}' project slug is not a valid Python identifier.".format(project_slug)


assert (  # noqa: S101
    '\\' not in '{{ cookiecutter.author_name }}'  # noqa: WPS308
), "Don't include backslashes in author name."
