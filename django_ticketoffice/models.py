# -*- coding: utf-8 -*-
"""Models."""
from functools import partial
from uuid import uuid4

from django.db import models
from django.utils.timezone import now
from django.contrib.auth import hashers
from django.contrib.auth.models import AnonymousUser

from jsonfield import JSONField

from django_ticketoffice.managers import TicketManager
from django_ticketoffice import settings
from django_ticketoffice.utils import import_member


class Ticket(models.Model):
    """Tickets are generic one-shot credentials."""
    #: Unique identifier for the ticket.
    uuid = models.UUIDField(default=uuid4)

    #: Encrypted password for the ticket.
    password = models.CharField(max_length=255,
                                default=partial(hashers.make_password, None))

    #: Location where the ticket is to be used.
    place = models.CharField(max_length=50, blank=True, db_index=True)

    #: Purpose of the ticket, i.e. what does the invitation grant access to.
    purpose = models.CharField(max_length=50, blank=True, db_index=True)

    #: Data relative to the ticket.
    #: Serialized as JSON.
    data = JSONField()

    #: Date and time when the ticket was created.
    creation_datetime = models.DateTimeField(auto_now_add=True,
                                             db_index=True)

    #: Date and time until when the ticket is valid.
    #: ``None`` means no deadline.
    expiry_datetime = models.DateTimeField(null=True,
                                           blank=True,
                                           db_index=True,
                                           default=None)

    #: Date and time when the ticket was used, None if not used.
    usage_datetime = models.DateTimeField(null=True,
                                          blank=True,
                                          db_index=True,
                                          default=None)

    objects = TicketManager()

    def set_password(self, clear_password):
        """Encrypt and set password.

        Does not save the instance.

        """
        self.password = hashers.make_password(clear_password)

    def generate_password(self):
        """Generate password, set :py:attr:`password` and return clear value.

        Uses ``settings.TICKETOFFICE_PASSWORD_GENERATOR``.

        Does not save the instance.

        """
        import_path, args, kwargs = settings.TICKETOFFICE_PASSWORD_GENERATOR
        generator = import_member(import_path)
        clear_password = generator(*args, **kwargs)
        self.set_password(clear_password)
        return clear_password

    def authenticate(self, clear_password):
        """Return `True` if encrypted password matches `clear_password`."""
        return hashers.check_password(clear_password, self.password)

    def is_valid(self):
        """Return True if ticket is neither used nor expired."""
        return not (self.used or self.expired)

    def is_appropriate(self, place, purpose):
        """Return True if ticket matches `place` and `purpose`.

        >>> ticket = Ticket(place=u'library', purpose=u'read')
        >>> ticket.is_appropriate(u'library', u'read')
        True
        >>> ticket.is_appropriate(u'library', u'shout')
        False

        """
        return (place, purpose) == (self.place, self.purpose)

    @property
    def used(self):
        """Return True if ticket was used."""
        return self.usage_datetime is not None

    @property
    def expired(self):
        """Return True if ticket expired."""
        return self.expiry_datetime and self.expiry_datetime < now()

    def use(self):
        """Mark the ticket as used and save it."""
        self.usage_datetime = now()
        self.save()


class GuestUser(AnonymousUser):
    """Anonymous user who can authenticate with invitation ticket."""
    def __init__(self, invitation=None, invitation_valid=False):
        self.invitation = invitation
        self.invitation_valid = invitation_valid
        super(GuestUser, self).__init__()

    def is_authenticated(self):
        return self.invitation is not None and self.invitation_valid
