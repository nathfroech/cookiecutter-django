import os
import pathlib
import re

import pytest
import sh
import yaml
from binaryornot.check import is_binary
from hamcrest import assert_that, equal_to, is_, none
from pytest_cases import pytest_fixture_plus

PATTERN = r'{{(\s?cookiecutter)[.](.*?)}}'
RE_OBJ = re.compile(PATTERN)

YN_CHOICES = ('y', 'n')
CLOUD_CHOICES = ('AWS', 'GCE')


@pytest.fixture
def context():
    return {
        'project_name': 'My Test Project',
        'project_slug': 'my_test_project',
        'author_name': 'Test Author',
        'description': 'A short description of the project.',
        'domain_name': 'example.com',
        'version': '0.1.0',
    }


@pytest_fixture_plus  # noqa: WPS211,WPS216
@pytest.mark.parametrize('windows', YN_CHOICES, ids=lambda yn: 'win:{0}'.format(yn))
@pytest.mark.parametrize('use_docker', YN_CHOICES, ids=lambda yn: 'docker:{0}'.format(yn))
@pytest.mark.parametrize('use_celery', YN_CHOICES, ids=lambda yn: 'celery:{0}'.format(yn))
@pytest.mark.parametrize('use_mailhog', YN_CHOICES, ids=lambda yn: 'mailhog:{0}'.format(yn))
@pytest.mark.parametrize('use_sentry', YN_CHOICES, ids=lambda yn: 'sentry:{0}'.format(yn))
@pytest.mark.parametrize('use_compressor', YN_CHOICES, ids=lambda yn: 'cmpr:{0}'.format(yn))
@pytest.mark.parametrize('use_whitenoise', YN_CHOICES, ids=lambda yn: 'wnoise:{0}'.format(yn))
@pytest.mark.parametrize('cloud_provider', CLOUD_CHOICES, ids=lambda yn: 'cloud:{0}'.format(yn))
def context_combination(
    windows,
    use_docker,
    use_celery,
    use_mailhog,
    use_sentry,
    use_compressor,
    use_whitenoise,
    cloud_provider,
):
    """Fixture that parametrize the function where it's used."""
    return {
        'windows': windows,
        'use_docker': use_docker,
        'use_compressor': use_compressor,
        'use_celery': use_celery,
        'use_mailhog': use_mailhog,
        'use_sentry': use_sentry,
        'use_whitenoise': use_whitenoise,
        'cloud_provider': cloud_provider,
    }


def build_files_list(root_dir):
    """Build a list containing absolute paths to the generated files."""
    return [
        os.path.join(dirpath, file_path)
        for dirpath, subdirs, files in os.walk(root_dir)
        for file_path in files
    ]


def check_paths(paths):
    """Check all paths have correct substitutions, used by other tests cases."""
    # Assert that no match is found in any of the files
    message_template = 'cookiecutter variable not replaced in {0}'
    for path in paths:
        if is_binary(path):
            continue

        for line in open(path, 'r'):
            match = RE_OBJ.search(line)
            assert_that(match, is_(none()), message_template.format(path))


def test_project_generation(cookies, context, context_combination):  # noqa: WPS213
    """
    Test that project is generated, fully rendered and passes pre-commit.

    This is parametrized for each combination from ``context_combination`` fixture
    """
    baked_result = cookies.bake(extra_context={**context, **context_combination})
    project_path = str(baked_result.project)

    assert_that(baked_result.exit_code, is_(equal_to(0)))
    assert_that(baked_result.exception, is_(none()))
    assert_that(baked_result.project.basename, is_(equal_to(context['project_slug'])))
    assert_that(baked_result.project.isdir())

    assert_that(pathlib.Path(project_path).joinpath('setup.cfg').is_file())
    assert_that(pathlib.Path(project_path).joinpath('.env').is_file())

    paths = build_files_list(project_path)
    assert_that(paths)
    check_paths(paths)

    try:
        sh.git('init', _cwd=project_path)
        sh.git('add', '.', _cwd=project_path)
        sh.pre_commit('install', _cwd=project_path)
        sh.pre_commit('run', '--all-files', _cwd=project_path)
    except sh.ErrorReturnCode as error:
        pytest.fail(error.stdout)


def test_travis_invokes_pytest(cookies, context):
    context.update({'use_travisci': 'y'})
    baked_result = cookies.bake(extra_context=context)

    assert_that(baked_result.exit_code, is_(equal_to(0)))
    assert_that(baked_result.exception, is_(none()))
    assert_that(baked_result.project.basename, is_(equal_to(context['project_slug'])))
    assert_that(baked_result.project.isdir())

    with open('{0}/.travis.yml'.format(baked_result.project), 'r') as travis_yml:
        try:
            travis_script = yaml.full_load(travis_yml)['script']
            assert_that(travis_script, is_(equal_to(['pytest'])))
        except yaml.YAMLError as error:
            pytest.fail(error)
