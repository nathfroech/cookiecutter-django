{{cookiecutter.project_name}}
{{ '=' * cookiecutter.project_name|length }}

{{cookiecutter.description}}

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style
{% if cookiecutter.open_source_license != "Not open source" %}

:License: {{cookiecutter.open_source_license}}
{% endif %}

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Updating requirements
^^^^^^^^^^^^^^^^^^^^^

Project uses `pip-tools
<https://github.com/jazzband/pip-tools>`_ for requirements management. If you need to add a new requirement, go to
``requirements`` directory and change the corresponding \*.in file. After that call ``make update_requirements`` to
compile \*.txt files and synchronize local environment.

For requirements installation in CI or production environments it is enough to simply call ``pip install -r
requirements/<file_name>.txt``.

For compatibility with traditional project structure there is also ``requirements.txt`` file at project root, which
simply links to ``requirements/production.txt``.

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy {{cookiecutter.project_slug}}

Tests
^^^^^

Project uses ``pytest`` for testing.

All tests should be placed inside ``tests/`` directory of the corresponding project and (ideally) follow the project
structure - for example, tests for models from app ``user`` should be located at ``user/tests/test_models.py`` (or
inside the package ``user/tests/models/``, if there are too many tests).

As an alternative, tests may be placed inside ``tests/`` directory at the project's root (for example, if tests are not
related to any certain app).

For assertions either default python's ``assert`` can be used, or more specific assertions from PyHamcrest_ - may be
useful for complex assertions and just more readable.

.. _PyHamcrest: https://pyhamcrest.readthedocs.io/en/release-1.8/library/

To run tests: ``make test``.
To run tests and receive a coverage statistics: ``make coverage``.

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html

{% if cookiecutter.use_celery == "y" %}

Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd {{cookiecutter.project_slug}}
    celery -A {{cookiecutter.project_slug}}.taskapp worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

{% endif %}
{% if cookiecutter.use_mailhog == "y" %}

Email Server
^^^^^^^^^^^^
{% if cookiecutter.use_docker == 'y' %}
In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server `MailHog`_ with a web interface is available as docker container.

Container mailhog will start automatically when you will run all docker containers.
Please check `cookiecutter-django Docker documentation`_ for more details how to start all containers.

With MailHog running, to view messages that are sent by your application, open your browser and go to ``http://127.0.0.1:8025``
{% else %}
In development, it is often nice to be able to see emails that are being sent from your application. If you choose to use `MailHog`_ when generating the project a local SMTP server with a web interface will be available.

#. `Download the latest MailHog release`_ for your OS.

#. Rename the build to ``MailHog``.

#. Copy the file to the project root.

#. Make it executable: ::

    $ chmod +x MailHog

#. Spin up another terminal window and start it there: ::

    ./MailHog

#. Check out `<http://127.0.0.1:8025/>`_ to see how it goes.

Now you have your own mail server running locally, ready to receive whatever you send it.

.. _`Download the latest MailHog release`: https://github.com/mailhog/MailHog/releases
{% endif %}
.. _mailhog: https://github.com/mailhog/MailHog
{% endif %}
{% if cookiecutter.use_sentry == "y" %}

Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.
{% endif %}

Deployment
----------

The following details how to deploy this application.
{% if cookiecutter.use_heroku.lower() == "y" %}

Heroku
^^^^^^

See detailed `cookiecutter-django Heroku documentation`_.

.. _`cookiecutter-django Heroku documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html
{% endif %}
{% if cookiecutter.use_docker.lower() == "y" %}

Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html
{% endif %}

{% if cookiecutter.custom_bootstrap_compilation == "y" %}
Custom Bootstrap Compilation
^^^^^^

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v4 is installed using npm and customised by tweaking your variables in ``static/sass/custom_bootstrap_vars``.

You can find a list of available variables `in the bootstrap source`_, or get explanations on them in the `Bootstrap docs`_.

{% if cookiecutter.js_task_runner == 'Gulp' %}
Bootstrap's javascript as well as its dependencies is concatenated into a single file: ``static/js/vendors.js``.
{% endif %}

.. _in the bootstrap source: https://github.com/twbs/bootstrap/blob/v4-dev/scss/_variables.scss
.. _Bootstrap docs: https://getbootstrap.com/docs/4.1/getting-started/theming/
{% endif %}
