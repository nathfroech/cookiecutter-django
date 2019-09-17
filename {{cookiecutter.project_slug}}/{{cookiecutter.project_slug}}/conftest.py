import pytest
from model_mommy import mommy

from django.test import RequestFactory

from {{ cookiecutter.project_slug }}.users.models import User


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return mommy.make(User)


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
