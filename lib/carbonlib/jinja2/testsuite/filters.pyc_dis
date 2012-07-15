#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\testsuite\filters.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Markup, Environment
env = Environment()

class FilterTestCase(JinjaTestCase):

    def test_capitalize(self):
        tmpl = env.from_string('{{ "foo bar"|capitalize }}')

    def test_center(self):
        tmpl = env.from_string('{{ "foo"|center(9) }}')

    def test_default(self):
        tmpl = env.from_string("{{ missing|default('no') }}|{{ false|default('no') }}|{{ false|default('no', true) }}|{{ given|default('no') }}")

    def test_dictsort(self):
        tmpl = env.from_string('{{ foo|dictsort }}|{{ foo|dictsort(true) }}|{{ foo|dictsort(false, "value") }}')
        out = tmpl.render(foo={'aa': 0,
         'b': 1,
         'c': 2,
         'AB': 3})

    def test_batch(self):
        tmpl = env.from_string("{{ foo|batch(3)|list }}|{{ foo|batch(3, 'X')|list }}")
        out = tmpl.render(foo=range(10))

    def test_slice(self):
        tmpl = env.from_string('{{ foo|slice(3)|list }}|{{ foo|slice(3, "X")|list }}')
        out = tmpl.render(foo=range(10))

    def test_escape(self):
        tmpl = env.from_string('{{ \'<">&\'|escape }}')
        out = tmpl.render()

    def test_striptags(self):
        tmpl = env.from_string('{{ foo|striptags }}')
        out = tmpl.render(foo='  <p>just a small   \n <a href="#">example</a> link</p>\n<p>to a webpage</p> <!-- <p>and some commented stuff</p> -->')

    def test_filesizeformat(self):
        tmpl = env.from_string('{{ 100|filesizeformat }}|{{ 1000|filesizeformat }}|{{ 1000000|filesizeformat }}|{{ 1000000000|filesizeformat }}|{{ 1000000000000|filesizeformat }}|{{ 100|filesizeformat(true) }}|{{ 1000|filesizeformat(true) }}|{{ 1000000|filesizeformat(true) }}|{{ 1000000000|filesizeformat(true) }}|{{ 1000000000000|filesizeformat(true) }}')
        out = tmpl.render()
        self.assert_equal(out, '100 Bytes|1.0 kB|1.0 MB|1.0 GB|1.0 TB|100 Bytes|1000 Bytes|976.6 KiB|953.7 MiB|931.3 GiB')

    def test_filesizeformat_issue59(self):
        tmpl = env.from_string('{{ 300|filesizeformat }}|{{ 3000|filesizeformat }}|{{ 3000000|filesizeformat }}|{{ 3000000000|filesizeformat }}|{{ 3000000000000|filesizeformat }}|{{ 300|filesizeformat(true) }}|{{ 3000|filesizeformat(true) }}|{{ 3000000|filesizeformat(true) }}')
        out = tmpl.render()
        self.assert_equal(out, '300 Bytes|3.0 kB|3.0 MB|3.0 GB|3.0 TB|300 Bytes|2.9 KiB|2.9 MiB')

    def test_first(self):
        tmpl = env.from_string('{{ foo|first }}')
        out = tmpl.render(foo=range(10))

    def test_float(self):
        tmpl = env.from_string('{{ "42"|float }}|{{ "ajsghasjgd"|float }}|{{ "32.32"|float }}')
        out = tmpl.render()

    def test_format(self):
        tmpl = env.from_string('{{ "%s|%s"|format("a", "b") }}')
        out = tmpl.render()

    def test_indent(self):
        tmpl = env.from_string('{{ foo|indent(2) }}|{{ foo|indent(2, true) }}')
        text = '\n'.join([' '.join(['foo', 'bar'] * 2)] * 2)
        out = tmpl.render(foo=text)

    def test_int(self):
        tmpl = env.from_string('{{ "42"|int }}|{{ "ajsghasjgd"|int }}|{{ "32.32"|int }}')
        out = tmpl.render()

    def test_join(self):
        tmpl = env.from_string('{{ [1, 2, 3]|join("|") }}')
        out = tmpl.render()
        env2 = Environment(autoescape=True)
        tmpl = env2.from_string('{{ ["<foo>", "<span>foo</span>"|safe]|join }}')

    def test_join_attribute(self):

        class User(object):

            def __init__(self, username):
                self.username = username

        tmpl = env.from_string("{{ users|join(', ', 'username') }}")

    def test_last(self):
        tmpl = env.from_string('{{ foo|last }}')
        out = tmpl.render(foo=range(10))

    def test_length(self):
        tmpl = env.from_string('{{ "hello world"|length }}')
        out = tmpl.render()

    def test_lower(self):
        tmpl = env.from_string('{{ "FOO"|lower }}')
        out = tmpl.render()

    def test_pprint(self):
        from pprint import pformat
        tmpl = env.from_string('{{ data|pprint }}')
        data = range(1000)

    def test_random(self):
        tmpl = env.from_string('{{ seq|random }}')
        seq = range(100)
        for _ in range(10):
            pass

    def test_reverse(self):
        tmpl = env.from_string('{{ "foobar"|reverse|join }}|{{ [1, 2, 3]|reverse|list }}')

    def test_string(self):
        x = [1,
         2,
         3,
         4,
         5]
        tmpl = env.from_string('{{ obj|string }}')

    def test_title(self):
        tmpl = env.from_string('{{ "foo bar"|title }}')

    def test_truncate(self):
        tmpl = env.from_string('{{ data|truncate(15, true, ">>>") }}|{{ data|truncate(15, false, ">>>") }}|{{ smalldata|truncate(15) }}')
        out = tmpl.render(data='foobar baz bar' * 1000, smalldata='foobar baz bar')

    def test_upper(self):
        tmpl = env.from_string('{{ "foo"|upper }}')

    def test_urlize(self):
        tmpl = env.from_string('{{ "foo http://www.example.com/ bar"|urlize }}')

    def test_wordcount(self):
        tmpl = env.from_string('{{ "foo bar baz"|wordcount }}')

    def test_block(self):
        tmpl = env.from_string('{% filter lower|escape %}<HEHE>{% endfilter %}')

    def test_chaining(self):
        tmpl = env.from_string("{{ ['<foo>', '<bar>']|first|upper|escape }}")

    def test_sum(self):
        tmpl = env.from_string('{{ [1, 2, 3, 4, 5, 6]|sum }}')

    def test_sum_attributes(self):
        tmpl = env.from_string("{{ values|sum('value') }}")

    def test_sum_attributes_nested(self):
        tmpl = env.from_string("{{ values|sum('real.value') }}")

    def test_abs(self):
        tmpl = env.from_string('{{ -1|abs }}|{{ 1|abs }}')

    def test_round_positive(self):
        tmpl = env.from_string("{{ 2.7|round }}|{{ 2.1|round }}|{{ 2.1234|round(3, 'floor') }}|{{ 2.1|round(0, 'ceil') }}")

    def test_round_negative(self):
        tmpl = env.from_string("{{ 21.3|round(-1)}}|{{ 21.3|round(-1, 'ceil')}}|{{ 21.3|round(-1, 'floor')}}")

    def test_xmlattr(self):
        tmpl = env.from_string("{{ {'foo': 42, 'bar': 23, 'fish': none, 'spam': missing, 'blub:blub': '<?>'}|xmlattr }}")
        out = tmpl.render().split()

    def test_sort1(self):
        tmpl = env.from_string('{{ [2, 3, 1]|sort }}|{{ [2, 3, 1]|sort(true) }}')

    def test_sort2(self):
        tmpl = env.from_string('{{ "".join(["c", "A", "b", "D"]|sort) }}')

    def test_sort3(self):
        tmpl = env.from_string("{{ ['foo', 'Bar', 'blah']|sort }}")

    def test_sort4(self):

        class Magic(object):

            def __init__(self, value):
                self.value = value

            def __unicode__(self):
                return unicode(self.value)

        tmpl = env.from_string("{{ items|sort(attribute='value')|join }}")

    def test_groupby(self):
        tmpl = env.from_string("\n        {%- for grouper, list in [{'foo': 1, 'bar': 2},\n                                  {'foo': 2, 'bar': 3},\n                                  {'foo': 1, 'bar': 1},\n                                  {'foo': 3, 'bar': 4}]|groupby('foo') -%}\n            {{ grouper }}{% for x in list %}: {{ x.foo }}, {{ x.bar }}{% endfor %}|\n        {%- endfor %}")

    def test_groupby_tuple_index(self):
        tmpl = env.from_string("\n        {%- for grouper, list in [('a', 1), ('a', 2), ('b', 1)]|groupby(0) -%}\n            {{ grouper }}{% for x in list %}:{{ x.1 }}{% endfor %}|\n        {%- endfor %}")

    def test_groupby_multidot(self):

        class Date(object):

            def __init__(self, day, month, year):
                self.day = day
                self.month = month
                self.year = year

        class Article(object):

            def __init__(self, title, *date):
                self.date = Date(*date)
                self.title = title

        articles = [Article('aha', 1, 1, 1970),
         Article('interesting', 2, 1, 1970),
         Article('really?', 3, 1, 1970),
         Article('totally not', 1, 1, 1971)]
        tmpl = env.from_string("\n        {%- for year, list in articles|groupby('date.year') -%}\n            {{ year }}{% for x in list %}[{{ x.title }}]{% endfor %}|\n        {%- endfor %}")

    def test_filtertag(self):
        tmpl = env.from_string("{% filter upper|replace('FOO', 'foo') %}foobar{% endfilter %}")

    def test_replace(self):
        env = Environment()
        tmpl = env.from_string('{{ string|replace("o", 42) }}')
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ string|replace("o", 42) }}')
        tmpl = env.from_string('{{ string|replace("<", 42) }}')
        tmpl = env.from_string('{{ string|replace("o", ">x<") }}')

    def test_forceescape(self):
        tmpl = env.from_string('{{ x|forceescape }}')

    def test_safe(self):
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ "<div>foo</div>"|safe }}')
        tmpl = env.from_string('{{ "<div>foo</div>" }}')

    def test_urlencode(self):
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ "Hello, world!"|urlencode }}')
        tmpl = env.from_string('{{ o|urlencode }}')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilterTestCase))
    return suite