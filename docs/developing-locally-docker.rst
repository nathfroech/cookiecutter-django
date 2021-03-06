Getting Up and Running Locally With Docker
==========================================

.. index:: Docker

The steps below will get you up and running with a local development environment.
All of these commands assume you are in the root of your generated project.


Prerequisites
-------------

* Docker; if you don't have it yet, follow the `installation instructions`_;
* Docker Compose; refer to the official documentation for the `installation guide`_.

.. _`installation instructions`: https://docs.docker.com/install/#supported-platforms
.. _`installation guide`: https://docs.docker.com/compose/install/


Build the Stack
---------------

This can take a while, especially the first time you run this particular command on your development system::

    $ docker-compose -f local.yml build

Generally, if you want to emulate production environment use ``production.yml`` instead. And this is true for any other actions you might need to perform: whenever a switch is required, just do it!


Run the Stack
-------------

This brings up both Django and PostgreSQL. The first time it is run it might take a while to get started, but subsequent runs will occur quickly.

Open a terminal at the project root and run the following for local development::

    $ docker-compose -f local.yml up

You can also set the environment variable ``COMPOSE_FILE`` pointing to ``local.yml`` like this::

    $ export COMPOSE_FILE=local.yml

And then run::

    $ docker-compose up

To run in a detached (background) mode, just::

    $ docker-compose up -d


Execute Management Commands
---------------------------

As with any shell command that we wish to run in our container, this is done using the ``docker-compose -f local.yml run --rm`` command: ::

    $ docker-compose -f local.yml run --rm django python manage.py migrate
    $ docker-compose -f local.yml run --rm django python manage.py createsuperuser

Here, ``django`` is the target service we are executing the commands against.


(Optionally) Designate your Docker Development Server IP
--------------------------------------------------------

When ``DEBUG`` is set to ``True``, the host is validated against ``['localhost', '127.0.0.1', '[::1]']``. This is adequate when running a ``virtualenv``. For Docker, in the ``config.settings``, add your host development server IP to ``INTERNAL_IPS`` or ``ALLOWED_HOSTS`` if the variable exists.


.. _envs:

Configuring the Environment
---------------------------

This is the excerpt from your project's ``local.yml``: ::

  # ...

  postgres:
    build:
      context: .
      dockerfile: ./compose/production/postgres/Dockerfile
    volumes:
      - local_postgres_data:/var/lib/postgresql/data
      - local_postgres_data_backups:/backups
    env_file:
      - ./.envs/.local

  # ...

The most important thing for us here now is ``env_file`` section enlisting ``./.envs/.local``. Generally, the stack's behavior is governed by a number of environment variables (`env(s)`, for short) residing in ``envs/``, for instance, this is what we generate for you: ::

    .envs
    ├── .local
    └── .production

By convention, for services in environment ``e`` (you know ``someenv`` is an environment when there is a ``someenv.yml`` file in the project root), given that any service requires configuration, a ``.envs/.e`` file exists (it contains configurations for all services).

Consider the aforementioned ``.envs/.local``: ::

    # PostgreSQL
    # ------------------------------------------------------------------------------
    POSTGRES_HOST=postgres
    POSTGRES_DB=<your project slug>
    POSTGRES_USER=XgOWtQtJecsAbaIyslwGvFvPawftNaqO
    POSTGRES_PASSWORD=jSljDz4whHuwO3aJIgVBrqEml5Ycbghorep4uVJ4xjDYQu0LfuTZdctj7y0YcCLu

The three envs we are presented with here are ``POSTGRES_DB``, ``POSTGRES_USER``, and ``POSTGRES_PASSWORD`` (by the way, their values have also been generated for you). You might have figured out already where these definitions will end up; it's all the same with ``django`` service container envs.

One final touch: you may also need to copy ``.envs/.production`` as an ``.env`` file at project root: ::

    $ cp .envs/.production .env

Tips & Tricks
-------------

Activate a Docker Machine
~~~~~~~~~~~~~~~~~~~~~~~~~

This tells our computer that all future commands are specifically for the dev1 machine. Using the ``eval`` command we can switch machines as needed.::

    $ eval "$(docker-machine env dev1)"

Debugging
~~~~~~~~~

ipdb
"""""

If you are using the following within your code to debug: ::

    import ipdb; ipdb.set_trace()

Then you may need to run the following for it to work as desired: ::

    $ docker-compose -f local.yml run --rm --service-ports django


django-debug-toolbar
""""""""""""""""""""

In order for ``django-debug-toolbar`` to work designate your Docker Machine IP with ``INTERNAL_IPS`` in ``settings.py``.


Mailhog
~~~~~~~

When developing locally you can go with MailHog_ for email testing provided ``use_mailhog`` was set to ``y`` on setup. To proceed,

#. make sure ``mailhog`` container is up and running;

#. open up ``http://127.0.0.1:8025``.

.. _Mailhog: https://github.com/mailhog/MailHog/

.. _`CeleryTasks`:

Celery tasks in local development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When not using docker Celery tasks are set to run in Eager mode, so that a full stack is not needed. When using docker the task
scheduler will be used by default.

If you need tasks to be executed on the main thread during development set CELERY_TASK_ALWAYS_EAGER = True in config/settings.py.

Possible uses could be for testing, or ease of profiling with DJDT.

.. _`CeleryFlower`:

Celery Flower
~~~~~~~~~~~~~

`Flower`_ is a "real-time monitor and web admin for Celery distributed task queue".

Prerequisites:

* ``use_docker`` was set to ``y`` on project initialization;
* ``use_celery`` was set to ``y`` on project initialization.

By default, it's enabled both in local and production environments (``local.yml`` and ``production.yml`` Docker Compose configs, respectively) through a ``flower`` service. For added security, ``flower`` requires its clients to provide authentication credentials specified as the corresponding environments' ``.envs/.local`` and ``.envs/.production`` ``CELERY_FLOWER_USER`` and ``CELERY_FLOWER_PASSWORD`` environment variables. Check out ``localhost:5555`` and see for yourself.

.. _`Flower`: https://github.com/mher/flower
