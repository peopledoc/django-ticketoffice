# -*- coding: utf-8 -*-
"""Managers for models."""
from django.db.models import Manager
from django.core.exceptions import ValidationError

from django_ticketoffice import exceptions


class TicketManager(Manager):

    def authenticate(self, uuid, clear_password, place=u'', purpose=u''):
        try:
            ticket = self.get(uuid=uuid, place=place, purpose=purpose)
        except self.model.DoesNotExist:
            raise exceptions.CredentialsError(
                f'No ticket with UUID "{uuid}" for place "{place}" and '
                f'purpose "{purpose}"')
        except (ValueError, ValidationError):
            raise exceptions.CredentialsError(
                f'Invalid UUID format for {uuid}')
        # Check password.
        if not ticket.authenticate(clear_password):
            raise exceptions.CredentialsError(
                f'Wrong password for UUID {ticket.uuid}')
        # Check usage.
        if ticket.used:
            raise exceptions.TicketUsedError(
                f'Ticket with UUID {ticket.uuid} was used '
                f'at {ticket.usage_datetime}')
        # Check expiry.
        if ticket.expired:
            raise exceptions.TicketExpiredError(
                f'Ticket with UUID {ticket.uuid} expired '
                f'at {ticket.expiry_datetime}')
        # Alright, return ticket.
        return ticket
