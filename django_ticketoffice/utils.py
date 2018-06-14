# -*- coding: utf-8 -*-
"""Utilities that may be packaged in external libraries."""
import os

from collections import OrderedDict

from django.views.generic import TemplateView
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash


def random_unicode(min_length=None,
                   max_length=None,
                   alphabet=u'abcdefghijklmnopqrstuvwxyz'
                            u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                            u'0123456789'):
    """Return random unicode.

    .. note:: Uses :py:func:`os.urandom`.

    """
    if min_length is None:
        if max_length is None:
            raise ValueError("Provide min_length or max_length.")
        else:
            min_length = 1
    if max_length is None:
        max_length = min_length
    if min_length < 1:
        raise ValueError("Minimum length is 1.")
    if max_length < min_length:
        raise ValueError("Maximum length must be greater than minimum length.")
    random_bytes = os.urandom((max_length + 1) * 2)
    # Compute random length using 2 first bytes.
    interval = max_length - min_length + 1
    random_shift = ord(random_bytes[0])
    random_number = ord(random_bytes[1])
    length = min_length + (random_shift + random_number) % interval
    # Compute random string.
    interval = len(alphabet)
    result = []
    for index in range(1, length + 1):
        index *= 2
        random_shift = ord(random_bytes[index])
        random_number = ord(random_bytes[index + 1])
        random_char = alphabet[(random_shift + random_number) % interval]
        result.append(random_char)
    return u''.join(result)


def random_password(min_length=16, max_length=32,
                    alphabet='abcdefghjkmnpqrstuvwxyz'
                             'ABCDEFGHJKLMNPQRSTUVWXYZ'
                             '23456789'):
    """Return random password of random length with limited ASCII alphabet.

    .. note::

       The default value of allowed chars does not have "I" or "O" or
       letters and digits that look similar -- just to avoid confusion.

    """
    return random_unicode(min_length, max_length, alphabet)


class PlainPasswordHasher(BasePasswordHasher):
    "Plain password hashing algorithm for test (DO NOT USE in production)."
    algorithm = "plain"

    def salt(self):
        return ''

    def encode(self, password, salt):
        return '%s$$%s' % (self.algorithm, password)

    def verify(self, password, encoded):
        algorithm, hash = encoded.split('$$', 1)
        assert algorithm == self.algorithm
        return password == hash

    def safe_summary(self, encoded):
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('hash', mask_hash(encoded, show=3)),
        ])


class UnauthorizedView(TemplateView):
    template_name = '401.html'

    def render_to_response(self, context, **response_kwargs):
        """Render response with status code 401."""
        response_kwargs.setdefault('status', 401)
        return TemplateView.render_to_response(self, context,
                                               **response_kwargs)


class ForbiddenView(TemplateView):
    template_name = '403.html'

    def render_to_response(self, context, **response_kwargs):
        """Render response with status code 401."""
        response_kwargs.setdefault('status', 403)
        return TemplateView.render_to_response(self, context,
                                               **response_kwargs)


def import_member(import_string):
    """Import one member of Python module by path.

    >>> import os.path
    >>> imported = import_member('os.path.supports_unicode_filenames')
    >>> os.path.supports_unicode_filenames is imported
    True

    """
    module_name, factory_name = import_string.rsplit('.', 1)
    module = __import__(module_name, globals(), locals(), [factory_name], -1)
    return getattr(module, factory_name)


#: Sentinel to detect undefined function argument.
UNDEFINED_FUNCTION = object()


class NotCallableError(TypeError):
    """Raised when operation requires a callable."""


class Decorator(object):
    """Base class to create class-based decorators.

    See: https://tech.people-doc.com/python-class-based-decorators.html

    Override :meth:`setup`, :meth:`run` or :meth:`decorate` to create custom
    decorators:

    * :meth:`setup` is dedicated to setup, i.e. setting decorator's internal
      options.
      :meth:`__init__` calls :py:meth:`setup`.

    * :meth:`decorate` is dedicated to wrapping function, i.e. remember the
      function to decorate.
      :meth:`__init__` or :meth:`__call__` may call :meth:`decorate`,
      depending on the usage.

    * :meth:`run` is dedicated to execution, i.e. running the decorated
      function.
      :meth:`__call__` calls :meth:`run` if a function has already been
      decorated.

    Decorator instances are callables. The :meth:`__call__` method has a
    special implementation in Decorator. Generally, consider overriding
    :meth:`run` instead of :meth:`__call__`.

    """
    #: Sentinel to detect undefined function argument.
    UNDEFINED_FUNCTION = UNDEFINED_FUNCTION

    #: Shortcut to exception:
    NotCallableError = NotCallableError

    def __init__(self, func=UNDEFINED_FUNCTION):
        """Constructor.

        Accepts one optional positional argument: the function to decorate.

        Other arguments **must** be keyword arguments.

        And beware passing ``func`` as keyword argument: it would be used as
        the function to decorate.

        Handle decorator's options; return decorator instance (``self``).

        Default implementation decorates ``func``.

        Override this method and adapt its signature depending on your needs.

        If the decorator has mandatory options, they should be positional
        arguments in :meth:`setup` (or an exception should be raised inside
        :meth:`setup`).

        If the decorator accepts optional configuration, there should be
        keyword arguments in :meth:`setup`.

        """
        #: Decorated function.
        self.decorated = self.UNDEFINED_FUNCTION
        # Decorate function, if it has been passed to :meth:`__init__`, i.e.
        # if decorator has been used with ``@`` and without parentheses:
        #
        # .. code:: python
        #
        #    @Decorator
        #    def some_function():
        #        pass
        #
        # Which is an equivalent to:
        #
        # .. code:: python
        #
        #    def some_function():
        #        pass
        #    some_function = Decorator(some_function)
        if func is not self.UNDEFINED_FUNCTION:
            self.decorate(func)
        return self

    def decorate(self, func):
        """Set :attr:`decorated`; return decorator instance (``self``).

        Raises :class:`NotCallableError` (inherits from :class:`TypeError` if
        ``func`` is not a callable.

        """
        if not callable(func):
            raise NotCallableError(
                'Cannot decorate non callable object "{func}"'
                .format(func=func))
        self.decorated = func
        return self

    def __call__(self, *args, **kwargs):
        """Run decorated function if available, else decorate first arg.

        First use case of :meth:`__call__` is: decorator instance has already
        been initialized with function to decorate, and the decorated function
        is called:

        .. code:: python

           @Decorator  # No parentheses => __init__() will be called with
                       # some_function as first (and only) argument.
           def some_function():
               pass

           some_function()  # Decorator.__call__()

        Second use case is: decorator instance has been initialized with
        configuration, but without function to decorate. Then the decorator
        instance is used to decorate a function:

        .. code:: python

           @Decorator()  # Parentheses => ``some_function`` will be decorated
                         # via ``Decorator.__call__(some_function)``.
           def some_function():
               pass

        """
        if self.decorated is self.UNDEFINED_FUNCTION:
            func = args[0]
            if args[1:] or kwargs:
                raise ValueError('Cannot decorate and setup simultaneously '
                                 'with __call__(). Use __init__() or '
                                 'setup() for setup. Use __call__() or '
                                 'decorate() to decorate.')
            self.decorate(func)
            return self
        else:
            return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        """Actually run the decorator.

        This base implementation is a transparent proxy to the decorated
        function: it passes positional and keyword arguments as is, and returns
        result.

        """
        return self.decorated(*args, **kwargs)
