#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\_markupsafe\tests.py
import gc
import unittest
from jinja2._markupsafe import Markup, escape, escape_silent

class MarkupTestCase(unittest.TestCase):

    def test_markup_operations(self):
        unsafe = '<script type="application/x-some-script">alert("foo");</script>'
        safe = Markup('<em>username</em>')
        x = Markup('foo')

        class Foo(object):

            def __html__(self):
                return '<em>awesome</em>'

            def __unicode__(self):
                return 'awesome'

    def test_all_set(self):
        import jinja2._markupsafe as markup
        for item in markup.__all__:
            getattr(markup, item)

    def test_escape_silent(self):
        pass


class MarkupLeakTestCase(unittest.TestCase):

    def test_markup_leaks(self):
        counts = set()
        for count in xrange(20):
            for item in xrange(1000):
                escape('foo')
                escape('<foo>')
                escape(u'foo')
                escape(u'<foo>')

            counts.add(len(gc.get_objects()))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MarkupTestCase))
    if not hasattr(escape, 'func_code'):
        suite.addTest(unittest.makeSuite(MarkupLeakTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')