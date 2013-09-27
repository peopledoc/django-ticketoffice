# -*- coding: utf-8 -*-
"""Managers for models."""
from djqmixin import Manager, QMixin

from django_ticketoffice import exceptions


class CredentialsMixin(QMixin):
    def authenticate(self, uuid, clear_password, place=u'', purpose=u''):
        try:
            ticket = self.get(uuid=uuid, place=place, purpose=purpose)
        except self.model.DoesNotExist:
            raise exceptions.CredentialsError(
                'No ticket with UUID "{uuid}" for place "{place}" and purpose '
                '"{purpose}"'.format(uuid=uuid, place=place, purpose=purpose))
        # Check usage.
        if ticket.used:
            raise exceptions.TicketUsedError(
                'Ticket with UUID {uuid} was used at {date}'.format(
                    uuid=ticket.uuid,
                    date=ticket.usage_datetime))
        # Check expiry.
        if ticket.expired:
            raise exceptions.TicketExpiredError(
                'Ticket with UUID {uuid} expired at {date}'.format(
                    uuid=ticket.uuid,
                    date=ticket.expiry_datetime))
        # Check password.
        if not ticket.authenticate(clear_password):
            raise exceptions.CredentialsError(
                'Wrong password for UUID {uuid}'.format(uuid=ticket.uuid))
        # Alright, return ticket.
        return ticket


#: Manager for :py:class:`django_ticketoffice.models.Ticket`.
TicketManager = Manager.include(CredentialsMixin)
