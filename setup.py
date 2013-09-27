# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

NAME = u'django-ticketoffice'
DESCRIPTION = u'One-shot authentication (invitation) utilities for Django.'
README = open(os.path.join(here, 'README.rst')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()
PACKAGES = ['django_ticketoffice']
REQUIREMENTS = ['Django',
                'django-floppyforms',
                'django-jsonfield',
                'django-qmixin',
                'django-uuidfield',
                'mock',
                'setuptools']
ENTRY_POINTS = {}
AUTHOR = u'Benoît Bryon'
EMAIL = u'benoit@marmelune.net'
URL = u'https://github.com/novapost/django-ticketoffice'
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               "Programming Language :: Python :: 2.7"]
KEYWORDS = []


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
          packages=PACKAGES,
          include_package_data=True,
          zip_safe=False,
          install_requires=REQUIREMENTS,
          entry_points=ENTRY_POINTS)
