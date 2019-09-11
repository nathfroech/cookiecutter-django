{% if cookiecutter.use_celery == 'y' -%}

from celery import Celery

from django.apps import AppConfig, apps

from config.prepare_environment import prepare_environment

prepare_environment()


app = Celery('{{cookiecutter.project_slug}}')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


class CeleryAppConfig(AppConfig):
    name = '{{cookiecutter.project_slug}}.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)
{% else %}
# Use this as a starting point for your project with celery.
# If you are not using celery, you can remove this app
{% endif -%}
