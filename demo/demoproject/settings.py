# -*- coding: utf-8 -*-
"""Django settings.

.. warning::

   These settings are made for development environment.
   They are not safe in production!

"""
import os


here = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(here))
data_dir = os.path.join(root_dir, 'var')
cfg_dir = os.path.join(root_dir, 'etc')


# Applications, dependencies.
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    # Third-parties.
    'django_nose',
    'floppyforms',
    # Project's.
    'django_ticketoffice',
]


# Databases.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(data_dir, 'database.sqlite3'),
    }
}


# URL configuration.
ROOT_URLCONF = '{package}.urls'.format(package=__package__)


# Fake secret key.
SECRET_KEY = 'Fake secret.'


# Use django-nose.
INSTALLED_APPS = list(INSTALLED_APPS) + [
    'django_nose',
]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
nose_cfg_dir = os.path.join(cfg_dir, 'nose')
NOSE_ARGS = [
    '--verbosity=2',
    '--nocapture',
    '--rednose',
    '--no-path-adjustment',
    '--all-modules',
    '--cover-inclusive',
    '--cover-tests',
]

# Disable password hashing for better performances.
# Enable this feature on demand with @django.test.override_settings() or
# @django.test.TestCase.settings() decorators in tests.
PASSWORD_HASHERS = (
    'django_ticketoffice.utils.PlainPasswordHasher',
)