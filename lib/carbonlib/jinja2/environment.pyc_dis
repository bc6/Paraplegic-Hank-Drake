#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\environment.py
import os
import sys
from jinja2 import nodes
from jinja2.defaults import *
from jinja2.lexer import get_lexer, TokenStream
from jinja2.parser import Parser
from jinja2.optimizer import optimize
from jinja2.compiler import generate
from jinja2.runtime import Undefined, new_context
from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound, TemplatesNotFound
from jinja2.utils import import_string, LRUCache, Markup, missing, concat, consume, internalcode, _encode_filename
_spontaneous_environments = LRUCache(10)
_make_traceback = None

def get_spontaneous_environment(*args):
    try:
        env = _spontaneous_environments.get(args)
    except TypeError:
        return Environment(*args)

    if env is not None:
        return env
    _spontaneous_environments[args] = env = Environment(*args)
    env.shared = True
    return env


def create_cache(size):
    if size == 0:
        return None
    if size < 0:
        return {}
    return LRUCache(size)


def copy_cache(cache):
    if cache is None:
        return
    if type(cache) is dict:
        return {}
    return LRUCache(cache.capacity)


def load_extensions(environment, extensions):
    result = {}
    for extension in extensions:
        if isinstance(extension, basestring):
            extension = import_string(extension)
        result[extension.identifier] = extension(environment)

    return result


def _environment_sanity_check(environment):
    return environment


class Environment(object):
    sandboxed = False
    overlayed = False
    linked_to = None
    shared = False
    exception_handler = None
    exception_formatter = None

    def __init__(self, block_start_string = BLOCK_START_STRING, block_end_string = BLOCK_END_STRING, variable_start_string = VARIABLE_START_STRING, variable_end_string = VARIABLE_END_STRING, comment_start_string = COMMENT_START_STRING, comment_end_string = COMMENT_END_STRING, line_statement_prefix = LINE_STATEMENT_PREFIX, line_comment_prefix = LINE_COMMENT_PREFIX, trim_blocks = TRIM_BLOCKS, newline_sequence = NEWLINE_SEQUENCE, extensions = (), optimized = True, undefined = Undefined, finalize = None, autoescape = False, loader = None, cache_size = 50, auto_reload = True, bytecode_cache = None):
        self.block_start_string = block_start_string
        self.block_end_string = block_end_string
        self.variable_start_string = variable_start_string
        self.variable_end_string = variable_end_string
        self.comment_start_string = comment_start_string
        self.comment_end_string = comment_end_string
        self.line_statement_prefix = line_statement_prefix
        self.line_comment_prefix = line_comment_prefix
        self.trim_blocks = trim_blocks
        self.newline_sequence = newline_sequence
        self.undefined = undefined
        self.optimized = optimized
        self.finalize = finalize
        self.autoescape = autoescape
        self.filters = DEFAULT_FILTERS.copy()
        self.tests = DEFAULT_TESTS.copy()
        self.globals = DEFAULT_NAMESPACE.copy()
        self.loader = loader
        self.bytecode_cache = None
        self.cache = create_cache(cache_size)
        self.bytecode_cache = bytecode_cache
        self.auto_reload = auto_reload
        self.extensions = load_extensions(self, extensions)
        _environment_sanity_check(self)

    def add_extension(self, extension):
        self.extensions.update(load_extensions(self, [extension]))

    def extend(self, **attributes):
        for key, value in attributes.iteritems():
            if not hasattr(self, key):
                setattr(self, key, value)

    def overlay(self, block_start_string = missing, block_end_string = missing, variable_start_string = missing, variable_end_string = missing, comment_start_string = missing, comment_end_string = missing, line_statement_prefix = missing, line_comment_prefix = missing, trim_blocks = missing, extensions = missing, optimized = missing, undefined = missing, finalize = missing, autoescape = missing, loader = missing, cache_size = missing, auto_reload = missing, bytecode_cache = missing):
        args = dict(locals())
        del args['self']
        del args['cache_size']
        del args['extensions']
        rv = object.__new__(self.__class__)
        rv.__dict__.update(self.__dict__)
        rv.overlayed = True
        rv.linked_to = self
        for key, value in args.iteritems():
            if value is not missing:
                setattr(rv, key, value)

        if cache_size is not missing:
            rv.cache = create_cache(cache_size)
        else:
            rv.cache = copy_cache(self.cache)
        rv.extensions = {}
        for key, value in self.extensions.iteritems():
            rv.extensions[key] = value.bind(rv)

        if extensions is not missing:
            rv.extensions.update(load_extensions(rv, extensions))
        return _environment_sanity_check(rv)

    lexer = property(get_lexer, doc='The lexer for this environment.')

    def iter_extensions(self):
        return iter(sorted(self.extensions.values(), key=lambda x: x.priority))

    def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (TypeError, LookupError):
            if isinstance(argument, basestring):
                try:
                    attr = str(argument)
                except Exception:
                    pass
                else:
                    try:
                        return getattr(obj, attr)
                    except AttributeError:
                        pass

            return self.undefined(obj=obj, name=argument)

    def getattr(self, obj, attribute):
        try:
            return getattr(obj, attribute)
        except AttributeError:
            pass

        try:
            return obj[attribute]
        except (TypeError, LookupError, AttributeError):
            return self.undefined(obj=obj, name=attribute)

    @internalcode
    def parse(self, source, name = None, filename = None):
        try:
            return self._parse(source, name, filename)
        except TemplateSyntaxError:
            exc_info = sys.exc_info()

        self.handle_exception(exc_info, source_hint=source)

    def _parse(self, source, name, filename):
        return Parser(self, source, name, _encode_filename(filename)).parse()

    def lex(self, source, name = None, filename = None):
        source = unicode(source)
        try:
            return self.lexer.tokeniter(source, name, filename)
        except TemplateSyntaxError:
            exc_info = sys.exc_info()

        self.handle_exception(exc_info, source_hint=source)

    def preprocess(self, source, name = None, filename = None):
        return reduce(lambda s, e: e.preprocess(s, name, filename), self.iter_extensions(), unicode(source))

    def _tokenize(self, source, name, filename = None, state = None):
        source = self.preprocess(source, name, filename)
        stream = self.lexer.tokenize(source, name, filename, state)
        for ext in self.iter_extensions():
            stream = ext.filter_stream(stream)
            if not isinstance(stream, TokenStream):
                stream = TokenStream(stream, name, filename)

        return stream

    def _generate(self, source, name, filename, defer_init = False):
        return generate(source, self, name, filename, defer_init=defer_init)

    def _compile(self, source, filename):
        return compile(source, filename, 'exec')

    @internalcode
    def compile(self, source, name = None, filename = None, raw = False, defer_init = False):
        source_hint = None
        try:
            if isinstance(source, basestring):
                source_hint = source
                source = self._parse(source, name, filename)
            if self.optimized:
                source = optimize(source, self)
            source = self._generate(source, name, filename, defer_init=defer_init)
            if raw:
                return source
            if filename is None:
                filename = '<template>'
            else:
                filename = _encode_filename(filename)
            return self._compile(source, filename)
        except TemplateSyntaxError:
            exc_info = sys.exc_info()

        self.handle_exception(exc_info, source_hint=source)

    def compile_expression(self, source, undefined_to_none = True):
        parser = Parser(self, source, state='variable')
        exc_info = None
        try:
            expr = parser.parse_expression()
            if not parser.stream.eos:
                raise TemplateSyntaxError('chunk after expression', parser.stream.current.lineno, None, None)
            expr.set_environment(self)
        except TemplateSyntaxError:
            exc_info = sys.exc_info()

        if exc_info is not None:
            self.handle_exception(exc_info, source_hint=source)
        body = [nodes.Assign(nodes.Name('result', 'store'), expr, lineno=1)]
        template = self.from_string(nodes.Template(body, lineno=1))
        return TemplateExpression(template, undefined_to_none)

    def compile_templates(self, target, extensions = None, filter_func = None, zip = 'deflated', log_function = None, ignore_errors = True, py_compile = False):
        from jinja2.loaders import ModuleLoader
        if log_function is None:
            log_function = lambda x: None
        if py_compile:
            import imp, marshal
            py_header = imp.get_magic() + u'\xff\xff\xff\xff'.encode('iso-8859-15')

        def write_file(filename, data, mode):
            if zip:
                info = ZipInfo(filename)
                info.external_attr = 32309248L
                zip_file.writestr(info, data)
            else:
                f = open(os.path.join(target, filename), mode)
                try:
                    f.write(data)
                finally:
                    f.close()

        if zip is not None:
            from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, ZIP_STORED
            zip_file = ZipFile(target, 'w', dict(deflated=ZIP_DEFLATED, stored=ZIP_STORED)[zip])
            log_function('Compiling into Zip archive "%s"' % target)
        else:
            if not os.path.isdir(target):
                os.makedirs(target)
            log_function('Compiling into folder "%s"' % target)
        try:
            for name in self.list_templates(extensions, filter_func):
                source, filename, _ = self.loader.get_source(self, name)
                try:
                    code = self.compile(source, name, filename, True, True)
                except TemplateSyntaxError as e:
                    if not ignore_errors:
                        raise 
                    log_function('Could not compile "%s": %s' % (name, e))
                    continue

                filename = ModuleLoader.get_module_filename(name)
                if py_compile:
                    c = self._compile(code, _encode_filename(filename))
                    write_file(filename + 'c', py_header + marshal.dumps(c), 'wb')
                    log_function('Byte-compiled "%s" as %s' % (name, filename + 'c'))
                else:
                    write_file(filename, code, 'w')
                    log_function('Compiled "%s" as %s' % (name, filename))

        finally:
            if zip:
                zip_file.close()

        log_function('Finished compiling templates')

    def list_templates(self, extensions = None, filter_func = None):
        x = self.loader.list_templates()
        if extensions is not None:
            if filter_func is not None:
                raise TypeError('either extensions or filter_func can be passed, but not both')
            filter_func = lambda x: '.' in x and x.rsplit('.', 1)[1] in extensions
        if filter_func is not None:
            x = filter(filter_func, x)
        return x

    def handle_exception(self, exc_info = None, rendered = False, source_hint = None):
        global _make_traceback
        if exc_info is None:
            exc_info = sys.exc_info()
        if _make_traceback is None:
            from jinja2.debug import make_traceback as _make_traceback
        traceback = _make_traceback(exc_info, source_hint)
        if rendered and self.exception_formatter is not None:
            return self.exception_formatter(traceback)
        if self.exception_handler is not None:
            self.exception_handler(traceback)
        exc_type, exc_value, tb = traceback.standard_exc_info
        raise exc_type, exc_value, tb

    def join_path(self, template, parent):
        return template

    @internalcode
    def _load_template(self, name, globals):
        if self.loader is None:
            raise TypeError('no loader for this environment specified')
        if self.cache is not None:
            template = self.cache.get(name)
            if template is not None and (not self.auto_reload or template.is_up_to_date):
                return template
        template = self.loader.load(self, name, globals)
        if self.cache is not None:
            self.cache[name] = template
        return template

    @internalcode
    def get_template(self, name, parent = None, globals = None):
        if isinstance(name, Template):
            return name
        if parent is not None:
            name = self.join_path(name, parent)
        return self._load_template(name, self.make_globals(globals))

    @internalcode
    def select_template(self, names, parent = None, globals = None):
        if not names:
            raise TemplatesNotFound(message=u'Tried to select from an empty list of templates.')
        globals = self.make_globals(globals)
        for name in names:
            if isinstance(name, Template):
                return name
            if parent is not None:
                name = self.join_path(name, parent)
            try:
                return self._load_template(name, globals)
            except TemplateNotFound:
                pass

        raise TemplatesNotFound(names)

    @internalcode
    def get_or_select_template(self, template_name_or_list, parent = None, globals = None):
        if isinstance(template_name_or_list, basestring):
            return self.get_template(template_name_or_list, parent, globals)
        if isinstance(template_name_or_list, Template):
            return template_name_or_list
        return self.select_template(template_name_or_list, parent, globals)

    def from_string(self, source, globals = None, template_class = None):
        globals = self.make_globals(globals)
        cls = template_class or self.template_class
        return cls.from_code(self, self.compile(source), globals, None)

    def make_globals(self, d):
        if not d:
            return self.globals
        return dict(self.globals, **d)


class Template(object):

    def __new__(cls, source, block_start_string = BLOCK_START_STRING, block_end_string = BLOCK_END_STRING, variable_start_string = VARIABLE_START_STRING, variable_end_string = VARIABLE_END_STRING, comment_start_string = COMMENT_START_STRING, comment_end_string = COMMENT_END_STRING, line_statement_prefix = LINE_STATEMENT_PREFIX, line_comment_prefix = LINE_COMMENT_PREFIX, trim_blocks = TRIM_BLOCKS, newline_sequence = NEWLINE_SEQUENCE, extensions = (), optimized = True, undefined = Undefined, finalize = None, autoescape = False):
        env = get_spontaneous_environment(block_start_string, block_end_string, variable_start_string, variable_end_string, comment_start_string, comment_end_string, line_statement_prefix, line_comment_prefix, trim_blocks, newline_sequence, frozenset(extensions), optimized, undefined, finalize, autoescape, None, 0, False, None)
        return env.from_string(source, template_class=cls)

    @classmethod
    def from_code(cls, environment, code, globals, uptodate = None):
        namespace = {'environment': environment,
         '__file__': code.co_filename}
        exec code in namespace
        rv = cls._from_namespace(environment, namespace, globals)
        rv._uptodate = uptodate
        return rv

    @classmethod
    def from_module_dict(cls, environment, module_dict, globals):
        return cls._from_namespace(environment, module_dict, globals)

    @classmethod
    def _from_namespace(cls, environment, namespace, globals):
        t = object.__new__(cls)
        t.environment = environment
        t.globals = globals
        t.name = namespace['name']
        t.filename = namespace['__file__']
        t.blocks = namespace['blocks']
        t.root_render_func = namespace['root']
        t._module = None
        t._debug_info = namespace['debug_info']
        t._uptodate = None
        namespace['environment'] = environment
        namespace['__jinja_template__'] = t
        return t

    def render(self, *args, **kwargs):
        vars = dict(*args, **kwargs)
        try:
            return concat(self.root_render_func(self.new_context(vars)))
        except Exception:
            exc_info = sys.exc_info()

        return self.environment.handle_exception(exc_info, True)

    def stream(self, *args, **kwargs):
        return TemplateStream(self.generate(*args, **kwargs))

    def generate(self, *args, **kwargs):
        vars = dict(*args, **kwargs)
        try:
            for event in self.root_render_func(self.new_context(vars)):
                yield event

        except Exception:
            exc_info = sys.exc_info()
        else:
            return

        yield self.environment.handle_exception(exc_info, True)

    def new_context(self, vars = None, shared = False, locals = None):
        return new_context(self.environment, self.name, self.blocks, vars, shared, self.globals, locals)

    def make_module(self, vars = None, shared = False, locals = None):
        return TemplateModule(self, self.new_context(vars, shared, locals))

    @property
    def module(self):
        if self._module is not None:
            return self._module
        self._module = rv = self.make_module()
        return rv

    def get_corresponding_lineno(self, lineno):
        for template_line, code_line in reversed(self.debug_info):
            if code_line <= lineno:
                return template_line

        return 1

    @property
    def is_up_to_date(self):
        if self._uptodate is None:
            return True
        return self._uptodate()

    @property
    def debug_info(self):
        return [ tuple(map(int, x.split('='))) for x in self._debug_info.split('&') ]

    def __repr__(self):
        if self.name is None:
            name = 'memory:%x' % id(self)
        else:
            name = repr(self.name)
        return '<%s %s>' % (self.__class__.__name__, name)


class TemplateModule(object):

    def __init__(self, template, context):
        self._body_stream = list(template.root_render_func(context))
        self.__dict__.update(context.get_exported())
        self.__name__ = template.name

    def __html__(self):
        return Markup(concat(self._body_stream))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return concat(self._body_stream)

    def __repr__(self):
        if self.__name__ is None:
            name = 'memory:%x' % id(self)
        else:
            name = repr(self.__name__)
        return '<%s %s>' % (self.__class__.__name__, name)


class TemplateExpression(object):

    def __init__(self, template, undefined_to_none):
        self._template = template
        self._undefined_to_none = undefined_to_none

    def __call__(self, *args, **kwargs):
        context = self._template.new_context(dict(*args, **kwargs))
        consume(self._template.root_render_func(context))
        rv = context.vars['result']
        if self._undefined_to_none and isinstance(rv, Undefined):
            rv = None
        return rv


class TemplateStream(object):

    def __init__(self, gen):
        self._gen = gen
        self.disable_buffering()

    def dump(self, fp, encoding = None, errors = 'strict'):
        close = False
        if isinstance(fp, basestring):
            fp = file(fp, 'w')
            close = True
        try:
            if encoding is not None:
                iterable = (x.encode(encoding, errors) for x in self)
            else:
                iterable = self
            if hasattr(fp, 'writelines'):
                fp.writelines(iterable)
            else:
                for item in iterable:
                    fp.write(item)

        finally:
            if close:
                fp.close()

    def disable_buffering(self):
        self._next = self._gen.next
        self.buffered = False

    def enable_buffering(self, size = 5):
        if size <= 1:
            raise ValueError('buffer size too small')

        def generator(next):
            buf = []
            c_size = 0
            push = buf.append
            while 1:
                try:
                    while c_size < size:
                        c = next()
                        push(c)
                        if c:
                            c_size += 1

                except StopIteration:
                    if not c_size:
                        return

                yield concat(buf)
                del buf[:]
                c_size = 0

        self.buffered = True
        self._next = generator(self._gen.next).next

    def __iter__(self):
        return self

    def next(self):
        return self._next()


Environment.template_class = Template