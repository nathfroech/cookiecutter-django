import pytest
from hamcrest import assert_that, equal_to, is_

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

        expected_url = '/users/{0}/'.format(user.username)
        assert_that(view.get_success_url(), is_(equal_to(expected_url)))

    def test_get_object(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        view = UserUpdateView()
        request = request_factory.get('/fake-url/')
        request.user = user

        view.request = request

        assert_that(view.get_object(), is_(equal_to(user)))


class TestUserRedirectView:
    def test_get_redirect_url(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        view = UserRedirectView()
        request = request_factory.get('/fake-url')
        request.user = user

        view.request = request

        expected_url = '/users/{0}/'.format(user.username)
        assert_that(view.get_redirect_url(), is_(equal_to(expected_url)))
