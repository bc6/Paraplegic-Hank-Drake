#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\routing.py
import re
from pprint import pformat
from urlparse import urljoin
from itertools import izip
from werkzeug.urls import url_encode, url_quote
from werkzeug.utils import redirect, format_string
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed
from werkzeug._internal import _get_environ
_rule_re = re.compile('\n    (?P<static>[^<]*)                           # static rule data\n    <\n    (?:\n        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name\n        (?:\\((?P<args>.*?)\\))?                  # converter arguments\n        \\:                                      # variable delimiter\n    )?\n    (?P<variable>[a-zA-Z][a-zA-Z0-9_]*)         # variable name\n    >\n', re.VERBOSE)
_simple_rule_re = re.compile('<([^>]+)>')

def parse_rule(rule):
    pos = 0
    end = len(rule)
    do_match = _rule_re.match
    used_names = set()
    while pos < end:
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        if data['static']:
            yield (None, None, data['static'])
        variable = data['variable']
        converter = data['converter'] or 'default'
        if variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(variable)
        yield (converter, data['args'] or None, variable)
        pos = m.end()

    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield (None, None, remaining)


def get_converter(map, name, args):
    if name not in map.converters:
        raise LookupError('the converter %r does not exist' % name)
    if args:
        storage = type('_Storage', (), {'__getitem__': lambda s, x: x})()
        args, kwargs = eval(u'(lambda *a, **kw: (a, kw))(%s)' % args, {}, storage)
    else:
        args = ()
        kwargs = {}
    return map.converters[name](map, *args, **kwargs)


class RoutingException(Exception):
    pass


class RequestRedirect(HTTPException, RoutingException):
    code = 301

    def __init__(self, new_url):
        RoutingException.__init__(self, new_url)
        self.new_url = new_url

    def get_response(self, environ):
        return redirect(self.new_url, 301)


class RequestSlash(RoutingException):
    pass


class BuildError(RoutingException, LookupError):

    def __init__(self, endpoint, values, method):
        LookupError.__init__(self, endpoint, values, method)
        self.endpoint = endpoint
        self.values = values
        self.method = method


class ValidationError(ValueError):
    pass


class RuleFactory(object):

    def get_rules(self, map):
        raise NotImplementedError()


class Subdomain(RuleFactory):

    def __init__(self, subdomain, rules):
        self.subdomain = subdomain
        self.rules = rules

    def get_rules(self, map):
        for rulefactory in self.rules:
            for rule in rulefactory.get_rules(map):
                rule = rule.empty()
                rule.subdomain = self.subdomain
                yield rule


class Submount(RuleFactory):

    def __init__(self, path, rules):
        self.path = path.rstrip('/')
        self.rules = rules

    def get_rules(self, map):
        for rulefactory in self.rules:
            for rule in rulefactory.get_rules(map):
                rule = rule.empty()
                rule.rule = self.path + rule.rule
                yield rule


class EndpointPrefix(RuleFactory):

    def __init__(self, prefix, rules):
        self.prefix = prefix
        self.rules = rules

    def get_rules(self, map):
        for rulefactory in self.rules:
            for rule in rulefactory.get_rules(map):
                rule = rule.empty()
                rule.endpoint = self.prefix + rule.endpoint
                yield rule


class RuleTemplate(object):

    def __init__(self, rules):
        self.rules = list(rules)

    def __call__(self, *args, **kwargs):
        return RuleTemplateFactory(self.rules, dict(*args, **kwargs))


class RuleTemplateFactory(RuleFactory):

    def __init__(self, rules, context):
        self.rules = rules
        self.context = context

    def get_rules(self, map):
        for rulefactory in self.rules:
            for rule in rulefactory.get_rules(map):
                new_defaults = subdomain = None
                if rule.defaults is not None:
                    new_defaults = {}
                    for key, value in rule.defaults.iteritems():
                        if isinstance(value, basestring):
                            value = format_string(value, self.context)
                        new_defaults[key] = value

                if rule.subdomain is not None:
                    subdomain = format_string(rule.subdomain, self.context)
                new_endpoint = rule.endpoint
                if isinstance(new_endpoint, basestring):
                    new_endpoint = format_string(new_endpoint, self.context)
                yield Rule(format_string(rule.rule, self.context), new_defaults, subdomain, rule.methods, rule.build_only, new_endpoint, rule.strict_slashes)


class Rule(RuleFactory):

    def __init__(self, string, defaults = None, subdomain = None, methods = None, build_only = False, endpoint = None, strict_slashes = None, redirect_to = None):
        if not string.startswith('/'):
            raise ValueError('urls must start with a leading slash')
        self.rule = string
        self.is_leaf = not string.endswith('/')
        self.map = None
        self.strict_slashes = strict_slashes
        self.subdomain = subdomain
        self.defaults = defaults
        self.build_only = build_only
        if methods is None:
            self.methods = None
        else:
            self.methods = set([ x.upper() for x in methods ])
            if 'HEAD' not in self.methods and 'GET' in self.methods:
                self.methods.add('HEAD')
        self.endpoint = endpoint
        self.greediness = 0
        self.redirect_to = redirect_to
        if defaults is not None:
            self.arguments = set(map(str, defaults))
        else:
            self.arguments = set()
        self._trace = self._converters = self._regex = self._weights = None

    def empty(self):
        defaults = None
        if self.defaults is not None:
            defaults = dict(self.defaults)
        return Rule(self.rule, defaults, self.subdomain, self.methods, self.build_only, self.endpoint, self.strict_slashes, self.redirect_to)

    def get_rules(self, map):
        yield self

    def refresh(self):
        self.bind(self.map, rebind=True)

    def bind(self, map, rebind = False):
        if self.map is not None and not rebind:
            raise RuntimeError('url rule %r already bound to map %r' % (self, self.map))
        self.map = map
        if self.strict_slashes is None:
            self.strict_slashes = map.strict_slashes
        if self.subdomain is None:
            self.subdomain = map.default_subdomain
        rule = self.subdomain + '|' + (self.is_leaf and self.rule or self.rule.rstrip('/'))
        self._trace = []
        self._converters = {}
        self._weights = []
        regex_parts = []
        for converter, arguments, variable in parse_rule(rule):
            if converter is None:
                regex_parts.append(re.escape(variable))
                self._trace.append((False, variable))
                self._weights.append(len(variable))
            else:
                convobj = get_converter(map, converter, arguments)
                regex_parts.append('(?P<%s>%s)' % (variable, convobj.regex))
                self._converters[variable] = convobj
                self._trace.append((True, variable))
                self._weights.append(convobj.weight)
                self.arguments.add(str(variable))
                if convobj.is_greedy:
                    self.greediness += 1

        if not self.is_leaf:
            self._trace.append((False, '/'))
        if not self.build_only:
            regex = '^%s%s$' % (u''.join(regex_parts), (not self.is_leaf or not self.strict_slashes) and '(?<!/)(?P<__suffix__>/?)' or '')
            self._regex = re.compile(regex, re.UNICODE)

    def match(self, path):
        if not self.build_only:
            m = self._regex.search(path)
            if m is not None:
                groups = m.groupdict()
                if self.strict_slashes and not self.is_leaf and not groups.pop('__suffix__'):
                    raise RequestSlash()
                elif not self.strict_slashes:
                    del groups['__suffix__']
                result = {}
                for name, value in groups.iteritems():
                    try:
                        value = self._converters[name].to_python(value)
                    except ValidationError:
                        return

                    result[str(name)] = value

                if self.defaults is not None:
                    result.update(self.defaults)
                return result

    def build(self, values, append_unknown = True):
        tmp = []
        add = tmp.append
        processed = set(self.arguments)
        for is_dynamic, data in self._trace:
            if is_dynamic:
                try:
                    add(self._converters[data].to_url(values[data]))
                except ValidationError:
                    return

                processed.add(data)
            else:
                add(data)

        subdomain, url = u''.join(tmp).split('|', 1)
        if append_unknown:
            query_vars = MultiDict(values)
            for key in processed:
                if key in query_vars:
                    del query_vars[key]

            if query_vars:
                url += '?' + url_encode(query_vars, self.map.charset, sort=self.map.sort_parameters, key=self.map.sort_key)
        return (subdomain, url)

    def provides_defaults_for(self, rule):
        return not self.build_only and self.defaults is not None and self.endpoint == rule.endpoint and self != rule and self.arguments == rule.arguments

    def suitable_for(self, values, method = None):
        if method is not None:
            if self.methods is not None and method not in self.methods:
                return False
        valueset = set(values)
        for key in self.arguments - set(self.defaults or ()):
            if key not in values:
                return False

        if self.arguments.issubset(valueset):
            if self.defaults is None:
                return True
            for key, value in self.defaults.iteritems():
                if value != values[key]:
                    return False

        return True

    def match_compare(self, other):
        for sw, ow in izip(self._weights, other._weights):
            if sw > ow:
                return -1
            if sw < ow:
                return 1

        if len(self._weights) > len(other._weights):
            return -1
        if len(self._weights) < len(other._weights):
            return 1
        if not other.arguments and self.arguments:
            return 1
        if other.arguments and not self.arguments:
            return -1
        if other.defaults is None and self.defaults is not None:
            return 1
        if other.defaults is not None and self.defaults is None:
            return -1
        if self.greediness > other.greediness:
            return -1
        if self.greediness < other.greediness:
            return 1
        if len(self.arguments) > len(other.arguments):
            return 1
        if len(self.arguments) < len(other.arguments):
            return -1
        return 1

    def build_compare(self, other):
        if not other.arguments and self.arguments:
            return -1
        if other.arguments and not self.arguments:
            return 1
        if other.defaults is None and self.defaults is not None:
            return -1
        if other.defaults is not None and self.defaults is None:
            return 1
        if self.provides_defaults_for(other):
            return -1
        if other.provides_defaults_for(self):
            return 1
        if self.greediness > other.greediness:
            return -1
        if self.greediness < other.greediness:
            return 1
        if len(self.arguments) > len(other.arguments):
            return -1
        if len(self.arguments) < len(other.arguments):
            return 1
        return -1

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self._trace == other._trace

    def __ne__(self, other):
        return not self.__eq__(other)

    def __unicode__(self):
        return self.rule

    def __str__(self):
        charset = self.map is not None and self.map.charset or 'utf-8'
        return unicode(self).encode(charset)

    def __repr__(self):
        if self.map is None:
            return '<%s (unbound)>' % self.__class__.__name__
        charset = self.map is not None and self.map.charset or 'utf-8'
        tmp = []
        for is_dynamic, data in self._trace:
            if is_dynamic:
                tmp.append('<%s>' % data)
            else:
                tmp.append(data)

        return '<%s %r%s -> %s>' % (self.__class__.__name__,
         u''.join(tmp).encode(charset).lstrip('|'),
         self.methods is not None and ' (%s)' % ', '.join(self.methods) or '',
         self.endpoint)


class BaseConverter(object):
    regex = '[^/]+'
    is_greedy = False
    weight = 100

    def __init__(self, map):
        self.map = map

    def to_python(self, value):
        return value

    def to_url(self, value):
        return url_quote(value, self.map.charset)


class UnicodeConverter(BaseConverter):

    def __init__(self, map, minlength = 1, maxlength = None, length = None):
        BaseConverter.__init__(self, map)
        if length is not None:
            length = '{%d}' % int(length)
        else:
            if maxlength is None:
                maxlength = ''
            else:
                maxlength = int(maxlength)
            length = '{%s,%s}' % (int(minlength), maxlength)
        self.regex = '[^/]' + length


class AnyConverter(BaseConverter):

    def __init__(self, map, *items):
        BaseConverter.__init__(self, map)
        self.regex = '(?:%s)' % '|'.join([ re.escape(x) for x in items ])


class PathConverter(BaseConverter):
    regex = '[^/].*?'
    is_greedy = True
    weight = 50


class NumberConverter(BaseConverter):

    def __init__(self, map, fixed_digits = 0, min = None, max = None):
        BaseConverter.__init__(self, map)
        self.fixed_digits = fixed_digits
        self.min = min
        self.max = max

    def to_python(self, value):
        if self.fixed_digits and len(value) != self.fixed_digits:
            raise ValidationError()
        value = self.num_convert(value)
        if self.min is not None and value < self.min or self.max is not None and value > self.max:
            raise ValidationError()
        return value

    def to_url(self, value):
        value = self.num_convert(value)
        if self.fixed_digits:
            value = '%%0%sd' % self.fixed_digits % value
        return str(value)


class IntegerConverter(NumberConverter):
    regex = '\\d+'
    num_convert = int


class FloatConverter(NumberConverter):
    regex = '\\d+\\.\\d+'
    num_convert = float

    def __init__(self, map, min = None, max = None):
        NumberConverter.__init__(self, map, 0, min, max)


class Map(object):
    default_converters = None

    def __init__(self, rules = None, default_subdomain = '', charset = 'utf-8', strict_slashes = True, redirect_defaults = True, converters = None, sort_parameters = False, sort_key = None):
        self._rules = []
        self._rules_by_endpoint = {}
        self._remap = True
        self.default_subdomain = default_subdomain
        self.charset = charset
        self.strict_slashes = strict_slashes
        self.redirect_defaults = redirect_defaults
        self.converters = self.default_converters.copy()
        if converters:
            self.converters.update(converters)
        self.sort_parameters = sort_parameters
        self.sort_key = sort_key
        for rulefactory in rules or ():
            self.add(rulefactory)

    def is_endpoint_expecting(self, endpoint, *arguments):
        self.update()
        arguments = set(arguments)
        for rule in self._rules_by_endpoint[endpoint]:
            if arguments.issubset(rule.arguments):
                return True

        return False

    def iter_rules(self, endpoint = None):
        if endpoint is not None:
            return iter(self._rules_by_endpoint[endpoint])
        return iter(self._rules)

    def add(self, rulefactory):
        for rule in rulefactory.get_rules(self):
            rule.bind(self)
            self._rules.append(rule)
            self._rules_by_endpoint.setdefault(rule.endpoint, []).append(rule)

        self._remap = True

    def bind(self, server_name, script_name = None, subdomain = None, url_scheme = 'http', default_method = 'GET', path_info = None):
        if subdomain is None:
            subdomain = self.default_subdomain
        if script_name is None:
            script_name = '/'
        return MapAdapter(self, server_name, script_name, subdomain, url_scheme, path_info, default_method)

    def bind_to_environ(self, environ, server_name = None, subdomain = None):
        environ = _get_environ(environ)
        if server_name is None:
            if 'HTTP_HOST' in environ:
                server_name = environ['HTTP_HOST']
            else:
                server_name = environ['SERVER_NAME']
                if (environ['wsgi.url_scheme'], environ['SERVER_PORT']) not in (('https', '443'), ('http', '80')):
                    server_name += ':' + environ['SERVER_PORT']
        elif subdomain is None:
            wsgi_server_name = environ.get('HTTP_HOST', environ['SERVER_NAME'])
            cur_server_name = wsgi_server_name.split(':', 1)[0].split('.')
            real_server_name = server_name.split(':', 1)[0].split('.')
            offset = -len(real_server_name)
            if cur_server_name[offset:] != real_server_name:
                raise ValueError('the server name provided (%r) does not match the server name from the WSGI environment (%r)' % (server_name, wsgi_server_name))
            subdomain = '.'.join(filter(None, cur_server_name[:offset]))
        return Map.bind(self, server_name, environ.get('SCRIPT_NAME'), subdomain, environ['wsgi.url_scheme'], environ['REQUEST_METHOD'], environ.get('PATH_INFO'))

    def update(self):
        if self._remap:
            self._rules.sort(lambda a, b: a.match_compare(b))
            for rules in self._rules_by_endpoint.itervalues():
                rules.sort(lambda a, b: a.build_compare(b))

            self._remap = False

    def __repr__(self):
        rules = self.iter_rules()
        return '%s([%s])' % (self.__class__.__name__, pformat(list(rules)))


class MapAdapter(object):

    def __init__(self, map, server_name, script_name, subdomain, url_scheme, path_info, default_method):
        self.map = map
        self.server_name = server_name
        if not script_name.endswith('/'):
            script_name += '/'
        self.script_name = script_name
        self.subdomain = subdomain
        self.url_scheme = url_scheme
        self.path_info = path_info or u''
        self.default_method = default_method

    def dispatch(self, view_func, path_info = None, method = None, catch_http_exceptions = False):
        try:
            try:
                endpoint, args = self.match(path_info, method)
            except RequestRedirect as e:
                return e

            return view_func(endpoint, args)
        except HTTPException as e:
            if catch_http_exceptions:
                return e
            raise 

    def match(self, path_info = None, method = None, return_rule = False):
        self.map.update()
        if path_info is None:
            path_info = self.path_info
        if not isinstance(path_info, unicode):
            path_info = path_info.decode(self.map.charset, 'ignore')
        method = (method or self.default_method).upper()
        path = u'%s|/%s' % (self.subdomain, path_info.lstrip('/'))
        have_match_for = set()
        for rule in self.map._rules:
            try:
                rv = rule.match(path)
            except RequestSlash:
                raise RequestRedirect(str('%s://%s%s%s/%s/' % (self.url_scheme,
                 self.subdomain and self.subdomain + '.' or '',
                 self.server_name,
                 self.script_name[:-1],
                 url_quote(path_info.lstrip('/'), self.map.charset))))

            if rv is None:
                continue
            if rule.methods is not None and method not in rule.methods:
                have_match_for.update(rule.methods)
                continue
            if self.map.redirect_defaults:
                for r in self.map._rules_by_endpoint[rule.endpoint]:
                    if r.provides_defaults_for(rule) and r.suitable_for(rv, method):
                        rv.update(r.defaults)
                        subdomain, path = r.build(rv)
                        raise RequestRedirect(str('%s://%s%s%s/%s' % (self.url_scheme,
                         subdomain and subdomain + '.' or '',
                         self.server_name,
                         self.script_name[:-1],
                         url_quote(path.lstrip('/'), self.map.charset))))

            if rule.redirect_to is not None:
                if isinstance(rule.redirect_to, basestring):

                    def _handle_match(match):
                        value = rv[match.group(1)]
                        return rule._converters[match.group(1)].to_url(value)

                    redirect_url = _simple_rule_re.sub(_handle_match, rule.redirect_to)
                else:
                    redirect_url = rule.redirect_to(self, **rv)
                raise RequestRedirect(str(urljoin('%s://%s%s%s' % (self.url_scheme,
                 self.subdomain and self.subdomain + '.' or '',
                 self.server_name,
                 self.script_name), redirect_url)))
            if return_rule:
                return (rule, rv)
            return (rule.endpoint, rv)

        if have_match_for:
            raise MethodNotAllowed(valid_methods=list(have_match_for))
        raise NotFound()

    def test(self, path_info = None, method = None):
        try:
            self.match(path_info, method)
        except RequestRedirect:
            pass
        except NotFound:
            return False

        return True

    def _partial_build(self, endpoint, values, method, append_unknown):
        if method is None:
            rv = self._partial_build(endpoint, values, self.default_method, append_unknown)
            if rv is not None:
                return rv
        for rule in self.map._rules_by_endpoint.get(endpoint, ()):
            if rule.suitable_for(values, method):
                rv = rule.build(values, append_unknown)
                if rv is not None:
                    return rv

    def build(self, endpoint, values = None, method = None, force_external = False, append_unknown = True):
        self.map.update()
        if values:
            if isinstance(values, MultiDict):
                values = dict(((k, v) for k, v in values.iteritems(multi=True) if v is not None))
            else:
                values = dict(((k, v) for k, v in values.iteritems() if v is not None))
        else:
            values = {}
        rv = self._partial_build(endpoint, values, method, append_unknown)
        if rv is None:
            raise BuildError(endpoint, values, method)
        subdomain, path = rv
        if not force_external and subdomain == self.subdomain:
            return str(urljoin(self.script_name, path.lstrip('/')))
        return str('%s://%s%s%s/%s' % (self.url_scheme,
         subdomain and subdomain + '.' or '',
         self.server_name,
         self.script_name[:-1],
         path.lstrip('/')))


DEFAULT_CONVERTERS = {'default': UnicodeConverter,
 'string': UnicodeConverter,
 'any': AnyConverter,
 'path': PathConverter,
 'int': IntegerConverter,
 'float': FloatConverter}
from werkzeug.datastructures import ImmutableDict, MultiDict
Map.default_converters = ImmutableDict(DEFAULT_CONVERTERS)