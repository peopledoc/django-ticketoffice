"""Forms."""
import uuid

from django.utils.translation import gettext_lazy as _

from django import forms


class TicketAuthenticationForm(forms.Form):
    """Check ticket credentials."""
    uuid = forms.CharField(label=_('Unique ID'), max_length=128)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'wrong_credentials': _("Invitation matching credentials does not "
                               "exist."),
        'ticket_expired': _("Invitation expired."),
        'ticket_used': _("Invitation has already been used."),
    }

    def __init__(self, place='', purpose='', *args, **kwargs):
        self.place = place
        self.purpose = purpose
        super().__init__(*args, **kwargs)

    def clean_uuid(self):
        try:
            return uuid.UUID(self.cleaned_data['uuid'])
        except ValueError:
            raise forms.ValidationError(_('Invalid UUID'))
