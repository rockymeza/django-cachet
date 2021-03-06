from __future__ import absolute_import, unicode_literals

from django.core.cache import cache
from django.template import (
    Library, TemplateSyntaxError, VariableDoesNotExist, Template,
    TOKEN_VAR, TOKEN_BLOCK,
)
from django.templatetags.cache import CacheNode

from cachet.utils import make_template_fragment_key

register = Library()


class CachetNode(CacheNode):
    def __init__(self, nodelist, contents, timeout_var=None, vary_on=tuple()):
        self.nodelist = nodelist
        self.contents = contents
        self.expire_time_var = timeout_var
        self.vary_on = vary_on

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cachet" tag got an unknown variable: %r' % self.expire_time_var.var)
        except AttributeError:
            expire_time = None
        else:
            try:
                expire_time = int(expire_time)
            except (ValueError, TypeError):
                raise TemplateSyntaxError('"cachet" tag got a non-integer timeout value: %r' % expire_time)
        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.contents, vary_on)
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache.set(cache_key, value, expire_time)
        return value


def get_contents_until(parser, endtag):
    """
    Seeks ahead to grab all content almost verbatim without consuming anything.
    """
    index = 0
    while True:
        token = parser.tokens[index]
        index += 1
        if token.contents == endtag:
            break
        if token.token_type == TOKEN_VAR:
            yield '{{'
        elif token.token_type == TOKEN_BLOCK:
            yield '{%'
        yield token.contents
        if token.token_type == TOKEN_VAR:
            yield '}}'
        elif token.token_type == TOKEN_BLOCK:
            yield '%}'


@register.tag('cachet')
def do_cachet(parser, token):
    """
    This will cache the contents of a template fragment.

    Usage::

        {% load cachet %}
        {% cachet [expire_time] [on [var1] [var2] ..] %}
            .. some expensive processing ..
        {% endcachet %}


    Each unique set of arguments will result in a unique cache entry.
    """
    contents = ''.join(get_contents_until(parser, 'endcachet'))
    nodelist = parser.parse(('endcachet',))
    parser.delete_first_token()
    kwargs = {}

    tokens = token.split_contents()

    remaining_tokens = tokens[1:]
    while remaining_tokens:
        option = remaining_tokens.pop(0)
        if option == 'on':
            kwargs['vary_on'] = map(parser.compile_filter, remaining_tokens)
            break
        elif 'timeout_var' not in kwargs:
            kwargs['timeout_var'] = parser.compile_filter(option)
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (tokens[0], option))

    return CachetNode(nodelist=nodelist, contents=contents, **kwargs)
