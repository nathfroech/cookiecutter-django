import pytest

from django.conf import settings
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_detail(user: settings.AUTH_USER_MODEL):
    assert (
        reverse('users:detail', kwargs={'username': user.username})
        == '/users/{0}/'.format(user.username)
    )
    assert resolve('/users/{0}/'.format(user.username)).view_name == 'users:detail'


def test_list():
    assert reverse('users:list') == '/users/'
    assert resolve('/users/').view_name == 'users:list'


def test_update():
    assert reverse('users:update') == '/users/~update/'
    assert resolve('/users/~update/').view_name == 'users:update'


def test_redirect():
    assert reverse('users:redirect') == '/users/~redirect/'
    assert resolve('/users/~redirect/').view_name == 'users:redirect'
