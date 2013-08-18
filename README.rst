django-cachet
=============

.. image:: https://api.travis-ci.org/rockymeza/django-cachet.png
   :alt: Building Status
   :target: https://travis-ci.org/rockymeza/django-cachet

A collection of caching helpers for Django.

Template Tags
-------------

Django-cachet provides a template tag that is similar to Django's built-in cache
template tag, but that derives the cache key from the actual content of the
template. With this template tag, a timeout is optional. With specific enough
keys, you don't need to expire your cache.

.. code-block:: html+django

    {% load cachet %}
    {% cachet %}
      There are {{ expensive_query.count }} objects in the list.
    {% endcachet %}

Just like the built-in cache template tag, you can pass in an optional timeout
or variance keys as well, but the syntax is different.

.. code-block:: html+django

    {% cachet [timeout] [on *key_args] %}

The benefit of this approach over Django's is that when you modify the cached
template fragment, the cache key will change, meaning that you can develop more
easily without having to manually invalidate your cache. Essentially, the
template fragment is content addressed. This also means that you don't need to
expire your cache either.
