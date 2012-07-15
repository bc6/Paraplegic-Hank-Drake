#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\core_tags.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment, TemplateSyntaxError, UndefinedError, DictLoader
env = Environment()

class ForLoopTestCase(JinjaTestCase):

    def test_simple(self):
        tmpl = env.from_string('{% for item in seq %}{{ item }}{% endfor %}')

    def test_else(self):
        tmpl = env.from_string('{% for item in seq %}XXX{% else %}...{% endfor %}')

    def test_empty_blocks(self):
        tmpl = env.from_string('<{% for item in seq %}{% else %}{% endfor %}>')

    def test_context_vars(self):
        tmpl = env.from_string('{% for item in seq -%}\n        {{ loop.index }}|{{ loop.index0 }}|{{ loop.revindex }}|{{\n            loop.revindex0 }}|{{ loop.first }}|{{ loop.last }}|{{\n           loop.length }}###{% endfor %}')
        one, two, _ = tmpl.render(seq=[0, 1]).split('###')
        one_index, one_index0, one_revindex, one_revindex0, one_first, one_last, one_length = one.split('|')
        two_index, two_index0, two_revindex, two_revindex0, two_first, two_last, two_length = two.split('|')

    def test_cycling(self):
        tmpl = env.from_string("{% for item in seq %}{{\n            loop.cycle('<1>', '<2>') }}{% endfor %}{%\n            for item in seq %}{{ loop.cycle(*through) }}{% endfor %}")
        output = tmpl.render(seq=range(4), through=('<1>', '<2>'))

    def test_scope(self):
        tmpl = env.from_string('{% for item in seq %}{% endfor %}{{ item }}')
        output = tmpl.render(seq=range(10))

    def test_varlen(self):

        def inner():
            for item in range(5):
                yield item

        tmpl = env.from_string('{% for item in iter %}{{ item }}{% endfor %}')
        output = tmpl.render(iter=inner())

    def test_noniter(self):
        tmpl = env.from_string('{% for item in none %}...{% endfor %}')
        self.assert_raises(TypeError, tmpl.render)

    def test_recursive(self):
        tmpl = env.from_string('{% for item in seq recursive -%}\n            [{{ item.a }}{% if item.b %}<{{ loop(item.b) }}>{% endif %}]\n        {%- endfor %}')

    def test_looploop(self):
        tmpl = env.from_string('{% for row in table %}\n            {%- set rowloop = loop -%}\n            {% for cell in row -%}\n                [{{ rowloop.index }}|{{ loop.index }}]\n            {%- endfor %}\n        {%- endfor %}')

    def test_reversed_bug(self):
        tmpl = env.from_string('{% for i in items %}{{ i }}{% if not loop.last %},{% endif %}{% endfor %}')

    def test_loop_errors(self):
        tmpl = env.from_string('{% for item in [1] if loop.index\n                                      == 0 %}...{% endfor %}')
        self.assert_raises(UndefinedError, tmpl.render)
        tmpl = env.from_string('{% for item in [] %}...{% else\n            %}{{ loop }}{% endfor %}')

    def test_loop_filter(self):
        tmpl = env.from_string('{% for item in range(10) if item is even %}[{{ item }}]{% endfor %}')
        tmpl = env.from_string('\n            {%- for item in range(10) if item is even %}[{{\n                loop.index }}:{{ item }}]{% endfor %}')

    def test_loop_unassignable(self):
        self.assert_raises(TemplateSyntaxError, env.from_string, '{% for loop in seq %}...{% endfor %}')

    def test_scoped_special_var(self):
        t = env.from_string('{% for s in seq %}[{{ loop.first }}{% for c in s %}|{{ loop.first }}{% endfor %}]{% endfor %}')

    def test_scoped_loop_var(self):
        t = env.from_string('{% for x in seq %}{{ loop.first }}{% for y in seq %}{% endfor %}{% endfor %}')
        t = env.from_string('{% for x in seq %}{% for y in seq %}{{ loop.first }}{% endfor %}{% endfor %}')

    def test_recursive_empty_loop_iter(self):
        t = env.from_string('\n        {%- for item in foo recursive -%}{%- endfor -%}\n        ')

    def test_call_in_loop(self):
        t = env.from_string('\n        {%- macro do_something() -%}\n            [{{ caller() }}]\n        {%- endmacro %}\n\n        {%- for i in [1, 2, 3] %}\n            {%- call do_something() -%}\n                {{ i }}\n            {%- endcall %}\n        {%- endfor -%}\n        ')

    def test_scoping_bug(self):
        t = env.from_string('\n        {%- for item in foo %}...{{ item }}...{% endfor %}\n        {%- macro item(a) %}...{{ a }}...{% endmacro %}\n        {{- item(2) -}}\n        ')

    def test_unpacking(self):
        tmpl = env.from_string('{% for a, b, c in [[1, 2, 3]] %}{{ a }}|{{ b }}|{{ c }}{% endfor %}')


class IfConditionTestCase(JinjaTestCase):

    def test_simple(self):
        tmpl = env.from_string('{% if true %}...{% endif %}')

    def test_elif(self):
        tmpl = env.from_string('{% if false %}XXX{% elif true\n            %}...{% else %}XXX{% endif %}')

    def test_else(self):
        tmpl = env.from_string('{% if false %}XXX{% else %}...{% endif %}')

    def test_empty(self):
        tmpl = env.from_string('[{% if true %}{% else %}{% endif %}]')

    def test_complete(self):
        tmpl = env.from_string('{% if a %}A{% elif b %}B{% elif c == d %}C{% else %}D{% endif %}')

    def test_no_scope(self):
        tmpl = env.from_string('{% if a %}{% set foo = 1 %}{% endif %}{{ foo }}')
        tmpl = env.from_string('{% if true %}{% set foo = 1 %}{% endif %}{{ foo }}')


class MacrosTestCase(JinjaTestCase):
    env = Environment(trim_blocks=True)

    def test_simple(self):
        tmpl = self.env.from_string("{% macro say_hello(name) %}Hello {{ name }}!{% endmacro %}\n{{ say_hello('Peter') }}")

    def test_scoping(self):
        tmpl = self.env.from_string("{% macro level1(data1) %}\n{% macro level2(data2) %}{{ data1 }}|{{ data2 }}{% endmacro %}\n{{ level2('bar') }}{% endmacro %}\n{{ level1('foo') }}")

    def test_arguments(self):
        tmpl = self.env.from_string("{% macro m(a, b, c='c', d='d') %}{{ a }}|{{ b }}|{{ c }}|{{ d }}{% endmacro %}\n{{ m() }}|{{ m('a') }}|{{ m('a', 'b') }}|{{ m(1, 2, 3) }}")

    def test_varargs(self):
        tmpl = self.env.from_string("{% macro test() %}{{ varargs|join('|') }}{% endmacro %}{{ test(1, 2, 3) }}")

    def test_simple_call(self):
        tmpl = self.env.from_string('{% macro test() %}[[{{ caller() }}]]{% endmacro %}{% call test() %}data{% endcall %}')

    def test_complex_call(self):
        tmpl = self.env.from_string("{% macro test() %}[[{{ caller('data') }}]]{% endmacro %}{% call(data) test() %}{{ data }}{% endcall %}")

    def test_caller_undefined(self):
        tmpl = self.env.from_string('{% set caller = 42 %}{% macro test() %}{{ caller is not defined }}{% endmacro %}{{ test() }}')

    def test_include(self):
        self.env = Environment(loader=DictLoader({'include': '{% macro test(foo) %}[{{ foo }}]{% endmacro %}'}))
        tmpl = self.env.from_string('{% from "include" import test %}{{ test("foo") }}')

    def test_macro_api(self):
        tmpl = self.env.from_string('{% macro foo(a, b) %}{% endmacro %}{% macro bar() %}{{ varargs }}{{ kwargs }}{% endmacro %}{% macro baz() %}{{ caller() }}{% endmacro %}')

    def test_callself(self):
        tmpl = self.env.from_string('{% macro foo(x) %}{{ x }}{% if x > 1 %}|{{ foo(x - 1) }}{% endif %}{% endmacro %}{{ foo(5) }}')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForLoopTestCase))
    suite.addTest(unittest.makeSuite(IfConditionTestCase))
    suite.addTest(unittest.makeSuite(MacrosTestCase))
    return suite