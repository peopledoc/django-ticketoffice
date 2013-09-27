# -*- coding: utf-8 -*-
"""Custom exceptions."""


class CredentialsError(Exception):
    """No ticket match credentials (uuid, password, place and purpose)."""


class TicketExpiredError(Exception):
    """Ticket found, but expired."""


class TicketUsedError(Exception):
    """Ticket found, but was already used."""
