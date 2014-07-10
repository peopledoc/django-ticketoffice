###################
django-ticketoffice
###################

`django-ticketoffice` provides one-shot authentication (a.k.a. temporary
credentials) utilities for Django.
It lets you create and manage tickets that allow users to perform one action
on the website. As an example, Django could use it for the "password reset"
action, where users authenticate using a temporary token.


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
emails. You may check `django-mail-factory`_ about sending emails.


**************
Project status
**************

`django-ticketoffice` is, at the moment, a proof-of-concept: it delivers basic
features in order to create tickets and to use them in views. It works (you
can use it), but it may lack some features (ideas are welcome), and it may
change (improve) quite a bit. That said, maintainers will take care of release
notes and migrations.

See also `vision`_, `roadmap`_ and `alternatives`_ to get a better overview of
project status.


*********
Resources
*********

* Documentation: https://django-ticketoffice.readthedocs.org
* PyPI page: http://pypi.python.org/pypi/django-ticketoffice
* Code repository: https://github.com/novapost/django-ticketoffice
* Bugtracker: https://github.com/novapost/django-ticketoffice/issues
* Continuous integration: https://travis-ci.org/novapost/django-ticketoffice
* Roadmap: https://github.com/novapost/django-ticketoffice/issues/milestones


.. _`django-mail-factory`:
   https://pypi.python.org/pypi/django-mail-factory
.. _`vision`:
   https://django-ticketoffice.readthedocs.org/en/latest/about/vision.html
.. _`roadmap`:
   https://github.com/novapost/django-ticketoffice/issues/milestones
.. _`alternatives`:
   https://django-ticketoffice.readthedocs.org/en/latest/about/alternatives.html
