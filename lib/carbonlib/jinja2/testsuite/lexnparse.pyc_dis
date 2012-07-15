#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\lexnparse.py
import sys
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment, Template, TemplateSyntaxError, UndefinedError, nodes
env = Environment()
if sys.version_info < (3, 0):

    def jinja_string_repr(string):
        return repr(string)[1:]


else:
    jinja_string_repr = repr

class LexerTestCase(JinjaTestCase):

    def test_raw1(self):
        tmpl = env.from_string('{% raw %}foo{% endraw %}|{%raw%}{{ bar }}|{% baz %}{%       endraw    %}')

    def test_raw2(self):
        tmpl = env.from_string('1  {%- raw -%}   2   {%- endraw -%}   3')

    def test_balancing(self):
        env = Environment('{%', '%}', '${', '}')
        tmpl = env.from_string("{% for item in seq\n            %}${{'foo': item}|upper}{% endfor %}")

    def test_comments(self):
        env = Environment('<!--', '-->', '{', '}')
        tmpl = env.from_string('<ul>\n<!--- for item in seq -->\n  <li>{item}</li>\n<!--- endfor -->\n</ul>')

    def test_string_escapes(self):
        for char in (u'\x00', u'\u2668', u'\xe4', u'\t', u'\r', u'\n'):
            tmpl = env.from_string('{{ %s }}' % jinja_string_repr(char))

    def test_bytefallback(self):
        from pprint import pformat
        tmpl = env.from_string(u"{{ 'foo'|pprint }}|{{ 'b\xe4r'|pprint }}")

    def test_operators(self):
        from jinja2.lexer import operators
        for test, expect in operators.iteritems():
            if test in '([{}])':
                continue
            stream = env.lexer.tokenize('{{ %s }}' % test)
            stream.next()

    def test_normalizing(self):
        for seq in ('\r', '\r\n', '\n'):
            env = Environment(newline_sequence=seq)
            tmpl = env.from_string('1\n2\r\n3\n4\n')
            result = tmpl.render()


class ParserTestCase(JinjaTestCase):

    def test_php_syntax(self):
        env = Environment('<?', '?>', '<?=', '?>', '<!--', '-->')
        tmpl = env.from_string("<!-- I'm a comment, I'm not interesting --><? for item in seq -?>\n    <?= item ?>\n<?- endfor ?>")

    def test_erb_syntax(self):
        env = Environment('<%', '%>', '<%=', '%>', '<%#', '%>')
        tmpl = env.from_string("<%# I'm a comment, I'm not interesting %><% for item in seq -%>\n    <%= item %>\n<%- endfor %>")

    def test_comment_syntax(self):
        env = Environment('<!--', '-->', '${', '}', '<!--#', '-->')
        tmpl = env.from_string("<!--# I'm a comment, I'm not interesting --><!-- for item in seq --->\n    ${item}\n<!--- endfor -->")

    def test_balancing(self):
        tmpl = env.from_string("{{{'foo':'bar'}.foo}}")

    def test_start_comment(self):
        tmpl = env.from_string('{# foo comment\nand bar comment #}\n{% macro blub() %}foo{% endmacro %}\n{{ blub() }}')

    def test_line_syntax(self):
        env = Environment('<%', '%>', '${', '}', '<%#', '%>', '%')
        tmpl = env.from_string('<%# regular comment %>\n% for item in seq:\n    ${item}\n% endfor')
        env = Environment('<%', '%>', '${', '}', '<%#', '%>', '%', '##')
        tmpl = env.from_string('<%# regular comment %>\n% for item in seq:\n    ${item} ## the rest of the stuff\n% endfor')

    def test_line_syntax_priority(self):
        env = Environment('{%', '%}', '${', '}', '/*', '*/', '##', '#')
        tmpl = env.from_string("/* ignore me.\n   I'm a multiline comment */\n## for item in seq:\n* ${item}          # this is just extra stuff\n## endfor")
        env = Environment('{%', '%}', '${', '}', '/*', '*/', '#', '##')
        tmpl = env.from_string("/* ignore me.\n   I'm a multiline comment */\n# for item in seq:\n* ${item}          ## this is just extra stuff\n    ## extra stuff i just want to ignore\n# endfor")

    def test_error_messages(self):

        def assert_error(code, expected):
            try:
                Template(code)
            except TemplateSyntaxError as e:
                pass

        assert_error('{% for item in seq %}...{% endif %}', "Encountered unknown tag 'endif'. Jinja was looking for the following tags: 'endfor' or 'else'. The innermost block that needs to be closed is 'for'.")
        assert_error('{% if foo %}{% for item in seq %}...{% endfor %}{% endfor %}', "Encountered unknown tag 'endfor'. Jinja was looking for the following tags: 'elif' or 'else' or 'endif'. The innermost block that needs to be closed is 'if'.")
        assert_error('{% if foo %}', "Unexpected end of template. Jinja was looking for the following tags: 'elif' or 'else' or 'endif'. The innermost block that needs to be closed is 'if'.")
        assert_error('{% for item in seq %}', "Unexpected end of template. Jinja was looking for the following tags: 'endfor' or 'else'. The innermost block that needs to be closed is 'for'.")
        assert_error('{% block foo-bar-baz %}', 'Block names in Jinja have to be valid Python identifiers and may not contain hyphens, use an underscore instead.')
        assert_error('{% unknown_tag %}', "Encountered unknown tag 'unknown_tag'.")


class SyntaxTestCase(JinjaTestCase):

    def test_call(self):
        env = Environment()
        env.globals['foo'] = lambda a, b, c, e, g: a + b + c + e + g
        tmpl = env.from_string("{{ foo('a', c='d', e='f', *['b'], **{'g': 'h'}) }}")

    def test_slicing(self):
        tmpl = env.from_string('{{ [1, 2, 3][:] }}|{{ [1, 2, 3][::-1] }}')

    def test_attr(self):
        tmpl = env.from_string("{{ foo.bar }}|{{ foo['bar'] }}")

    def test_subscript(self):
        tmpl = env.from_string('{{ foo[0] }}|{{ foo[-1] }}')

    def test_tuple(self):
        tmpl = env.from_string('{{ () }}|{{ (1,) }}|{{ (1, 2) }}')

    def test_math(self):
        tmpl = env.from_string('{{ (1 + 1 * 2) - 3 / 2 }}|{{ 2**3 }}')

    def test_div(self):
        tmpl = env.from_string('{{ 3 // 2 }}|{{ 3 / 2 }}|{{ 3 % 2 }}')

    def test_unary(self):
        tmpl = env.from_string('{{ +3 }}|{{ -3 }}')

    def test_concat(self):
        tmpl = env.from_string("{{ [1, 2] ~ 'foo' }}")

    def test_compare(self):
        tmpl = env.from_string('{{ 1 > 0 }}|{{ 1 >= 1 }}|{{ 2 < 3 }}|{{ 2 == 2 }}|{{ 1 <= 1 }}')

    def test_inop(self):
        tmpl = env.from_string('{{ 1 in [1, 2, 3] }}|{{ 1 not in [1, 2, 3] }}')

    def test_literals(self):
        tmpl = env.from_string('{{ [] }}|{{ {} }}|{{ () }}')

    def test_bool(self):
        tmpl = env.from_string('{{ true and false }}|{{ false or true }}|{{ not false }}')

    def test_grouping(self):
        tmpl = env.from_string('{{ (true and false) or (false and true) and not false }}')

    def test_django_attr(self):
        tmpl = env.from_string('{{ [1, 2, 3].0 }}|{{ [[1]].0.0 }}')

    def test_conditional_expression(self):
        tmpl = env.from_string('{{ 0 if true else 1 }}')

    def test_short_conditional_expression(self):
        tmpl = env.from_string('<{{ 1 if false }}>')
        tmpl = env.from_string('<{{ (1 if false).bar }}>')
        self.assert_raises(UndefinedError, tmpl.render)

    def test_filter_priority(self):
        tmpl = env.from_string('{{ "foo"|upper + "bar"|upper }}')

    def test_function_calls(self):
        tests = [(True, '*foo, bar'),
         (True, '*foo, *bar'),
         (True, '*foo, bar=42'),
         (True, '**foo, *bar'),
         (True, '**foo, bar'),
         (False, 'foo, bar'),
         (False, 'foo, bar=42'),
         (False, 'foo, bar=23, *args'),
         (False, 'a, b=c, *d, **e'),
         (False, '*foo, **bar')]
        for should_fail, sig in tests:
            if should_fail:
                self.assert_raises(TemplateSyntaxError, env.from_string, '{{ foo(%s) }}' % sig)
            else:
                env.from_string('foo(%s)' % sig)

    def test_tuple_expr(self):
        for tmpl in ['{{ () }}',
         '{{ (1, 2) }}',
         '{{ (1, 2,) }}',
         '{{ 1, }}',
         '{{ 1, 2 }}',
         '{% for foo, bar in seq %}...{% endfor %}',
         '{% for x in foo, bar %}...{% endfor %}',
         '{% for x in foo, %}...{% endfor %}']:
            pass

    def test_trailing_comma(self):
        tmpl = env.from_string('{{ (1, 2,) }}|{{ [1, 2,] }}|{{ {1: 2,} }}')

    def test_block_end_name(self):
        env.from_string('{% block foo %}...{% endblock foo %}')
        self.assert_raises(TemplateSyntaxError, env.from_string, '{% block x %}{% endblock y %}')

    def test_constant_casing(self):
        for const in (True, False, None):
            tmpl = env.from_string('{{ %s }}|{{ %s }}|{{ %s }}' % (str(const), str(const).lower(), str(const).upper()))

    def test_test_chaining(self):
        self.assert_raises(TemplateSyntaxError, env.from_string, '{{ foo is string is sequence }}')

    def test_string_concatenation(self):
        tmpl = env.from_string('{{ "foo" "bar" "baz" }}')

    def test_notin(self):
        bar = xrange(100)
        tmpl = env.from_string('{{ not 42 in bar }}')

    def test_implicit_subscribed_tuple(self):

        class Foo(object):

            def __getitem__(self, x):
                return x

        t = env.from_string('{{ foo[1, 2] }}')

    def test_raw2(self):
        tmpl = env.from_string('{% raw %}{{ FOO }} and {% BAR %}{% endraw %}')

    def test_const(self):
        tmpl = env.from_string('{{ true }}|{{ false }}|{{ none }}|{{ none is defined }}|{{ missing is defined }}')

    def test_neg_filter_priority(self):
        node = env.parse('{{ -1|foo }}')

    def test_const_assign(self):
        constass1 = '{% set true = 42 %}'
        constass2 = '{% for none in seq %}{% endfor %}'
        for tmpl in (constass1, constass2):
            self.assert_raises(TemplateSyntaxError, env.from_string, tmpl)

    def test_localset(self):
        tmpl = env.from_string('{% set foo = 0 %}{% for item in [1, 2] %}{% set foo = 1 %}{% endfor %}{{ foo }}')

    def test_parse_unary(self):
        tmpl = env.from_string('{{ -foo["bar"] }}')
        tmpl = env.from_string('{{ -foo["bar"]|abs }}')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LexerTestCase))
    suite.addTest(unittest.makeSuite(ParserTestCase))
    suite.addTest(unittest.makeSuite(SyntaxTestCase))
    return suite