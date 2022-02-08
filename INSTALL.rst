#######
Install
#######

`django-ticketoffice` is open-source software, published under BSD license.
See :doc:`/about/license` for details.

If you want to install a development environment, you should go to
:doc:`/contributing` documentation.


*************
Prerequisites
*************

* `Python`_ >=3.8.


************
As a library
************

In most cases, you will use `django-ticketoffice` as a dependency of your
`Django` project. In such a case, you should add ``django-ticketoffice`` in
your main project's requirements. Typically in :file:`setup.py`:

.. code:: python

   from setuptools import setup

   setup(
       install_requires=[
           'django-ticketoffice',
           #...
       ]
       # ...
   )

Then when you install your main project with your favorite package manager
(like `pip`_), `django-ticketoffice` will automatically be installed.


**********
Standalone
**********

You can install `django-ticketoffice` with your favorite Python package manager.
As an example with `pip`_:

.. code:: sh

   pip install django-ticketoffice


*****
Check
*****

Check `django-ticketoffice` has been installed:

.. code:: sh

   python -c "import django_ticketoffice;print(django_ticketoffice.__version__)"

You should get `django_ticketoffice`'s version.


.. rubric:: References

.. target-notes::

.. _`Python`: http://python.org
.. _`pip`: https://pypi.python.org/pypi/pip/
