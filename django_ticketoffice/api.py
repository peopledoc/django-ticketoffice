"""API shortcuts for use in client applications."""
from django_ticketoffice.exceptions import (
    CredentialsError,
    NoTicketError,
    TicketExpiredError,
    TicketUsedError,
)
from django_ticketoffice.decorators import (
    invitation_required,
    stamp_invitation,
)
from django_ticketoffice.models import Ticket


__all__ = [
    # exceptions
    'CredentialsError',
    'NoTicketError',
    'TicketExpiredError',
    'TicketUsedError',
    # decorators
    'invitation_required',
    'stamp_invitation',
    # models
    'Ticket',
]
