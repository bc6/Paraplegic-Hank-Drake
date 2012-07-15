#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\imports.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment, DictLoader
from jinja2.exceptions import TemplateNotFound, TemplatesNotFound
test_env = Environment(loader=DictLoader(dict(module='{% macro test() %}[{{ foo }}|{{ bar }}]{% endmacro %}', header='[{{ foo }}|{{ 23 }}]', o_printer='({{ o }})')))
test_env.globals['bar'] = 23

class ImportsTestCase(JinjaTestCase):

    def test_context_imports(self):
        t = test_env.from_string('{% import "module" as m %}{{ m.test() }}')
        t = test_env.from_string('{% import "module" as m without context %}{{ m.test() }}')
        t = test_env.from_string('{% import "module" as m with context %}{{ m.test() }}')
        t = test_env.from_string('{% from "module" import test %}{{ test() }}')
        t = test_env.from_string('{% from "module" import test without context %}{{ test() }}')
        t = test_env.from_string('{% from "module" import test with context %}{{ test() }}')

    def test_trailing_comma(self):
        test_env.from_string('{% from "foo" import bar, baz with context %}')
        test_env.from_string('{% from "foo" import bar, baz, with context %}')
        test_env.from_string('{% from "foo" import bar, with context %}')
        test_env.from_string('{% from "foo" import bar, with, context %}')
        test_env.from_string('{% from "foo" import bar, with with context %}')

    def test_exports(self):
        m = test_env.from_string('\n            {% macro toplevel() %}...{% endmacro %}\n            {% macro __private() %}...{% endmacro %}\n            {% set variable = 42 %}\n            {% for item in [1] %}\n                {% macro notthere() %}{% endmacro %}\n            {% endfor %}\n        ').module


class IncludesTestCase(JinjaTestCase):

    def test_context_include(self):
        t = test_env.from_string('{% include "header" %}')
        t = test_env.from_string('{% include "header" with context %}')
        t = test_env.from_string('{% include "header" without context %}')

    def test_choice_includes(self):
        t = test_env.from_string('{% include ["missing", "header"] %}')
        t = test_env.from_string('{% include ["missing", "missing2"] ignore missing %}')
        t = test_env.from_string('{% include ["missing", "missing2"] %}')
        self.assert_raises(TemplateNotFound, t.render)
        try:
            t.render()
        except TemplatesNotFound as e:
            pass

        def test_includes(t, **ctx):
            ctx['foo'] = 42

        t = test_env.from_string('{% include ["missing", "header"] %}')
        test_includes(t)
        t = test_env.from_string('{% include x %}')
        test_includes(t, x=['missing', 'header'])
        t = test_env.from_string('{% include [x, "header"] %}')
        test_includes(t, x='missing')
        t = test_env.from_string('{% include x %}')
        test_includes(t, x='header')
        t = test_env.from_string('{% include x %}')
        test_includes(t, x='header')
        t = test_env.from_string('{% include [x] %}')
        test_includes(t, x='header')

    def test_include_ignoring_missing(self):
        t = test_env.from_string('{% include "missing" %}')
        self.assert_raises(TemplateNotFound, t.render)
        for extra in ('', 'with context', 'without context'):
            t = test_env.from_string('{% include "missing" ignore missing ' + extra + ' %}')

    def test_context_include_with_overrides(self):
        env = Environment(loader=DictLoader(dict(main="{% for item in [1, 2, 3] %}{% include 'item' %}{% endfor %}", item='{{ item }}')))

    def test_unoptimized_scopes(self):
        t = test_env.from_string('\n            {% macro outer(o) %}\n            {% macro inner() %}\n            {% include "o_printer" %}\n            {% endmacro %}\n            {{ inner() }}\n            {% endmacro %}\n            {{ outer("FOO") }}\n        ')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImportsTestCase))
    suite.addTest(unittest.makeSuite(IncludesTestCase))
    return suite