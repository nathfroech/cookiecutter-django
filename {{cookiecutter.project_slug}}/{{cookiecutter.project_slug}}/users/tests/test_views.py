import pytest

from django.conf import settings
from django.test import RequestFactory

from {{ cookiecutter.project_slug }}.users.views import UserRedirectView, UserUpdateView

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    def test_get_success_url(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        view = UserUpdateView()
        request = request_factory.get('/fake-url/')
        request.user = user

        view.request = request

        assert view.get_success_url() == '/users/{0}/'.format(user.username)

    def test_get_object(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        view = UserUpdateView()
        request = request_factory.get('/fake-url/')
        request.user = user

        view.request = request

        assert view.get_object() == user


class TestUserRedirectView:
    def test_get_redirect_url(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        view = UserRedirectView()
        request = request_factory.get('/fake-url')
        request.user = user

        view.request = request

        assert view.get_redirect_url() == '/users/{0}/'.format(user.username)
