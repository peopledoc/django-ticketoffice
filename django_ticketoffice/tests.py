# -*- coding: utf-8 -*-
"""Tests."""
from datetime import timedelta
import uuid
import unittest
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock

from django.conf import settings
import django.test
from django.test.utils import override_settings
from django.utils.timezone import now
from django.contrib.auth import hashers

from django_ticketoffice import decorators
from django_ticketoffice import exceptions
from django_ticketoffice import forms
from django_ticketoffice import managers
from django_ticketoffice import models
from django_ticketoffice import utils
from django_ticketoffice.settings import TICKETOFFICE_PASSWORD_GENERATOR


class APITestCase(unittest.TestCase):
    """Test suite around :py:module:`django_ticketoffice` API.

    This test suite mostly guarantees backward compatibility (i.e. make use the
    API does not change unless explicitely desired).

    """
    def test_ticket(self):
        """Import Ticket from django_ticketoffice."""
        from django_ticketoffice import Ticket  # NoQA


class TicketModelTestCase(django.test.TestCase):
    """Test suite around `django_ticketoffice.models.Ticket`."""
    def test_manager(self):
        """Ticket.objects uses custom TicketManager."""
        self.assertTrue(isinstance(models.Ticket.objects,
                                   managers.TicketManager))

    @override_settings(
        TICKETOFFICE_PASSWORD_GENERATOR=TICKETOFFICE_PASSWORD_GENERATOR)
    def test_generate_password(self):
        """Ticket.generate_password return random (clear) password."""
        ticket = models.Ticket()
        self.assertEqual(ticket.password, hashers.UNUSABLE_PASSWORD)
        generate_password_mock = mock.Mock(return_value=mock.sentinel.password)
        with mock.patch('django_ticketoffice.utils.random_password',
                        new=generate_password_mock):
            password = ticket.generate_password()
        self.assertNotEqual(ticket.password, hashers.UNUSABLE_PASSWORD)
        generate_password_mock.assert_called_once_with(
            *TICKETOFFICE_PASSWORD_GENERATOR[1],
            **TICKETOFFICE_PASSWORD_GENERATOR[2])
        self.assertEqual(password, mock.sentinel.password)


class TicketManagerTestCase(django.test.TestCase):
    "Test suite around `django_ticketoffice.managers.TicketManager`."
    def test_defaults(self):
        """Ticket instance is created with expected defaults."""
        ticket = models.Ticket.objects.create()
        self.assertNotEqual(ticket.uuid, u'')
        self.assertEqual(ticket.password, hashers.UNUSABLE_PASSWORD)
        self.assertEqual(ticket.usage_datetime, None)
        self.assertEqual(ticket.expiry_datetime, None)
        self.assertEqual(ticket.place, u'')
        self.assertEqual(ticket.purpose, u'')

    def test_authenticate_success(self):
        """authenticate() returns Ticket instance on success."""
        manager = models.Ticket.objects
        password = u'dummy password'
        original = manager.create()
        original.set_password(password)
        original.save()
        found = manager.authenticate(original.uuid, password)
        self.assertEqual(original, found)

    def test_authenticate_does_not_exist(self):
        """authenticate() raise CredentialsError if Ticket does not exist."""
        manager = models.Ticket.objects
        self.assertRaises(exceptions.CredentialsError,
                          manager.authenticate,
                          u'foo', u'bar')

    def test_authenticate_wrong_password(self):
        """authenticate() raise CredentialsError if password does not match."""
        manager = models.Ticket.objects
        original = manager.create()
        original.set_password(u'right password')
        original.save()
        self.assertRaises(exceptions.CredentialsError,
                          manager.authenticate,
                          original.uuid, u'wrong password')

    def test_authenticate_expired(self):
        """authenticate() raise TicketExpiredError if Ticket expired."""
        manager = models.Ticket.objects
        original = manager.create(
            expiry_datetime=now() - timedelta(days=2))
        password = u'dummy password'
        original.set_password(password)
        original.save()
        self.assertRaises(exceptions.TicketExpiredError,
                          manager.authenticate,
                          original.uuid, password)

    def test_authenticate_not_expired(self):
        """authenticate() succeeds if Ticket has not expired yet."""
        manager = models.Ticket.objects
        original = manager.create(
            expiry_datetime=now() + timedelta(days=2))
        password = u'dummy password'
        original.set_password(password)
        original.save()
        found = manager.authenticate(original.uuid, password)
        self.assertEqual(original, found)

    def test_authenticate_used(self):
        """authenticate() raise TicketUsedError if Ticket has been used."""
        manager = models.Ticket.objects
        original = manager.create(
            usage_datetime=now() - timedelta(days=2))
        password = u'dummy password'
        original.set_password(password)
        original.save()
        self.assertRaises(exceptions.TicketUsedError,
                          manager.authenticate,
                          original.uuid, password)


class TicketAuthenticationFormTestCase(unittest.TestCase):
    """Test suite around
    :py:class:`django_ticketoffice.forms.TicketAuthenticationForm`."""
    def test_clean_success(self):
        """TicketAuthenticationForm is valid if credentials syntax is ok."""
        data = {'uuid': u'foo', 'password': u'bar'}
        form = forms.TicketAuthenticationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_missing_credentials(self):
        """TicketAuthenticationForm requires both uuid and password."""
        form = forms.TicketAuthenticationForm()
        self.assertTrue(form.fields['uuid'].required)
        self.assertTrue(form.fields['password'].required)


class InvitationRequiredTestCase(unittest.TestCase):
    "Tests around :class:`django_ticketoffice.decorators.invitation_required`."
    def setUp(self):
        """Common setup: fake request, stub views, stub user test function."""
        super(InvitationRequiredTestCase, self).setUp()
        # Fake request and its positional and keywords arguments.
        self.request = mock.MagicMock()
        self.request_args = ['fake_arg']
        self.request_kwargs = {'fake': 'kwarg'}
        # Mock user test function.
        self.test_func = mock.MagicMock()
        # Mock unauthorized and forbidden views.
        self.unauthorized_view = mock.MagicMock(
            return_value=u"401 - You may log in.")
        self.forbidden_view = mock.MagicMock(
            return_value=u"403 - Insufficient privileges.")
        # Mock the view to decorate.
        self.authorized_view = mock.MagicMock(
            return_value=u"200 - Greetings, Professor Falken.")

    def run_decorated_view(self, place=u'', purpose=u''):
        """Setup, decorate and call view, then return response."""
        # Get decorator.
        decorator = decorators.invitation_required(
            place=place,
            purpose=purpose)
        decorator.unauthorized = self.unauthorized_view
        decorator.forbidden = self.forbidden_view
        # Decorate view.
        decorated_view = decorator(self.authorized_view)
        # Return response.
        return decorated_view(self.request,
                              *self.request_args,
                              **self.request_kwargs)

    def test_valid_invitation_in_session(self):
        "invitation_required() with valid guest session runs decorated view."
        # Setup.
        place = u'louvre'
        purpose = u'visit'
        fake_uuid = uuid.uuid4()
        invitation = models.Ticket(place=place, purpose=purpose)
        invitation.uuid = fake_uuid
        self.assertTrue(invitation.is_valid())
        self.request.session = {'invitation': invitation}
        self.request.cache = {}
        decorator = decorators.invitation_required(
            place=place,
            purpose=purpose)
        decorator.get_ticket_from_credentials = mock.Mock(
            side_effect=exceptions.NoTicketError)
        decorator.get_ticket_from_session = mock.Mock(
            return_value=invitation)
        # Run.
        response = decorator(self.authorized_view)(self.request,
                                                   *self.request_args,
                                                   **self.request_kwargs)
        # Check.
        self.authorized_view.assert_called_once_with(self.request,
                                                     *self.request_args,
                                                     **self.request_kwargs)
        self.assertEqual(response, self.authorized_view.return_value)
        self.assertFalse(self.unauthorized_view.called)
        self.assertFalse(self.forbidden_view.called)
        self.assertEqual(self.request.cache['invitation'], invitation)

    def test_invalid_invitation_in_session(self):
        "invitation_required() with invalid guest session returns 403."
        # Setup:
        #
        # * fake invitation uuid in session
        # * Ticket.objects.get() returns expired ticket.
        place = u'louvre'
        purpose = u'visit'
        fake_uuid = uuid.uuid4()
        invitation = models.Ticket(place=place, purpose=purpose,
                                   uuid=fake_uuid,
                                   expiry_datetime=now() - timedelta(days=2))
        self.assertFalse(invitation.is_valid())
        decorator = decorators.invitation_required(
            place=place,
            purpose=purpose)
        decorator.get_ticket_from_credentials = mock.Mock(
            side_effect=exceptions.NoTicketError)
        decorator.get_ticket_from_session = mock.Mock(
            return_value=invitation)
        decorator.forbidden = mock.Mock(return_value=mock.sentinel.forbidden)
        request = mock.MagicMock()
        request.session = {}
        # Run.
        response = decorator(self.authorized_view)(request)
        # Check.
        self.assertEqual(response, mock.sentinel.forbidden)
        decorator.get_ticket_from_credentials.assert_called_once_with(request)
        decorator.get_ticket_from_session.assert_called_once_with(request)
        decorator.forbidden.assert_called_once_with(request)

    def test_wrong_place_purpose_invitation_in_session(self):
        "invitation_required() with inappropriate guest session returns 403."
        # Setup:
        #
        # * fake invitation in session
        # * Ticket.objects.get() raises DoesNotExist.
        self.request.session = {'invitation': 'fake uuid'}
        manager_mock = mock.Mock()
        manager_mock.get = mock.Mock(
            side_effect=models.Ticket.DoesNotExist)
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        ticket_mock.DoesNotExist = models.Ticket.DoesNotExist
        with mock.patch('django_ticketoffice.decorators.Ticket',
                        new=ticket_mock):
            # Run.
            response = self.run_decorated_view()
        # Check.
        self.forbidden_view.assert_called_once_with(self.request)
        self.assertEqual(response, self.forbidden_view.return_value)
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.unauthorized_view.called)

    def test_valid_invitation_in_get(self):
        "invitation_required() with valid credentials returns 302."
        # Setup.
        place = u'louvre'
        purpose = u'visit'
        fake_uuid = uuid.uuid4()
        password = u'secret'
        invitation = models.Ticket(place=place, purpose=purpose)
        invitation.uuid = fake_uuid
        invitation.set_password(password)
        self.assertTrue(invitation.is_valid())
        self.request.session = {}
        self.request.GET = mock.MagicMock()
        form_mock = mock.Mock()
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = {'uuid': str(fake_uuid), 'password': password}
        form_class_mock = mock.Mock(return_value=form_mock)
        manager_mock = mock.Mock()
        manager_mock.get = mock.Mock(return_value=invitation)
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.decorators.Ticket',
                        new=ticket_mock):
            with mock.patch('django_ticketoffice.decorators'
                            '.TicketAuthenticationForm', new=form_class_mock):
                # Run.
                response = self.run_decorated_view(place=place,
                                                   purpose=purpose)
        # Check.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.request.session,
                         {'invitation': invitation.uuid})
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.unauthorized_view.called)
        self.assertFalse(self.forbidden_view.called)

    def test_invalid_invitation_in_get(self):
        "invitation_required() with invalid credentials returns 403."
        # Setup.
        self.request.session = {}
        self.request.GET = mock.MagicMock()
        form_mock = mock.Mock()
        form_mock.is_valid.return_value = False
        form_class_mock = mock.Mock(return_value=form_mock)
        with mock.patch('django_ticketoffice.decorators'
                        '.TicketAuthenticationForm', new=form_class_mock):
            # Run.
            response = self.run_decorated_view()
        # Check.
        form_mock.assertCalledOnceWith(mock.sentinel.query_string)
        self.forbidden_view.assert_called_once_with(self.request)
        self.assertEqual(response, self.forbidden_view.return_value)
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.unauthorized_view.called)

    def test_no_invitation_in_get(self):
        "invitation_required() without credentials returns 401."
        # Setup.
        self.request.session = {}
        self.request.GET = {}
        # Run.
        response = self.run_decorated_view()
        # Check.
        self.unauthorized_view.assert_called_once_with(self.request)
        self.assertEqual(response, self.unauthorized_view.return_value)
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.forbidden_view.called)

    def test_run_credentials_error(self):
        """invitation_required.run() calls forbidden() if CredentialsError."""
        decorator = decorators.invitation_required(place=u'', purpose=u'')
        decorator.get_ticket = mock.Mock(
            side_effect=exceptions.CredentialsError)
        decorator.forbidden = mock.Mock()
        decorator.run('fake request')
        decorator.forbidden.assert_called_once_with('fake request')

    def test_run_no_ticket_error(self):
        """invitation_required.run() calls unauthorized() if NoTicketError."""
        decorator = decorators.invitation_required(place=u'', purpose=u'')
        decorator.get_ticket = mock.Mock(side_effect=exceptions.NoTicketError)
        decorator.unauthorized = mock.Mock()
        decorator.run('fake request')
        decorator.unauthorized.assert_called_once_with('fake request')

    def test_run_ticket_used_error(self):
        "invitation_required.run() calls forbidden() if TicketUsedError."
        decorator = decorators.invitation_required(place=u'', purpose=u'')
        decorator.get_ticket = mock.Mock(
            side_effect=exceptions.TicketUsedError)
        decorator.forbidden = mock.Mock()
        decorator.run('fake request')
        decorator.forbidden.assert_called_once_with('fake request')

    def test_run_ticket_expired_error(self):
        "invitation_required.run() calls forbidden() if TicketExpiredError."
        decorator = decorators.invitation_required(place=u'', purpose=u'')
        decorator.get_ticket = mock.Mock(
            side_effect=exceptions.TicketExpiredError)
        decorator.forbidden = mock.Mock()
        decorator.run('fake request')
        decorator.forbidden.assert_called_once_with('fake request')


def SettingsTestCase(self):
    """Test suite around django.conf.settings."""
    def test_password_generator(self):
        """settings.TICKETOFFICE_PASSWORD_GENERATOR has default value."""
        self.assertTrue(settings.TICKETOFFICE_PASSWORD_GENERATOR)

    def test_password_generator_default(self):
        "django_ticketoffice.settings.TICKETOFFICE_PASSWORD_GENERATOR works."
        import_path, args, kwargs = TICKETOFFICE_PASSWORD_GENERATOR
        generator = utils.import_member(import_path)
        password = generator(args, kwargs)
        self.assertTrue(password)
