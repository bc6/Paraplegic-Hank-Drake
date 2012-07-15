#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\debug.py
import sys
import unittest
from jinja2.testsuite import JinjaTestCase, filesystem_loader
from jinja2 import Environment, TemplateSyntaxError
env = Environment(loader=filesystem_loader)

class DebugTestCase(JinjaTestCase):
    if sys.version_info[:2] != (2, 4):

        def test_runtime_error(self):

            def test():
                tmpl.render(fail=lambda : 1 / 0)

            tmpl = env.get_template('broken.html')
            self.assert_traceback_matches(test, '\n  File ".*?broken.html", line 2, in (top-level template code|<module>)\n    \\{\\{ fail\\(\\) \\}\\}\n  File ".*?debug.pyc?", line \\d+, in <lambda>\n    tmpl\\.render\\(fail=lambda: 1 / 0\\)\nZeroDivisionError: (int(eger)? )?division (or modulo )?by zero\n')

    def test_syntax_error(self):
        self.assert_traceback_matches(lambda : env.get_template('syntaxerror.html'), '(?sm)\n  File ".*?syntaxerror.html", line 4, in (template|<module>)\n    \\{% endif %\\}.*?\n(jinja2\\.exceptions\\.)?TemplateSyntaxError: Encountered unknown tag \'endif\'. Jinja was looking for the following tags: \'endfor\' or \'else\'. The innermost block that needs to be closed is \'for\'.\n    ')

    def test_regular_syntax_error(self):

        def test():
            raise TemplateSyntaxError('wtf', 42)

        self.assert_traceback_matches(test, '\n  File ".*debug.pyc?", line \\d+, in test\n    raise TemplateSyntaxError\\(\'wtf\', 42\\)\n(jinja2\\.exceptions\\.)?TemplateSyntaxError: wtf\n  line 42')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DebugTestCase))
    return suite