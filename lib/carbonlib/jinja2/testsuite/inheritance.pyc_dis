#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\inheritance.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment, DictLoader
LAYOUTTEMPLATE = '|{% block block1 %}block 1 from layout{% endblock %}\n|{% block block2 %}block 2 from layout{% endblock %}\n|{% block block3 %}\n{% block block4 %}nested block 4 from layout{% endblock %}\n{% endblock %}|'
LEVEL1TEMPLATE = '{% extends "layout" %}\n{% block block1 %}block 1 from level1{% endblock %}'
LEVEL2TEMPLATE = '{% extends "level1" %}\n{% block block2 %}{% block block5 %}nested block 5 from level2{%\nendblock %}{% endblock %}'
LEVEL3TEMPLATE = '{% extends "level2" %}\n{% block block5 %}block 5 from level3{% endblock %}\n{% block block4 %}block 4 from level3{% endblock %}\n'
LEVEL4TEMPLATE = '{% extends "level3" %}\n{% block block3 %}block 3 from level4{% endblock %}\n'
WORKINGTEMPLATE = '{% extends "layout" %}\n{% block block1 %}\n  {% if false %}\n    {% block block2 %}\n      this should workd\n    {% endblock %}\n  {% endif %}\n{% endblock %}\n'
env = Environment(loader=DictLoader({'layout': LAYOUTTEMPLATE,
 'level1': LEVEL1TEMPLATE,
 'level2': LEVEL2TEMPLATE,
 'level3': LEVEL3TEMPLATE,
 'level4': LEVEL4TEMPLATE,
 'working': WORKINGTEMPLATE}), trim_blocks=True)

class InheritanceTestCase(JinjaTestCase):

    def test_layout(self):
        tmpl = env.get_template('layout')

    def test_level1(self):
        tmpl = env.get_template('level1')

    def test_level2(self):
        tmpl = env.get_template('level2')

    def test_level3(self):
        tmpl = env.get_template('level3')

    def test_level4(sel):
        tmpl = env.get_template('level4')

    def test_super(self):
        env = Environment(loader=DictLoader({'a': '{% block intro %}INTRO{% endblock %}|BEFORE|{% block data %}INNER{% endblock %}|AFTER',
         'b': '{% extends "a" %}{% block data %}({{ super() }}){% endblock %}',
         'c': '{% extends "b" %}{% block intro %}--{{ super() }}--{% endblock %}\n{% block data %}[{{ super() }}]{% endblock %}'}))
        tmpl = env.get_template('c')

    def test_working(self):
        tmpl = env.get_template('working')

    def test_reuse_blocks(self):
        tmpl = env.from_string('{{ self.foo() }}|{% block foo %}42{% endblock %}|{{ self.foo() }}')

    def test_preserve_blocks(self):
        env = Environment(loader=DictLoader({'a': '{% if false %}{% block x %}A{% endblock %}{% endif %}{{ self.x() }}',
         'b': '{% extends "a" %}{% block x %}B{{ super() }}{% endblock %}'}))
        tmpl = env.get_template('b')

    def test_dynamic_inheritance(self):
        env = Environment(loader=DictLoader({'master1': 'MASTER1{% block x %}{% endblock %}',
         'master2': 'MASTER2{% block x %}{% endblock %}',
         'child': '{% extends master %}{% block x %}CHILD{% endblock %}'}))
        tmpl = env.get_template('child')
        for m in range(1, 3):
            pass

    def test_multi_inheritance(self):
        env = Environment(loader=DictLoader({'master1': 'MASTER1{% block x %}{% endblock %}',
         'master2': 'MASTER2{% block x %}{% endblock %}',
         'child': "{% if master %}{% extends master %}{% else %}{% extends\n                        'master1' %}{% endif %}{% block x %}CHILD{% endblock %}"}))
        tmpl = env.get_template('child')

    def test_scoped_block(self):
        env = Environment(loader=DictLoader({'master.html': '{% for item in seq %}[{% block item scoped %}{% endblock %}]{% endfor %}'}))
        t = env.from_string('{% extends "master.html" %}{% block item %}{{ item }}{% endblock %}')

    def test_super_in_scoped_block(self):
        env = Environment(loader=DictLoader({'master.html': '{% for item in seq %}[{% block item scoped %}{{ item }}{% endblock %}]{% endfor %}'}))
        t = env.from_string('{% extends "master.html" %}{% block item %}{{ super() }}|{{ item * 2 }}{% endblock %}')

    def test_scoped_block_after_inheritance(self):
        env = Environment(loader=DictLoader({'layout.html': '\n            {% block useless %}{% endblock %}\n            ',
         'index.html': "\n            {%- extends 'layout.html' %}\n            {% from 'helpers.html' import foo with context %}\n            {% block useless %}\n                {% for x in [1, 2, 3] %}\n                    {% block testing scoped %}\n                        {{ foo(x) }}\n                    {% endblock %}\n                {% endfor %}\n            {% endblock %}\n            ",
         'helpers.html': '\n            {% macro foo(x) %}{{ the_foo + x }}{% endmacro %}\n            '}))
        rv = env.get_template('index.html').render(the_foo=42).split()


class BugFixTestCase(JinjaTestCase):

    def test_fixed_macro_scoping_bug(self):
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InheritanceTestCase))
    suite.addTest(unittest.makeSuite(BugFixTestCase))
    return suite