import os
import sys

try:
    from setuptools import setup  # noqa: WPS433
except ImportError:
    from distutils.core import setup  # noqa: WPS433

# Our version ALWAYS matches the version of Django we support
# If Django has a new release, we branch, tag, then update this setting after the tag.
version = '2.0.2'

if sys.argv[-1] == 'tag':
    os.system('git tag -a {0} -m "version {0}"'.format(version))  # noqa: S605
    os.system('git push --tags')  # noqa: S605,S607
    sys.exit()

with open('README.rst') as readme_file:
    long_description = readme_file.read()

setup(
    name='cookiecutter-django',
    version=version,
    description='A Cookiecutter template for creating production-ready Django projects quickly.',
    long_description=long_description,
    author='Daniel Roy Greenfeld',
    author_email='pydanny@gmail.com',
    url='https://github.com/pydanny/cookiecutter-django',
    packages=[],
    license='BSD',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
    ],
    keywords=(
        'cookiecutter, Python, projects, project templates, django, '
        'skeleton, scaffolding, project directory, setup.py'
    ),
)
