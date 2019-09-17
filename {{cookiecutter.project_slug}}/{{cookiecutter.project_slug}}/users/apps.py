from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = '{{ cookiecutter.project_slug }}.users'
    verbose_name = 'Users'
