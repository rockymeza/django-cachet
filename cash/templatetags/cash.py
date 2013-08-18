from __future__ import absolute_import, unicode_literals

from django.core.cache import cache
from django.template import (
    Library, TemplateSyntaxError, VariableDoesNotExist, Template,
    TOKEN_VAR, TOKEN_BLOCK,
)
from django.templatetags.cache import CacheNode

from cash.utils import make_template_fragment_key

register = Library()


class CashNode(CacheNode):
    def __init__(self, template, timeout_var=None, vary_on=tuple()):
        self.template = Template(template)
        self.contents = template
        self.expire_time_var = timeout_var
        self.vary_on = vary_on

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cash" tag got an unknown variable: %r' % self.expire_time_var.var)
        except AttributeError:
            expire_time = None
        else:
            try:
                expire_time = int(expire_time)
            except (ValueError, TypeError):
                raise TemplateSyntaxError('"cash" tag got a non-integer timeout value: %r' % expire_time)
        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.contents, vary_on)
        value = cache.get(cache_key)
        if value is None:
            value = self.template.render(context)
            cache.set(cache_key, value, expire_time)
        return value


def get_contents_until(parser, endtag):
    while True:
        token = parser.tokens.pop(0)
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


@register.tag('cash')
def do_cash(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load cash %}
        {% cash [expire_time] [fragment_name] %}
            .. some expensive processing ..
        {% endcash %}

    This tag also supports varying by a list of arguments::

        {% load cash %}
        {% cash [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcash %}

    Each unique set of arguments will result in a unique cache entry.
    """
    template = ''.join(get_contents_until(parser, 'endcash'))
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

    return CashNode(template=template, **kwargs)
