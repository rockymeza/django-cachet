django-cash
===========

.. image:: https://api.travis-ci.org/rockymeza/django-cash.png
   :alt: Building Status
   :target: https://travis-ci.org/rockymeza/django-cash

A collection of caching helpers for Django.

Template Tags
-------------

Django-cash provides a template tag that is similar to Django's built-in cache
template tag, but that derives the cache key from the actual content of the
template.  With this template tag, a timeout is optional.  With specific enough
keys, you don't need to expire your cache.

.. code-block:: html+django

    {% load cash %}
    {% cash %}
      There are {{ expensive_query.count }} objects in the list.
    {% endcash %}

Just like the built-in cache template tag, you can pass in an optional timeout
or variance keys as well, but the syntax is different.

.. code-block:: html+django

    {% cash [timeout] [on *key_args] %}
