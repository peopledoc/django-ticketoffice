# -*- coding: utf-8 -*-
"""API shortcuts for use in client applications."""
from django_ticketoffice.decorators import (invitation_required,  # NoQA
                                            stamp_invitation)
from django_ticketoffice.exceptions import *  # NoQA
from django_ticketoffice.models import Ticket  # NoQA
