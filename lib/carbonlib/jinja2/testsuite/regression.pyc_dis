#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\regression.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Template, Environment, DictLoader, TemplateSyntaxError, TemplateNotFound, PrefixLoader
env = Environment()

class CornerTestCase(JinjaTestCase):

    def test_assigned_scoping(self):
        t = env.from_string('\n        {%- for item in (1, 2, 3, 4) -%}\n            [{{ item }}]\n        {%- endfor %}\n        {{- item -}}\n        ')
        t = env.from_string('\n        {%- for item in (1, 2, 3, 4) -%}\n            [{{ item }}]\n        {%- endfor %}\n        {%- set item = 42 %}\n        {{- item -}}\n        ')
        t = env.from_string('\n        {%- set item = 42 %}\n        {%- for item in (1, 2, 3, 4) -%}\n            [{{ item }}]\n        {%- endfor %}\n        {{- item -}}\n        ')

    def test_closure_scoping(self):
        t = env.from_string('\n        {%- set wrapper = "<FOO>" %}\n        {%- for item in (1, 2, 3, 4) %}\n            {%- macro wrapper() %}[{{ item }}]{% endmacro %}\n            {{- wrapper() }}\n        {%- endfor %}\n        {{- wrapper -}}\n        ')
        t = env.from_string('\n        {%- for item in (1, 2, 3, 4) %}\n            {%- macro wrapper() %}[{{ item }}]{% endmacro %}\n            {{- wrapper() }}\n        {%- endfor %}\n        {%- set wrapper = "<FOO>" %}\n        {{- wrapper -}}\n        ')
        t = env.from_string('\n        {%- for item in (1, 2, 3, 4) %}\n            {%- macro wrapper() %}[{{ item }}]{% endmacro %}\n            {{- wrapper() }}\n        {%- endfor %}\n        {{- wrapper -}}\n        ')


class BugTestCase(JinjaTestCase):

    def test_keyword_folding(self):
        env = Environment()
        env.filters['testing'] = lambda value, some: value + some

    def test_extends_output_bugs(self):
        env = Environment(loader=DictLoader({'parent.html': '(({% block title %}{% endblock %}))'}))
        t = env.from_string('{% if expr %}{% extends "parent.html" %}{% endif %}[[{% block title %}title{% endblock %}]]{% for item in [1, 2, 3] %}({{ item }}){% endfor %}')

    def test_urlize_filter_escaping(self):
        tmpl = env.from_string('{{ "http://www.example.org/<foo"|urlize }}')

    def test_loop_call_loop(self):
        tmpl = env.from_string('\n\n        {% macro test() %}\n            {{ caller() }}\n        {% endmacro %}\n\n        {% for num1 in range(5) %}\n            {% call test() %}\n                {% for num2 in range(10) %}\n                    {{ loop.index }}\n                {% endfor %}\n            {% endcall %}\n        {% endfor %}\n\n        ')

    def test_weird_inline_comment(self):
        env = Environment(line_statement_prefix='%')
        self.assert_raises(TemplateSyntaxError, env.from_string, '% for item in seq {# missing #}\n...% endfor')

    def test_old_macro_loop_scoping_bug(self):
        tmpl = env.from_string('{% for i in (1, 2) %}{{ i }}{% endfor %}{% macro i() %}3{% endmacro %}{{ i() }}')

    def test_partial_conditional_assignments(self):
        tmpl = env.from_string('{% if b %}{% set a = 42 %}{% endif %}{{ a }}')

    def test_stacked_locals_scoping_bug(self):
        env = Environment(line_statement_prefix='#')
        t = env.from_string("# for j in [1, 2]:\n#   set x = 1\n#   for i in [1, 2]:\n#     print x\n#     if i % 2 == 0:\n#       set x = x + 1\n#     endif\n#   endfor\n# endfor\n# if a\n#   print 'A'\n# elif b\n#   print 'B'\n# elif c == d\n#   print 'C'\n# else\n#   print 'D'\n# endif\n    ")

    def test_stacked_locals_scoping_bug_twoframe(self):
        t = Template('\n            {% set x = 1 %}\n            {% for item in foo %}\n                {% if item == 1 %}\n                    {% set x = 2 %}\n                {% endif %}\n            {% endfor %}\n            {{ x }}\n        ')
        rv = t.render(foo=[1]).strip()

    def test_call_with_args(self):
        t = Template('{% macro dump_users(users) -%}\n        <ul>\n          {%- for user in users -%}\n            <li><p>{{ user.username|e }}</p>{{ caller(user) }}</li>\n          {%- endfor -%}\n          </ul>\n        {%- endmacro -%}\n\n        {% call(user) dump_users(list_of_user) -%}\n          <dl>\n            <dl>Realname</dl>\n            <dd>{{ user.realname|e }}</dd>\n            <dl>Description</dl>\n            <dd>{{ user.description }}</dd>\n          </dl>\n        {% endcall %}')

    def test_empty_if_condition_fails(self):
        self.assert_raises(TemplateSyntaxError, Template, '{% if %}....{% endif %}')
        self.assert_raises(TemplateSyntaxError, Template, '{% if foo %}...{% elif %}...{% endif %}')
        self.assert_raises(TemplateSyntaxError, Template, '{% for x in %}..{% endfor %}')

    def test_recursive_loop_bug(self):
        tpl1 = Template('\n        {% for p in foo recursive%}\n            {{p.bar}}\n            {% for f in p.fields recursive%}\n                {{f.baz}}\n                {{p.bar}}\n                {% if f.rec %}\n                    {{ loop(f.sub) }}\n                {% endif %}\n            {% endfor %}\n        {% endfor %}\n        ')
        tpl2 = Template('\n        {% for p in foo%}\n            {{p.bar}}\n            {% for f in p.fields recursive%}\n                {{f.baz}}\n                {{p.bar}}\n                {% if f.rec %}\n                    {{ loop(f.sub) }}\n                {% endif %}\n            {% endfor %}\n        {% endfor %}\n        ')

    def test_correct_prefix_loader_name(self):
        env = Environment(loader=PrefixLoader({'foo': DictLoader({})}))
        try:
            env.get_template('foo/bar.html')
        except TemplateNotFound as e:
            pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CornerTestCase))
    suite.addTest(unittest.makeSuite(BugTestCase))
    return suite