# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import mock

from django.test import TestCase
from django.template import Template, Context
from django.core.cache import cache


class TemplateTagTest(TestCase):
    def setUp(self):
        self.func = mock.Mock(return_value="test content",
                              do_not_call_in_templates=False,
                              alters_data=False,
                              silent_variable_failure=False)

    def tearDown(self):
        cache.clear()

    def render_template(self, template, **context):
        context.setdefault('func', self.func)
        return Template(template).render(Context(context))

    def test_cachet_tag(self):
        template = "{% load cachet %}{% cachet %}{{ func }}{% endcachet %}"
        self.assertEqual(self.func.call_count, 0)
        rendered = self.render_template(template)

        self.assertEqual(rendered, 'test content')
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template)
        self.assertEqual(self.func.call_count, 1)

    def test_cachet_vary_on(self):
        template = "{% load cachet %}{% cachet on foo %}{{ func }}{% endcachet %}"
        self.assertEqual(self.func.call_count, 0)

        self.render_template(template, foo='bar')
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template, foo='bar')
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template, foo='baz')
        self.assertEqual(self.func.call_count, 2)

        self.render_template(template, foo='baz')
        self.assertEqual(self.func.call_count, 2)

    def test_cachet_on_multiple(self):
        template = "{% load cachet %}{% cachet on foo bar %}{{ func }}{% endcachet %}"
        self.assertEqual(self.func.call_count, 0)

        self.render_template(template, foo='bar', bar="a")
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template, foo='bar', bar="a")
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template, foo='baz', bar="a")
        self.assertEqual(self.func.call_count, 2)

        self.render_template(template, foo='baz', bar="b")
        self.assertEqual(self.func.call_count, 3)

        self.render_template(template, foo='baz', bar="b")
        self.assertEqual(self.func.call_count, 3)

    def test_cachet_expiry(self):
        template = "{% load cachet %}{% cachet 1 %}{{ func }}{% endcachet %}"
        self.assertEqual(self.func.call_count, 0)

        self.render_template(template)
        self.assertEqual(self.func.call_count, 1)

        self.render_template(template)
        self.assertEqual(self.func.call_count, 1)

        time.sleep(2)
        self.render_template(template)
        self.assertEqual(self.func.call_count, 2)