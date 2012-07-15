#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\ext.py
import re
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment, DictLoader, contextfunction, nodes
from jinja2.exceptions import TemplateAssertionError
from jinja2.ext import Extension
from jinja2.lexer import Token, count_newlines
from jinja2.utils import next
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

importable_object = 23
_gettext_re = re.compile('_\\((.*?)\\)(?s)')
i18n_templates = {'master.html': '<title>{{ page_title|default(_("missing")) }}</title>{% block body %}{% endblock %}',
 'child.html': '{% extends "master.html" %}{% block body %}{% trans %}watch out{% endtrans %}{% endblock %}',
 'plural.html': '{% trans user_count %}One user online{% pluralize %}{{ user_count }} users online{% endtrans %}',
 'stringformat.html': '{{ _("User: %(num)s")|format(num=user_count) }}'}
newstyle_i18n_templates = {'master.html': '<title>{{ page_title|default(_("missing")) }}</title>{% block body %}{% endblock %}',
 'child.html': '{% extends "master.html" %}{% block body %}{% trans %}watch out{% endtrans %}{% endblock %}',
 'plural.html': '{% trans user_count %}One user online{% pluralize %}{{ user_count }} users online{% endtrans %}',
 'stringformat.html': '{{ _("User: %(num)s", num=user_count) }}',
 'ngettext.html': '{{ ngettext("%(num)s apple", "%(num)s apples", apples) }}',
 'ngettext_long.html': '{% trans num=apples %}{{ num }} apple{% pluralize %}{{ num }} apples{% endtrans %}',
 'transvars1.html': '{% trans %}User: {{ num }}{% endtrans %}',
 'transvars2.html': '{% trans num=count %}User: {{ num }}{% endtrans %}',
 'transvars3.html': '{% trans count=num %}User: {{ count }}{% endtrans %}',
 'novars.html': '{% trans %}%(hello)s{% endtrans %}',
 'vars.html': '{% trans %}{{ foo }}%(foo)s{% endtrans %}',
 'explicitvars.html': '{% trans foo="42" %}%(foo)s{% endtrans %}'}
languages = {'de': {'missing': u'fehlend',
        'watch out': u'pass auf',
        'One user online': u'Ein Benutzer online',
        '%(user_count)s users online': u'%(user_count)s Benutzer online',
        'User: %(num)s': u'Benutzer: %(num)s',
        'User: %(count)s': u'Benutzer: %(count)s',
        '%(num)s apple': u'%(num)s Apfel',
        '%(num)s apples': u'%(num)s \xc4pfel'}}

@contextfunction
def gettext(context, string):
    language = context.get('LANGUAGE', 'en')
    return languages.get(language, {}).get(string, string)


@contextfunction
def ngettext(context, s, p, n):
    language = context.get('LANGUAGE', 'en')
    if n != 1:
        return languages.get(language, {}).get(p, p)
    return languages.get(language, {}).get(s, s)


i18n_env = Environment(loader=DictLoader(i18n_templates), extensions=['jinja2.ext.i18n'])
i18n_env.globals.update({'_': gettext,
 'gettext': gettext,
 'ngettext': ngettext})
newstyle_i18n_env = Environment(loader=DictLoader(newstyle_i18n_templates), extensions=['jinja2.ext.i18n'])
newstyle_i18n_env.install_gettext_callables(gettext, ngettext, newstyle=True)

class TestExtension(Extension):
    tags = set(['test'])
    ext_attr = 42

    def parse(self, parser):
        return nodes.Output([self.call_method('_dump', [nodes.EnvironmentAttribute('sandboxed'),
          self.attr('ext_attr'),
          nodes.ImportedName(__name__ + '.importable_object'),
          nodes.ContextReference()])]).set_lineno(next(parser.stream).lineno)

    def _dump(self, sandboxed, ext_attr, imported_object, context):
        return '%s|%s|%s|%s' % (sandboxed,
         ext_attr,
         imported_object,
         context.blocks)


class PreprocessorExtension(Extension):

    def preprocess(self, source, name, filename = None):
        return source.replace('[[TEST]]', '({{ foo }})')


class StreamFilterExtension(Extension):

    def filter_stream(self, stream):
        for token in stream:
            if token.type == 'data':
                for t in self.interpolate(token):
                    yield t

            else:
                yield token

    def interpolate(self, token):
        pos = 0
        end = len(token.value)
        lineno = token.lineno
        while 1:
            match = _gettext_re.search(token.value, pos)
            if match is None:
                break
            value = token.value[pos:match.start()]
            if value:
                yield Token(lineno, 'data', value)
            lineno += count_newlines(token.value)
            yield Token(lineno, 'variable_begin', None)
            yield Token(lineno, 'name', 'gettext')
            yield Token(lineno, 'lparen', None)
            yield Token(lineno, 'string', match.group(1))
            yield Token(lineno, 'rparen', None)
            yield Token(lineno, 'variable_end', None)
            pos = match.end()

        if pos < end:
            yield Token(lineno, 'data', token.value[pos:])


class ExtensionsTestCase(JinjaTestCase):

    def test_extend_late(self):
        env = Environment()
        env.add_extension('jinja2.ext.autoescape')
        t = env.from_string('{% autoescape true %}{{ "<test>" }}{% endautoescape %}')

    def test_loop_controls(self):
        env = Environment(extensions=['jinja2.ext.loopcontrols'])
        tmpl = env.from_string('\n            {%- for item in [1, 2, 3, 4] %}\n                {%- if item % 2 == 0 %}{% continue %}{% endif -%}\n                {{ item }}\n            {%- endfor %}')
        tmpl = env.from_string('\n            {%- for item in [1, 2, 3, 4] %}\n                {%- if item > 2 %}{% break %}{% endif -%}\n                {{ item }}\n            {%- endfor %}')

    def test_do(self):
        env = Environment(extensions=['jinja2.ext.do'])
        tmpl = env.from_string('\n            {%- set items = [] %}\n            {%- for char in "foo" %}\n                {%- do items.append(loop.index0 ~ char) %}\n            {%- endfor %}{{ items|join(\', \') }}')

    def test_with(self):
        env = Environment(extensions=['jinja2.ext.with_'])
        tmpl = env.from_string('        {% with a=42, b=23 -%}\n            {{ a }} = {{ b }}\n        {% endwith -%}\n            {{ a }} = {{ b }}        ')

    def test_extension_nodes(self):
        env = Environment(extensions=[TestExtension])
        tmpl = env.from_string('{% test %}')

    def test_identifier(self):
        pass

    def test_rebinding(self):
        original = Environment(extensions=[TestExtension])
        overlay = original.overlay()
        for env in (original, overlay):
            for ext in env.extensions.itervalues():
                pass

    def test_preprocessor_extension(self):
        env = Environment(extensions=[PreprocessorExtension])
        tmpl = env.from_string('{[[TEST]]}')

    def test_streamfilter_extension(self):
        env = Environment(extensions=[StreamFilterExtension])
        env.globals['gettext'] = lambda x: x.upper()
        tmpl = env.from_string('Foo _(bar) Baz')
        out = tmpl.render()

    def test_extension_ordering(self):

        class T1(Extension):
            priority = 1

        class T2(Extension):
            priority = 2

        env = Environment(extensions=[T1, T2])
        ext = list(env.iter_extensions())


class InternationalizationTestCase(JinjaTestCase):

    def test_trans(self):
        tmpl = i18n_env.get_template('child.html')

    def test_trans_plural(self):
        tmpl = i18n_env.get_template('plural.html')

    def test_complex_plural(self):
        tmpl = i18n_env.from_string('{% trans foo=42, count=2 %}{{ count }} item{% pluralize count %}{{ count }} items{% endtrans %}')
        self.assert_raises(TemplateAssertionError, i18n_env.from_string, '{% trans foo %}...{% pluralize bar %}...{% endtrans %}')

    def test_trans_stringformatting(self):
        tmpl = i18n_env.get_template('stringformat.html')

    def test_extract(self):
        from jinja2.ext import babel_extract
        source = BytesIO("\n        {{ gettext('Hello World') }}\n        {% trans %}Hello World{% endtrans %}\n        {% trans %}{{ users }} user{% pluralize %}{{ users }} users{% endtrans %}\n        ".encode('ascii'))

    def test_comment_extract(self):
        from jinja2.ext import babel_extract
        source = BytesIO("\n        {# trans first #}\n        {{ gettext('Hello World') }}\n        {% trans %}Hello World{% endtrans %}{# trans second #}\n        {#: third #}\n        {% trans %}{{ users }} user{% pluralize %}{{ users }} users{% endtrans %}\n        ".encode('utf-8'))


class NewstyleInternationalizationTestCase(JinjaTestCase):

    def test_trans(self):
        tmpl = newstyle_i18n_env.get_template('child.html')

    def test_trans_plural(self):
        tmpl = newstyle_i18n_env.get_template('plural.html')

    def test_complex_plural(self):
        tmpl = newstyle_i18n_env.from_string('{% trans foo=42, count=2 %}{{ count }} item{% pluralize count %}{{ count }} items{% endtrans %}')
        self.assert_raises(TemplateAssertionError, i18n_env.from_string, '{% trans foo %}...{% pluralize bar %}...{% endtrans %}')

    def test_trans_stringformatting(self):
        tmpl = newstyle_i18n_env.get_template('stringformat.html')

    def test_newstyle_plural(self):
        tmpl = newstyle_i18n_env.get_template('ngettext.html')

    def test_autoescape_support(self):
        env = Environment(extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'])
        env.install_gettext_callables(lambda x: u'<strong>Wert: %(name)s</strong>', lambda s, p, n: s, newstyle=True)
        t = env.from_string('{% autoescape ae %}{{ gettext("foo", name="<test>") }}{% endautoescape %}')

    def test_num_used_twice(self):
        tmpl = newstyle_i18n_env.get_template('ngettext_long.html')

    def test_num_called_num(self):
        source = newstyle_i18n_env.compile('\n            {% trans num=3 %}{{ num }} apple{% pluralize\n            %}{{ num }} apples{% endtrans %}\n        ', raw=True)

    def test_trans_vars(self):
        t1 = newstyle_i18n_env.get_template('transvars1.html')
        t2 = newstyle_i18n_env.get_template('transvars2.html')
        t3 = newstyle_i18n_env.get_template('transvars3.html')

    def test_novars_vars_escaping(self):
        t = newstyle_i18n_env.get_template('novars.html')
        t = newstyle_i18n_env.get_template('vars.html')
        t = newstyle_i18n_env.get_template('explicitvars.html')


class AutoEscapeTestCase(JinjaTestCase):

    def test_scoped_setting(self):
        env = Environment(extensions=['jinja2.ext.autoescape'], autoescape=True)
        tmpl = env.from_string('\n            {{ "<HelloWorld>" }}\n            {% autoescape false %}\n                {{ "<HelloWorld>" }}\n            {% endautoescape %}\n            {{ "<HelloWorld>" }}\n        ')
        env = Environment(extensions=['jinja2.ext.autoescape'], autoescape=False)
        tmpl = env.from_string('\n            {{ "<HelloWorld>" }}\n            {% autoescape true %}\n                {{ "<HelloWorld>" }}\n            {% endautoescape %}\n            {{ "<HelloWorld>" }}\n        ')

    def test_nonvolatile(self):
        env = Environment(extensions=['jinja2.ext.autoescape'], autoescape=True)
        tmpl = env.from_string('{{ {"foo": "<test>"}|xmlattr|escape }}')
        tmpl = env.from_string('{% autoescape false %}{{ {"foo": "<test>"}|xmlattr|escape }}{% endautoescape %}')

    def test_volatile(self):
        env = Environment(extensions=['jinja2.ext.autoescape'], autoescape=True)
        tmpl = env.from_string('{% autoescape foo %}{{ {"foo": "<test>"}|xmlattr|escape }}{% endautoescape %}')

    def test_scoping(self):
        env = Environment(extensions=['jinja2.ext.autoescape'])
        tmpl = env.from_string('{% autoescape true %}{% set x = "<x>" %}{{ x }}{% endautoescape %}{{ x }}{{ "<y>" }}')

    def test_volatile_scoping(self):
        env = Environment(extensions=['jinja2.ext.autoescape'])
        tmplsource = "\n        {% autoescape val %}\n            {% macro foo(x) %}\n                [{{ x }}]\n            {% endmacro %}\n            {{ foo().__class__.__name__ }}\n        {% endautoescape %}\n        {{ '<testing>' }}\n        "
        tmpl = env.from_string(tmplsource)
        env = Environment(extensions=['jinja2.ext.autoescape'])
        pysource = env.compile(tmplsource, raw=True)
        env = Environment(extensions=['jinja2.ext.autoescape'], autoescape=True)
        pysource = env.compile(tmplsource, raw=True)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExtensionsTestCase))
    suite.addTest(unittest.makeSuite(InternationalizationTestCase))
    suite.addTest(unittest.makeSuite(NewstyleInternationalizationTestCase))
    suite.addTest(unittest.makeSuite(AutoEscapeTestCase))
    return suite