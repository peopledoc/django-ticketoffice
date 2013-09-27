# -*- coding: utf-8 -*-
"""Forms."""
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms

from django_ticketoffice import exceptions
from django_ticketoffice.models import Ticket


class TicketAuthenticationForm(forms.Form):
    """Check ticket credentials."""
    uuid = forms.CharField(label=_(u'Unique ID'), max_length=128)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'wrong_credentials': _("Invitation matching credentials does not "
                               "exist."),
        'ticket_expired': _("Invitation expired."),
        'ticket_used': _("Invitation has already been used."),
    }

    def __init__(self, place=u'', purpose=u'', *args, **kwargs):
        self.place = place
        self.purpose = purpose
        super(TicketAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        """Raise ValidationError if ticket is not valid."""
        uuid = self.cleaned_data.get('uuid', None)
        password = self.cleaned_data.get('password', None)
        if uuid and password:
            try:
                self.instance = Ticket.objects.authenticate(uuid, password,
                                                            self.place,
                                                            self.purpose)
            except exceptions.CredentialsError:
                raise forms.ValidationError(
                    self.error_messages['wrong_credentials'])
            except exceptions.TicketExpiredError:
                raise forms.ValidationError(
                    self.error_messages['ticket_expired'])
            except exceptions.TicketUsedError:
                raise forms.ValidationError(
                    self.error_messages['ticket_used'])
