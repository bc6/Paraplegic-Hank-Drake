from __future__ import with_statement
import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import unittest2

class TestWith(unittest2.TestCase):

    def testAssertRaisesExcValue(self):

        class ExceptionMock(Exception):
            pass

        def Stub(foo):
            raise ExceptionMock(foo)


        v = 'particular value'
        ctx = self.assertRaises(ExceptionMock)
        with ctx:
            Stub(v)
        e = ctx.exception
        self.assertIsInstance(e, ExceptionMock)
        self.assertEqual(e.args[0], v)



    def test_assertRaises(self):

        def _raise(e):
            raise e


        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError('key'))
        try:
            self.assertRaises(KeyError, lambda : None)
        except self.failureException as e:
            self.assertIn('KeyError not raised', e.args)
        else:
            self.fail("assertRaises() didn't fail")
        try:
            self.assertRaises(KeyError, _raise, ValueError)
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")
        with self.assertRaises(KeyError) as cm:
            try:
                raise KeyError
            except Exception as e:
                raise 
        self.assertIs(cm.exception, e)
        with self.assertRaises(KeyError):
            raise KeyError('key')
        try:
            with self.assertRaises(KeyError):
                pass
        except self.failureException as e:
            self.assertIn('KeyError not raised', e.args)
        else:
            self.fail("assertRaises() didn't fail")
        try:
            with self.assertRaises(KeyError):
                raise ValueError
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")



if __name__ == '__main__':
    unittest2.main()

