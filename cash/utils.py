from __future__ import absolute_import, unicode_literals

# Based on django.core.cache.utils for compatibility with < Django 1.6

import hashlib
from django.utils.encoding import force_bytes
from django.utils.http import urlquote

TEMPLATE_FRAGMENT_KEY_TEMPLATE = 'template.cash.%s'


def make_template_fragment_key(fragment, vary_on=None):
    if vary_on is None:
        vary_on = ()
    key = ':'.join([fragment] + [urlquote(var) for var in vary_on])
    args = hashlib.md5(force_bytes(key))
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % args.hexdigest()
