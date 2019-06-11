import pytest
from hamcrest import assert_that, equal_to, is_

from django.conf import settings

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: settings.AUTH_USER_MODEL):
    expected_url = '/users/{0}/'.format(user.username)
    assert_that(user.get_absolute_url(), is_(equal_to(expected_url)))
