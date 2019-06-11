import pytest
from hamcrest import assert_that, equal_to, has_key, has_length, is_
from model_mommy import mommy

from {{ cookiecutter.project_slug }}.users.forms import UserCreationForm
from {{ cookiecutter.project_slug }}.users.models import User

pytestmark = pytest.mark.django_db


class TestUserCreationForm:
    def test_clean_username_of_nonexistent_user(self):
        form = UserCreationForm({
            'username': 'user',
            'password1': 'pwd',
            'password2': 'pwd',
        })

        assert_that(form.is_valid())
        assert_that(form.cleaned_data['username'], is_(equal_to('user')))

    def test_clean_username_of_existing_user(self):
        mommy.make(User, username='user')

        # The user with proto_user params already exists, hence cannot be created.
        form = UserCreationForm({
            'username': 'user',
            'password1': 'pwd',
            'password2': 'pwd',
        })

        assert_that(not form.is_valid())
        assert_that(form.errors, has_length(1))
        assert_that(form.errors, has_key('username'))
