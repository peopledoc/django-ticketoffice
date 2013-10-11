# -*- coding: utf-8 -*-
"""One-shot authentication service."""
import pkg_resources


#: Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


# API shortcuts.
from django_ticketoffice.api import *  # NoQA
