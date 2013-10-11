# -*- coding: utf-8 -*-
"""Utilities that may be packaged in external libraries."""
import os

from django.views.generic import TemplateView


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


from collections import OrderedDict

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash


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
