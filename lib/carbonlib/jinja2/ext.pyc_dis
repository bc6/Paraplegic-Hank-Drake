#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\ext.py
from collections import deque
from jinja2 import nodes
from jinja2.defaults import *
from jinja2.environment import Environment
from jinja2.runtime import Undefined, concat
from jinja2.exceptions import TemplateAssertionError, TemplateSyntaxError
from jinja2.utils import contextfunction, import_string, Markup, next
GETTEXT_FUNCTIONS = ('_', 'gettext', 'ngettext')

class ExtensionRegistry(type):

    def __new__(cls, name, bases, d):
        rv = type.__new__(cls, name, bases, d)
        rv.identifier = rv.__module__ + '.' + rv.__name__
        return rv


class Extension(object):
    __metaclass__ = ExtensionRegistry
    tags = set()
    priority = 100

    def __init__(self, environment):
        self.environment = environment

    def bind(self, environment):
        rv = object.__new__(self.__class__)
        rv.__dict__.update(self.__dict__)
        rv.environment = environment
        return rv

    def preprocess(self, source, name, filename = None):
        return source

    def filter_stream(self, stream):
        return stream

    def parse(self, parser):
        raise NotImplementedError()

    def attr(self, name, lineno = None):
        return nodes.ExtensionAttribute(self.identifier, name, lineno=lineno)

    def call_method(self, name, args = None, kwargs = None, dyn_args = None, dyn_kwargs = None, lineno = None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = []
        return nodes.Call(self.attr(name, lineno=lineno), args, kwargs, dyn_args, dyn_kwargs, lineno=lineno)


@contextfunction
def _gettext_alias(__context, *args, **kwargs):
    return __context.call(__context.resolve('gettext'), *args, **kwargs)


def _make_new_gettext(func):

    @contextfunction
    def gettext(__context, __string, **variables):
        rv = __context.call(func, __string)
        if __context.eval_ctx.autoescape:
            rv = Markup(rv)
        return rv % variables

    return gettext


def _make_new_ngettext(func):

    @contextfunction
    def ngettext(__context, __singular, __plural, __num, **variables):
        variables.setdefault('num', __num)
        rv = __context.call(func, __singular, __plural, __num)
        if __context.eval_ctx.autoescape:
            rv = Markup(rv)
        return rv % variables

    return ngettext


class InternationalizationExtension(Extension):
    tags = set(['trans'])

    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.globals['_'] = _gettext_alias
        environment.extend(install_gettext_translations=self._install, install_null_translations=self._install_null, install_gettext_callables=self._install_callables, uninstall_gettext_translations=self._uninstall, extract_translations=self._extract, newstyle_gettext=False)

    def _install(self, translations, newstyle = None):
        gettext = getattr(translations, 'ugettext', None)
        if gettext is None:
            gettext = translations.gettext
        ngettext = getattr(translations, 'ungettext', None)
        if ngettext is None:
            ngettext = translations.ngettext
        self._install_callables(gettext, ngettext, newstyle)

    def _install_null(self, newstyle = None):
        self._install_callables(lambda x: x, lambda s, p, n: (n != 1 and (p,) or (s,))[0], newstyle)

    def _install_callables(self, gettext, ngettext, newstyle = None):
        if newstyle is not None:
            self.environment.newstyle_gettext = newstyle
        if self.environment.newstyle_gettext:
            gettext = _make_new_gettext(gettext)
            ngettext = _make_new_ngettext(ngettext)
        self.environment.globals.update(gettext=gettext, ngettext=ngettext)

    def _uninstall(self, translations):
        for key in ('gettext', 'ngettext'):
            self.environment.globals.pop(key, None)

    def _extract(self, source, gettext_functions = GETTEXT_FUNCTIONS):
        if isinstance(source, basestring):
            source = self.environment.parse(source)
        return extract_from_ast(source, gettext_functions)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        num_called_num = False
        plural_expr = None
        variables = {}
        while parser.stream.current.type != 'block_end':
            if variables:
                parser.stream.expect('comma')
            if parser.stream.skip_if('colon'):
                break
            name = parser.stream.expect('name')
            if name.value in variables:
                parser.fail('translatable variable %r defined twice.' % name.value, name.lineno, exc=TemplateAssertionError)
            if parser.stream.current.type == 'assign':
                next(parser.stream)
                variables[name.value] = var = parser.parse_expression()
            else:
                variables[name.value] = var = nodes.Name(name.value, 'load')
            if plural_expr is None:
                plural_expr = var
                num_called_num = name.value == 'num'

        parser.stream.expect('block_end')
        plural = plural_names = None
        have_plural = False
        referenced = set()
        singular_names, singular = self._parse_block(parser, True)
        if singular_names:
            referenced.update(singular_names)
            if plural_expr is None:
                plural_expr = nodes.Name(singular_names[0], 'load')
                num_called_num = singular_names[0] == 'num'
        if parser.stream.current.test('name:pluralize'):
            have_plural = True
            next(parser.stream)
            if parser.stream.current.type != 'block_end':
                name = parser.stream.expect('name')
                if name.value not in variables:
                    parser.fail('unknown variable %r for pluralization' % name.value, name.lineno, exc=TemplateAssertionError)
                plural_expr = variables[name.value]
                num_called_num = name.value == 'num'
            parser.stream.expect('block_end')
            plural_names, plural = self._parse_block(parser, False)
            next(parser.stream)
            referenced.update(plural_names)
        else:
            next(parser.stream)
        for var in referenced:
            if var not in variables:
                variables[var] = nodes.Name(var, 'load')

        if not have_plural:
            plural_expr = None
        elif plural_expr is None:
            parser.fail('pluralize without variables', lineno)
        node = self._make_node(singular, plural, variables, plural_expr, bool(referenced), num_called_num and have_plural)
        node.set_lineno(lineno)
        return node

    def _parse_block(self, parser, allow_pluralize):
        referenced = []
        buf = []
        while 1:
            if parser.stream.current.type == 'data':
                buf.append(parser.stream.current.value.replace('%', '%%'))
                next(parser.stream)
            elif parser.stream.current.type == 'variable_begin':
                next(parser.stream)
                name = parser.stream.expect('name').value
                referenced.append(name)
                buf.append('%%(%s)s' % name)
                parser.stream.expect('variable_end')
            elif parser.stream.current.type == 'block_begin':
                next(parser.stream)
                if parser.stream.current.test('name:endtrans'):
                    break
                elif parser.stream.current.test('name:pluralize'):
                    if allow_pluralize:
                        break
                    parser.fail('a translatable section can have only one pluralize section')
                parser.fail('control structures in translatable sections are not allowed')
            elif parser.stream.eos:
                parser.fail('unclosed translation block')

        return (referenced, concat(buf))

    def _make_node(self, singular, plural, variables, plural_expr, vars_referenced, num_called_num):
        if not vars_referenced and not self.environment.newstyle_gettext:
            singular = singular.replace('%%', '%')
            if plural:
                plural = plural.replace('%%', '%')
        if plural_expr is None:
            gettext = nodes.Name('gettext', 'load')
            node = nodes.Call(gettext, [nodes.Const(singular)], [], None, None)
        else:
            ngettext = nodes.Name('ngettext', 'load')
            node = nodes.Call(ngettext, [nodes.Const(singular), nodes.Const(plural), plural_expr], [], None, None)
        if self.environment.newstyle_gettext:
            for key, value in variables.iteritems():
                if num_called_num and key == 'num':
                    continue
                node.kwargs.append(nodes.Keyword(key, value))

        else:
            node = nodes.MarkSafeIfAutoescape(node)
            if variables:
                node = nodes.Mod(node, nodes.Dict([ nodes.Pair(nodes.Const(key), value) for key, value in variables.items() ]))
        return nodes.Output([node])


class ExprStmtExtension(Extension):
    tags = set(['do'])

    def parse(self, parser):
        node = nodes.ExprStmt(lineno=next(parser.stream).lineno)
        node.node = parser.parse_tuple()
        return node


class LoopControlExtension(Extension):
    tags = set(['break', 'continue'])

    def parse(self, parser):
        token = next(parser.stream)
        if token.value == 'break':
            return nodes.Break(lineno=token.lineno)
        return nodes.Continue(lineno=token.lineno)


class WithExtension(Extension):
    tags = set(['with'])

    def parse(self, parser):
        node = nodes.Scope(lineno=next(parser.stream).lineno)
        assignments = []
        while parser.stream.current.type != 'block_end':
            lineno = parser.stream.current.lineno
            if assignments:
                parser.stream.expect('comma')
            target = parser.parse_assign_target()
            parser.stream.expect('assign')
            expr = parser.parse_expression()
            assignments.append(nodes.Assign(target, expr, lineno=lineno))

        node.body = assignments + list(parser.parse_statements(('name:endwith',), drop_needle=True))
        return node


class AutoEscapeExtension(Extension):
    tags = set(['autoescape'])

    def parse(self, parser):
        node = nodes.ScopedEvalContextModifier(lineno=next(parser.stream).lineno)
        node.options = [nodes.Keyword('autoescape', parser.parse_expression())]
        node.body = parser.parse_statements(('name:endautoescape',), drop_needle=True)
        return nodes.Scope([node])


def extract_from_ast(node, gettext_functions = GETTEXT_FUNCTIONS, babel_style = True):
    for node in node.find_all(nodes.Call):
        if not isinstance(node.node, nodes.Name) or node.node.name not in gettext_functions:
            continue
        strings = []
        for arg in node.args:
            if isinstance(arg, nodes.Const) and isinstance(arg.value, basestring):
                strings.append(arg.value)
            else:
                strings.append(None)

        for arg in node.kwargs:
            strings.append(None)

        if node.dyn_args is not None:
            strings.append(None)
        if node.dyn_kwargs is not None:
            strings.append(None)
        if not babel_style:
            strings = tuple((x for x in strings if x is not None))
            if not strings:
                continue
        elif len(strings) == 1:
            strings = strings[0]
        else:
            strings = tuple(strings)
        yield (node.lineno, node.node.name, strings)


class _CommentFinder(object):

    def __init__(self, tokens, comment_tags):
        self.tokens = tokens
        self.comment_tags = comment_tags
        self.offset = 0
        self.last_lineno = 0

    def find_backwards(self, offset):
        try:
            for _, token_type, token_value in reversed(self.tokens[self.offset:offset]):
                if token_type in ('comment', 'linecomment'):
                    try:
                        prefix, comment = token_value.split(None, 1)
                    except ValueError:
                        continue

                    if prefix in self.comment_tags:
                        return [comment.rstrip()]

            return []
        finally:
            self.offset = offset

    def find_comments(self, lineno):
        if not self.comment_tags or self.last_lineno > lineno:
            return []
        for idx, (token_lineno, _, _) in enumerate(self.tokens[self.offset:]):
            if token_lineno > lineno:
                return self.find_backwards(self.offset + idx)

        return self.find_backwards(len(self.tokens))


def babel_extract(fileobj, keywords, comment_tags, options):
    extensions = set()
    for extension in options.get('extensions', '').split(','):
        extension = extension.strip()
        if not extension:
            continue
        extensions.add(import_string(extension))

    if InternationalizationExtension not in extensions:
        extensions.add(InternationalizationExtension)

    def getbool(options, key, default = False):
        return options.get(key, str(default)).lower() in ('1', 'on', 'yes', 'true')

    silent = getbool(options, 'silent', True)
    environment = Environment(options.get('block_start_string', BLOCK_START_STRING), options.get('block_end_string', BLOCK_END_STRING), options.get('variable_start_string', VARIABLE_START_STRING), options.get('variable_end_string', VARIABLE_END_STRING), options.get('comment_start_string', COMMENT_START_STRING), options.get('comment_end_string', COMMENT_END_STRING), options.get('line_statement_prefix') or LINE_STATEMENT_PREFIX, options.get('line_comment_prefix') or LINE_COMMENT_PREFIX, getbool(options, 'trim_blocks', TRIM_BLOCKS), NEWLINE_SEQUENCE, frozenset(extensions), cache_size=0, auto_reload=False)
    if getbool(options, 'newstyle_gettext'):
        environment.newstyle_gettext = True
    source = fileobj.read().decode(options.get('encoding', 'utf-8'))
    try:
        node = environment.parse(source)
        tokens = list(environment.lex(environment.preprocess(source)))
    except TemplateSyntaxError as e:
        if not silent:
            raise 
        return

    finder = _CommentFinder(tokens, comment_tags)
    for lineno, func, message in extract_from_ast(node, keywords):
        yield (lineno,
         func,
         message,
         finder.find_comments(lineno))


i18n = InternationalizationExtension
do = ExprStmtExtension
loopcontrols = LoopControlExtension
with_ = WithExtension
autoescape = AutoEscapeExtension