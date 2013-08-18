from __future__ import absolute_import, unicode_literals

# Based on django.core.cache.utils for compatibility with < Django 1.6

import hashlib
import itertools

from django.utils.http import urlquote

try:
    from django.utils.encoding import force_bytes
except ImportError:  # Django < 1.5 (which means Python < 3)
    force_bytes = str

TEMPLATE_FRAGMENT_KEY_TEMPLATE = 'template.cash.%s'


def make_template_fragment_key(fragment, vary_on=None):
    if vary_on is None:
        vary_on = ()
    key_args = itertools.chain((fragment,), vary_on)
    key = ':'.join([urlquote(var) for var in key_args])
    args = hashlib.md5(force_bytes(key))
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % args.hexdigest()
