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
DESCRIPTION = 'One-shot authentication (invitation) utilities for Django.'
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
    'Django',
    'django-floppyforms',
    'django-jsonfield',
    'django-qmixin',
    'django-uuidfield>=0.5',
    'setuptools',
]
if IS_PYTHON2:
    REQUIREMENTS.append('mock')
ENTRY_POINTS = {}


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
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
          entry_points=ENTRY_POINTS)
