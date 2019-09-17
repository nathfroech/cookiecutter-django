from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ul


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _ul('username'),
        max_length=150,
        unique=True,
        help_text=_ul('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _ul('A user with that username already exists.'),
        },
    )
    first_name = models.CharField(_ul('first name'), max_length=30, blank=True)
    last_name = models.CharField(_ul('last name'), max_length=150, blank=True)
    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_ul('name of user'), max_length=255, blank=True)

    email = models.EmailField(_ul('email address'), blank=True)

    is_staff = models.BooleanField(
        _ul('staff status'),
        default=False,
        help_text=_ul('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _ul('active'),
        default=True,
        help_text=_ul(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.',
        ),
    )
    date_joined = models.DateTimeField(_ul('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _ul('user')
        verbose_name_plural = _ul('users')

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        if self.name:
            return self.name
        else:
            full_name = '{0} {1}'.format(self.first_name, self.last_name)
            return full_name.strip()

    @property
    def short_name(self) -> str:
        """Return the short name for the user."""
        return self.first_name or self.name

    def email_user(self, subject: str, message: str, from_email: Optional[str] = None, **kwargs) -> None:
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('users:detail', kwargs={'username': self.username})
