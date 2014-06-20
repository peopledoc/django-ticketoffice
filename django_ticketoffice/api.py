# -*- coding: utf-8 -*-
"""API shortcuts for use in client applications."""
from django_ticketoffice.exceptions import NoTicketError  # NoQA
from django_ticketoffice.exceptions import CredentialsError  # NoQA
from django_ticketoffice.exceptions import TicketExpiredError  # NoQA
from django_ticketoffice.exceptions import TicketUsedError  # NoQA
from django_ticketoffice.models import Ticket  # NoQA
from django_ticketoffice.decorators import invitation_required  # NoQA
from django_ticketoffice.decorators import stamp_invitation  # NoQA
