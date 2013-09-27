###################
django-ticketoffice
###################

`django-ticketoffice` provides one-shot authentication utilities for Django.
Typical usage is invitation tickets.

.. warning:: This project is experimental.


*******
Example
*******

Restrict some URL to guests with valid invitation tickets:

.. code:: python

   from django.conf.urls import patterns, url
   from django_ticketoffice.decorators import invitation_required, stamp_invitation

   @invitation_required(place=u'louvre', purpose=u'visit')
   @stamp_invitation  # Mark invitation as used right **after** view execution.
   def visit_louvre(request):
       ticket = request.cache['invitation']  # Set by `invitation_required`.
       return u'Welcome to the Louvre museum {guest}'.format(
           guest=ticket.data['first_name'])

   urlpatterns = patterns('', url('^louvre$', visit_louvre, name='louvre'))

Create and deliver tickets for this resource:

.. code:: python

   from django.utils.timezone import now
   from django_ticketoffice.models import Ticket

   ticket = Ticket(place=u'louvre', purpose=u'visit')
   ticket.set_password(u'I love Paris')  # Encrypted in database.
   ticket.expiry_datetime = now() + timedelta(days=5)  # Optional.
   ticket.data = {'first_name': u'Léonard'}  # Optional.
   ticket.save()

   credentials = {'uuid': ticket.uuid, 'password': u'I love Paris'}
   visit_url = reverse('louvre') + '?' + urlencode(credentials)

`django-ticketoffice` focuses on authentication. It does not send invitation
emails.


*********
Resources
*********

* Code repository: https://github.com/novapost/django-ticketoffice
