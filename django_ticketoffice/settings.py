# -*- coding: utf-8 -*-
"""Configuration."""
from django.conf import settings


# Set default value for ``settings.TICKETOFFICE_PASSWORD_GENERATOR``.
#: Password generator used by
#: :py:meth:`django_ticketoffice.models.Ticket.generate_password`.
#:
#: It is a list where:
#:
#: * first item is import path to generator callable;
#: * second item is list of positional arguments, i.e. ``*args``;
#: * third item is list of keyword arguments, i.e. ``*args``;
TICKETOFFICE_PASSWORD_GENERATOR = settings.__dict__.setdefault(
    'TICKETOFFICE_PASSWORD_GENERATOR',
    ('django_ticketoffice.utils.random_password',
     [],
     {'min_length': 12, 'max_length': 20})
)
