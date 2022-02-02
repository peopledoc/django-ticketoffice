# -*- coding: utf-8 -*-
"""Python packaging."""
import os
import sys

from setuptools import setup


#: Absolute path to directory containing setup.py file.
here = os.path.abspath(os.path.dirname(__file__))
#: Boolean, ``True`` if environment is running Python version 2.
IS_PYTHON2 = sys.version_info[0] == 2


NAME = 'django-ticketoffice'
DESCRIPTION = 'One-shot authentication (temporary credentials) utilities ' \
              'for Django.'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
AUTHOR = u'Benoît Bryon'
EMAIL = 'benoit@marmelune.net'
URL = 'https://{name}.readthedocs.org/'.format(name=NAME)
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               'License :: OSI Approved :: BSD License',
               'Programming Language :: Python :: 2.7',
               'Framework :: Django']
LICENSE = 'BSD'
KEYWORDS = [
    'authentication',
]
PACKAGES = [NAME.replace('-', '_')]
REQUIREMENTS = [
    'Django>=1.11',
    'psycopg2',
    'setuptools',
]
if IS_PYTHON2:
    REQUIREMENTS.append('mock')
ENTRY_POINTS = {}
SETUP_REQUIREMENTS = []
TEST_REQUIREMENTS = []
CMDCLASS = {}


# Tox integration.
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    """Test command that runs tox."""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # import here, cause outside the eggs aren't loaded.
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


TEST_REQUIREMENTS.append('tox')
CMDCLASS['test'] = Tox


if __name__ == '__main__':  # Do not run setup() when we import this module.
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=README,
        classifiers=CLASSIFIERS,
        keywords=' '.join(KEYWORDS),
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        license=LICENSE,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
        install_requires=REQUIREMENTS,
        entry_points=ENTRY_POINTS,
        tests_require=TEST_REQUIREMENTS,
        cmdclass=CMDCLASS,
        setup_requires=SETUP_REQUIREMENTS,
    )
