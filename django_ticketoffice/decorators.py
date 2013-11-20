# -*- coding: utf-8 -*-
"""View decorators."""
from functools import wraps

from django.utils.decorators import available_attrs

from django_ticketoffice import exceptions
from django_ticketoffice.forms import TicketAuthenticationForm
from django_ticketoffice.models import Ticket, GuestUser
from django_ticketoffice.utils import (UnauthorizedView, ForbiddenView,
                                       Decorator)


unauthorized_view = UnauthorizedView.as_view(
    template_name='invitation/401.html')


forbidden_view = ForbiddenView.as_view(
    template_name='invitation/403.html')


def guest_login(request, invitation):
    """Perform guest login in request."""
    # Cache the invitation instance in request.
    try:
        request.cache['invitation'] = invitation
    except AttributeError:
        setattr(request, 'cache', {'invitation': invitation})
    request.user = GuestUser(invitation=invitation, invitation_valid=True)
    try:
        request.user.id = invitation.data['user']
    except KeyError:
        pass


class invitation_required(Decorator):
    """Make sure invitation is provided for place and purpose.

    Here is the invitation validation scenario:

    1. If session holds a valid `invitation` instance, run decorated view.

    2. If session holds invalid (expired, used...) `invitation`, return
       `forbidden` view.

    3. If session does not hold `invitation`, looks for credentials passed in
       request's query string (GET arguments)...

       * if there are no credentials, return `unauthorized` view

       * if credentials match an invitation:

         * store invitation in session;
         * redirect to same URL (go to cases 1/ or 2/).

       * else return `forbidden` view.

    Additional arguments `place` and `purpose` are required to filter
    invitations. User is invitated somewhere (place) to do something (purpose).

    """
    def __init__(self, place, purpose):
        Decorator.__init__(self, func=Decorator.UNDEFINED_FUNCTION)
        self.place = place
        self.purpose = purpose

    def run(self, request, *args, **kwargs):
        try:
            self.get_ticket(request)
        except exceptions.NoTicketError:
            return self.unauthorized(request)
        except (exceptions.CredentialsError,
                exceptions.TicketUsedError,
                exceptions.TicketExpiredError):
            return self.forbidden(request)
        return self.valid(request, *args, **kwargs)

    def get_ticket(self, request):
        """Return ticket instance for ``request``."""
        try:
            invitation_uuid = request.session['invitation']
        except KeyError:  # No ticket in session, check credentials.
            if request.GET:
                form = TicketAuthenticationForm(data=request.GET,
                                                place=self.place,
                                                purpose=self.purpose)
                if form.is_valid():
                    # Support UUID with dashes. In DB, UUID has no dashes.
                    data = form.cleaned_data
                    if '-' in data['uuid']:
                        data['uuid'] = data['uuid'].replace('-', '')
                    try:
                        self.ticket = Ticket.objects.get(uuid=data['uuid'],
                                                         place=self.place,
                                                         purpose=self.purpose)
                    except Ticket.DoesNotExist:
                        raise exceptions.CredentialsError(
                            'No ticket with UUID="{uuid}" for place="{place}" '
                            'and purpose="{purpose}" in database.'
                            .format(
                                uuid=data['uuid'],
                                place=self.place,
                                purpose=self.purpose))
                    # Check password.
                    if not self.ticket.authenticate(data['password']):
                        raise exceptions.CredentialsError(
                            'Wrong password for ticket with UUID="{uuid}"'
                            .format(uuid=self.ticket.uuid))
                else:
                    raise exceptions.CredentialsError('Invalid credentials.')
            else:
                raise exceptions.NoTicketError('Missing ticket.')
        else:  # Ticket in session: credentials have already been checked.
            try:
                self.ticket = Ticket.objects.get(uuid=invitation_uuid,
                                                 place=self.place,
                                                 purpose=self.purpose)
            except Ticket.DoesNotExist:
                raise exceptions.CredentialsError(
                    'Ticket {uuid} in session no longer exists in database.'
                    .format(uuid=invitation_uuid))
        # Check usage.
        if self.ticket.used:
            raise exceptions.TicketUsedError(
                'Ticket with UUID="{uuid}" was used at {date}'.format(
                    uuid=self.ticket.uuid,
                    date=self.ticket.usage_datetime))
        # Check expiry.
        if self.ticket.expired:
            raise exceptions.TicketExpiredError(
                'Ticket with UUID="{uuid}" expired at {date}'.format(
                    uuid=self.ticket.uuid,
                    date=self.ticket.expiry_datetime))
        return self.ticket

    def unauthorized(self, request, *args, **kwargs):
        """Return response when credentials are missing (no invitation)."""
        return unauthorized_view(request)

    def forbidden(self, request, *args, **kwargs):
        """Return response when ticket is not valid (expired, used, wrong
        credentials)."""
        return forbidden_view(request)

    def login(self, request, *args, **kwargs):
        """Log the user in when ticket is valid."""
        # Cache the invitation instance in session.
        request.session['invitation'] = self.ticket.uuid
        return guest_login(request, self.ticket)

    def valid(self, request, *args, **kwargs):
        """Return response when ticket is valid."""
        self.login(request, *args, **kwargs)
        return Decorator.run(self, request, *args, **kwargs)


def stamp_invitation(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        # Execute view function.
        response = view_func(request, *args, **kwargs)
        # Stamp ticket if available.
        try:
            invitation = request.cache['invitation']
        except (AttributeError, KeyError):
            raise  # Invitation not request! Missing @invitation_required?
        invitation.use()
        return response
    return _wrapped_view
