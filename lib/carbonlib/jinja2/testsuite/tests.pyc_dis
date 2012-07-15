#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\tests.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Markup, Environment
env = Environment()

class TestsTestCase(JinjaTestCase):

    def test_defined(self):
        tmpl = env.from_string('{{ missing is defined }}|{{ true is defined }}')

    def test_even(self):
        tmpl = env.from_string('{{ 1 is even }}|{{ 2 is even }}')

    def test_odd(self):
        tmpl = env.from_string('{{ 1 is odd }}|{{ 2 is odd }}')

    def test_lower(self):
        tmpl = env.from_string('{{ "foo" is lower }}|{{ "FOO" is lower }}')

    def test_typechecks(self):
        tmpl = env.from_string('\n            {{ 42 is undefined }}\n            {{ 42 is defined }}\n            {{ 42 is none }}\n            {{ none is none }}\n            {{ 42 is number }}\n            {{ 42 is string }}\n            {{ "foo" is string }}\n            {{ "foo" is sequence }}\n            {{ [1] is sequence }}\n            {{ range is callable }}\n            {{ 42 is callable }}\n            {{ range(5) is iterable }}\n            {{ {} is mapping }}\n            {{ mydict is mapping }}\n            {{ [] is mapping }}\n        ')

        class MyDict(dict):
            pass

    def test_sequence(self):
        tmpl = env.from_string('{{ [1, 2, 3] is sequence }}|{{ "foo" is sequence }}|{{ 42 is sequence }}')

    def test_upper(self):
        tmpl = env.from_string('{{ "FOO" is upper }}|{{ "foo" is upper }}')

    def test_sameas(self):
        tmpl = env.from_string('{{ foo is sameas false }}|{{ 0 is sameas false }}')

    def test_no_paren_for_arg1(self):
        tmpl = env.from_string('{{ foo is sameas none }}')

    def test_escaped(self):
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ x is escaped }}|{{ y is escaped }}')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestsTestCase))
    return suite