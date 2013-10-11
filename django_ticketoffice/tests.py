# -*- coding: utf-8 -*-
"""Tests."""
from datetime import timedelta
import uuid
import unittest
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock

import django.test
from django.utils.timezone import now
from django.contrib.auth import hashers

from django_ticketoffice import decorators
from django_ticketoffice import exceptions
from django_ticketoffice import forms
from django_ticketoffice import managers
from django_ticketoffice import models


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
        """clean() pass if credentials match Ticket."""
        manager_mock = mock.Mock()
        manager_mock.authenticate = mock.Mock(return_value=u'foo')
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.forms.Ticket',
                        new=ticket_mock):
            form = forms.TicketAuthenticationForm(data={'uuid': u'foo',
                                                        'password': u'bar'})
            self.assertTrue(form.is_valid())

    def test_credentials_error(self):
        """clean() fail if Ticket manager raises CredentialsError."""
        manager_mock = mock.Mock()
        manager_mock.authenticate = mock.Mock(
            side_effect=exceptions.CredentialsError())
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.forms.Ticket',
                        new=ticket_mock):
            form = forms.TicketAuthenticationForm(data={'uuid': u'foo',
                                                        'password': u'bar'})
            self.assertFalse(form.is_valid())

    def test_used_error(self):
        """clean() fail if Ticket manager raises TicketUsedError."""
        manager_mock = mock.Mock()
        manager_mock.authenticate = mock.Mock(
            side_effect=exceptions.TicketUsedError())
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.forms.Ticket',
                        new=ticket_mock):
            form = forms.TicketAuthenticationForm(data={'uuid': u'foo',
                                                        'password': u'bar'})
            self.assertFalse(form.is_valid())

    def test_expired_error(self):
        """clean() fail if Ticket manager raises TicketExpiredError."""
        manager_mock = mock.Mock()
        manager_mock.authenticate = mock.Mock(
            side_effect=exceptions.TicketExpiredError())
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.forms.Ticket',
                        new=ticket_mock):
            form = forms.TicketAuthenticationForm(data={'uuid': u'foo',
                                                        'password': u'bar'})
            self.assertFalse(form.is_valid())


class InvitationRequiredTestCase(unittest.TestCase):
    """Tests around
    :py:func:`django_ticketoffice.decorators.invitation_required`."""
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
        # Custom setup.

        # Get decorator.
        decorator = decorators.invitation_required(
            place=place,
            purpose=purpose,
            unauthorized=self.unauthorized_view,
            forbidden=self.forbidden_view)
        # Decorate view.
        decorated_view = decorator(self.authorized_view)
        # Return response.
        return decorated_view(self.request,
                              *self.request_args,
                              **self.request_kwargs)

    def test_valid_invitation_in_session(self):
        "invitation_required() with valid guest session runs decorated view."
        # Setup:
        #
        # * fake invitation uuid in session
        # * Ticket.objects.get() returns valid ticket.
        place = u'louvre'
        purpose = u'visit'
        fake_uuid = uuid.uuid4()
        invitation = models.Ticket(place=place, purpose=purpose)
        invitation.uuid = fake_uuid
        self.assertTrue(invitation.is_valid())
        self.request.session = {'invitation': invitation}
        self.request.cache = {}
        manager_mock = mock.Mock()
        manager_mock.get = mock.Mock(return_value=invitation)
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.decorators.Ticket',
                        new=ticket_mock):
            # Run.
            response = self.run_decorated_view(place=place, purpose=purpose)
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
        invitation = models.Ticket(place=place, purpose=purpose,
                                   expiry_datetime=now() - timedelta(days=2))
        self.assertFalse(invitation.is_valid())
        fake_uuid = 'uuid'
        self.request.session = {'invitation': fake_uuid}
        manager_mock = mock.Mock()
        manager_mock.get = mock.Mock(return_value=invitation)
        ticket_mock = mock.Mock()
        ticket_mock.objects = manager_mock
        with mock.patch('django_ticketoffice.decorators.Ticket',
                        new=ticket_mock):
            # Run.
            response = self.run_decorated_view(place=place, purpose=purpose)
        # Check.
        self.forbidden_view.assert_called_once_with(self.request)
        manager_mock.get.assert_called_once_with(uuid=fake_uuid,
                                                 place=place, purpose=purpose)
        self.assertEqual(response, self.forbidden_view.return_value)
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.unauthorized_view.called)

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
        invitation = models.Ticket(place=place, purpose=purpose)
        invitation.uuid = fake_uuid
        self.assertTrue(invitation.is_valid())
        self.request.session = {}
        self.request.GET = mock.sentinel.query_string
        form_mock = mock.Mock()
        form_mock.is_valid.return_value = True
        form_mock.instance = invitation
        form_class_mock = mock.Mock(return_value=form_mock)
        with mock.patch('django_ticketoffice.decorators'
                        '.TicketAuthenticationForm', new=form_class_mock):
            # Run.
            response = self.run_decorated_view(place=place, purpose=purpose)
        # Check.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.request.session, {'invitation': invitation.uuid})
        self.assertFalse(self.authorized_view.called)
        self.assertFalse(self.unauthorized_view.called)
        self.assertFalse(self.forbidden_view.called)

    def test_invalid_invitation_in_get(self):
        "invitation_required() with invalid credentials returns 403."
        # Setup.
        self.request.session = {}
        self.request.GET = mock.sentinel.query_string
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
