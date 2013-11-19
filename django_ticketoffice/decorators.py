# -*- coding: utf-8 -*-
"""View decorators."""
from functools import wraps

from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs

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
    def __init__(self,
                 place,
                 purpose,
                 unauthorized=unauthorized_view,
                 forbidden=forbidden_view,
                 login=guest_login):
        Decorator.__init__(self, func=Decorator.UNDEFINED_FUNCTION)
        self.place = place
        self.purpose = purpose
        self.unauthorized = unauthorized
        self.forbidden = forbidden
        self.login = login

    def run(self, request, *args, **kwargs):
        try:
            invitation_uuid = request.session['invitation']
        except KeyError:  # No invitation in session, check credentials.
            if request.GET:
                data = request.GET.dict()
                if '-' in data['uuid']:
                    # Support UUID with dashes.
                    # In DB, UUID has no dashes.
                    data['uuid'] = data['uuid'].replace('-', '')
                form = TicketAuthenticationForm(data=data,
                                                place=self.place,
                                                purpose=self.purpose)
                if form.is_valid():
                    invitation = form.instance
                    # Start guest session.
                    request.session['invitation'] = invitation.uuid
                    return HttpResponseRedirect(request.path)
                else:
                    return self.forbidden(request)
            else:
                return self.unauthorized(request)
        try:
            invitation = Ticket.objects.get(uuid=invitation_uuid,
                                            place=self.place,
                                            purpose=self.purpose)
        except Ticket.DoesNotExist:
            return self.forbidden(request)
        if not invitation.is_valid():
            return self.forbidden(request)
        self.login(request, invitation)
        # At last, return the "normal" view.
        return super(invitation_required, self).run(request, *args, **kwargs)


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
