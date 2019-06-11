"""
Make additional operations after project generation.

NOTE:
    the below code is to be maintained Python 2.x-compatible
    as the whole Cookiecutter Django project initialization
    can potentially be run in Python 2.x environment
    (at least so we presume in `pre_gen_project.py`).

TODO: ? restrict Cookiecutter Django project initialization to Python 3.x environments only
"""
from __future__ import print_function  # noqa: Z422

import os
import pathlib
import random
import re
import shutil
import string

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

TERMINATOR = '\x1b[0m'
WARNING = '\x1b[1;33m [WARNING]: '
INFO = '\x1b[1;33m [INFO]: '
HINT = '\x1b[3;33m'
SUCCESS = '\x1b[1;32m [SUCCESS]: '

DEBUG_VALUE = 'debug'


PROJECT_ROOT = pathlib.Path.cwd()


def clean_files(*files_to_clean: str):
    for file_name in files_to_clean:
        PROJECT_ROOT.joinpath(file_name).unlink()


def clean_dir(*dir_path_terms: str):
    dir_path = PROJECT_ROOT.joinpath(*dir_path_terms)
    if dir_path.is_dir():
        shutil.rmtree(dir_path)


def remove_open_source_files():
    clean_files('CONTRIBUTORS.txt', 'LICENSE')


def remove_gplv3_files():
    clean_files('COPYING')


def remove_pycharm_files():
    clean_dir('.idea')
    clean_dir('docs', 'pycharm')


def remove_docker_files():
    clean_dir('compose')

    clean_files('local.yml', 'production.yml', '.dockerignore')


def remove_utility_files():
    clean_dir('utility')


def remove_heroku_files():
    file_names = ['Procfile', 'runtime.txt']
    if '{{ cookiecutter.use_travisci }}'.lower() != 'y':
        # don't remove the file if we are using travisci but not using heroku
        file_names.append('requirements.txt')
    clean_files(*file_names)


def remove_gulp_files():
    clean_files('gulpfile.js')


def remove_packagejson_file():
    clean_files('package.json')


def remove_celery_app():
    clean_dir('{{ cookiecutter.project_slug }}', 'taskapp')


def remove_dottravisyml_file():
    clean_files('.travis.yml')


def append_to_project_gitignore(path):
    gitignore_file_path = '.gitignore'
    with open(gitignore_file_path, 'a') as gitignore_file:
        gitignore_file.write(path)
        gitignore_file.write(os.linesep)


def generate_random_string(
    length, using_digits=False, using_ascii_letters=False, using_punctuation=False,
):
    """
    Generate random string of desired length.

    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', '\\', '$'}
        suitable = all_punctuation.difference(unsuitable)
        symbols += ''.join(suitable)
    return ''.join([random.choice(symbols) for _ in range(length)])


def set_flag(file_path, flag, value=None, formatted=None, *args, **kwargs):  # noqa: Z110,Z211
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your system. "
                'Please, make sure to manually {0} later.'.format(flag),
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string  # noqa: Z110

    with open(file_path, 'r+') as file:  # noqa: Z110
        file_contents = file.read().replace(flag, value)
        file.seek(0)
        file.write(file_contents)
        file.truncate()

    return value


def set_django_secret_key(file_path):
    django_secret_key = set_flag(
        file_path,
        '!!!SET DJANGO_SECRET_KEY!!!',
        length=64,  # noqa: Z432
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_secret_key


def set_django_admin_url(file_path):
    django_admin_url = set_flag(
        file_path,
        '!!!SET DJANGO_ADMIN_URL!!!',
        formatted='{0}/',
        length=32,  # noqa: Z432
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_admin_url


def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)  # noqa: Z432


def generate_postgres_user(debug=False):
    return DEBUG_VALUE if debug else generate_random_user()


def set_postgres_user(file_path, value):  # noqa: Z110
    postgres_user = set_flag(file_path, '!!!SET POSTGRES_USER!!!', value=value)
    return postgres_user


def set_postgres_password(file_path, value=None):  # noqa: Z110
    postgres_password = set_flag(
        file_path,
        '!!!SET POSTGRES_PASSWORD!!!',
        value=value,
        length=64,  # noqa: Z432
        using_digits=True,
        using_ascii_letters=True,
    )
    return postgres_password


def set_celery_flower_user(file_path, value):  # noqa: Z110
    celery_flower_user = set_flag(file_path, '!!!SET CELERY_FLOWER_USER!!!', value=value)
    return celery_flower_user


def set_celery_flower_password(file_path, value=None):  # noqa: Z110
    celery_flower_password = set_flag(
        file_path,
        '!!!SET CELERY_FLOWER_PASSWORD!!!',
        value=value,
        length=64,  # noqa: Z432
        using_digits=True,
        using_ascii_letters=True,
    )
    return celery_flower_password


def set_flags_in_envs(postgres_user, celery_flower_user, debug=False):  # noqa: Z213
    local_django_envs_path = os.path.join('.envs', '.local', '.django')
    production_django_envs_path = os.path.join('.envs', '.production', '.django')
    local_postgres_envs_path = os.path.join('.envs', '.local', '.postgres')
    production_postgres_envs_path = os.path.join('.envs', '.production', '.postgres')

    set_django_secret_key(production_django_envs_path)
    set_django_admin_url(production_django_envs_path)

    set_postgres_user(local_postgres_envs_path, value=postgres_user)
    set_postgres_password(local_postgres_envs_path, value=DEBUG_VALUE if debug else None)
    set_postgres_user(production_postgres_envs_path, value=postgres_user)
    set_postgres_password(production_postgres_envs_path, value=DEBUG_VALUE if debug else None)

    set_celery_flower_user(local_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(local_django_envs_path, value=DEBUG_VALUE if debug else None)
    set_celery_flower_user(production_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(production_django_envs_path, value=DEBUG_VALUE if debug else None)


def set_flags_in_settings_files():
    set_django_secret_key(os.path.join('config', 'settings', 'local.py'))
    set_django_secret_key(os.path.join('config', 'settings', 'test.py'))


def remove_envs_and_associated_files():
    shutil.rmtree('.envs')
    os.remove('merge_production_dotenvs_in_dotenv.py')


def remove_celery_compose_dirs():
    shutil.rmtree(os.path.join('compose', 'local', 'django', 'celery'))
    shutil.rmtree(os.path.join('compose', 'production', 'django', 'celery'))


def remove_node_dockerfile():
    shutil.rmtree(os.path.join('compose', 'local', 'node'))


def clean_file_contents():
    """Clean generated files from trailing whitespaces and extra newlines."""
    for file_path in PROJECT_ROOT.rglob('*'):
        if file_path.suffix in ('.ico',):
            continue
        if file_path.is_file():
            file_content = file_path.read_text()

            # Remove trailing whitespaces.
            file_content = re.sub(r'[ \t]+\n', '\n', file_content)
            # Python and Javascript files may use two empty lines to separate code blocks (classes, etc.). Each
            # particular case for them will be checked by language-specific linters. For other files one empty line
            # is enough.
            if file_path.suffix in ('.py', '.js'):
                file_content = re.sub(r'\n{4,}', '\n\n\n', file_content, flags=re.MULTILINE)
            else:
                file_content = re.sub(r'\n{3,}', '\n\n', file_content, flags=re.MULTILINE)
            # Remove extra newlines before end of file.
            file_content = re.sub(r'\n{2,}\Z', '\n', file_content, flags=re.MULTILINE)

            file_path.write_text(file_content)


def main():  # noqa: C901,Z213
    debug = '{{ cookiecutter.debug }}'.lower() == 'y'

    set_flags_in_envs(
        DEBUG_VALUE if debug else generate_random_user(),
        DEBUG_VALUE if debug else generate_random_user(),
        debug=debug,
    )
    set_flags_in_settings_files()

    if '{{ cookiecutter.open_source_license }}' == 'Not open source':  # noqa: Z308
        remove_open_source_files()
    if '{{ cookiecutter.open_source_license}}' != 'GPLv3':  # noqa: Z308
        remove_gplv3_files()

    if '{{ cookiecutter.use_pycharm }}'.lower() == 'n':
        remove_pycharm_files()

    if '{{ cookiecutter.use_docker }}'.lower() == 'y':
        remove_utility_files()
    else:
        remove_docker_files()

    if '{{ cookiecutter.use_heroku }}'.lower() == 'n':
        remove_heroku_files()

    if (
        '{{ cookiecutter.use_docker }}'.lower() == 'n'
        and '{{ cookiecutter.use_heroku }}'.lower() == 'n'
    ):
        if '{{ cookiecutter.keep_local_envs_in_vcs }}'.lower() == 'y':
            print(
                INFO + '.env(s) are only utilized when Docker Compose and/or '
                'Heroku support is enabled so keeping them does not '
                'make sense given your current setup.' + TERMINATOR,
            )
        remove_envs_and_associated_files()
    else:
        append_to_project_gitignore('.env')
        append_to_project_gitignore('.envs/*')
        if '{{ cookiecutter.keep_local_envs_in_vcs }}'.lower() == 'y':
            append_to_project_gitignore('!.envs/.local/')

    if '{{ cookiecutter.js_task_runner}}'.lower() == 'none':
        remove_gulp_files()
        remove_packagejson_file()
        if '{{ cookiecutter.use_docker }}'.lower() == 'y':
            remove_node_dockerfile()

    if '{{ cookiecutter.use_celery }}'.lower() == 'n':
        remove_celery_app()
        if '{{ cookiecutter.use_docker }}'.lower() == 'y':
            remove_celery_compose_dirs()

    if '{{ cookiecutter.use_travisci }}'.lower() == 'n':
        remove_dottravisyml_file()

    clean_file_contents()

    print(SUCCESS + 'Project initialized, keep up the good work!' + TERMINATOR)


if __name__ == '__main__':
    main()
