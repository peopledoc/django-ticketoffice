# -*- coding: utf-8 -*-
"""Custom exceptions."""


class NoTicketError(Exception):
    """No ticket provided."""


class CredentialsError(Exception):
    """No ticket match credentials (uuid, password, place and purpose)."""


class TicketExpiredError(Exception):
    """Ticket found, but expired."""


class TicketUsedError(Exception):
    """Ticket found, but was already used."""
