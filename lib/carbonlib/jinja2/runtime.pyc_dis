#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\runtime.py
from itertools import chain, imap
from jinja2.nodes import EvalContext, _context_function_types
from jinja2.utils import Markup, partial, soft_unicode, escape, missing, concat, internalcode, next, object_type_repr
from jinja2.exceptions import UndefinedError, TemplateRuntimeError, TemplateNotFound
__all__ = ['LoopContext',
 'TemplateReference',
 'Macro',
 'Markup',
 'TemplateRuntimeError',
 'missing',
 'concat',
 'escape',
 'markup_join',
 'unicode_join',
 'to_string',
 'identity',
 'TemplateNotFound']
to_string = unicode
identity = lambda x: x
_last_iteration = object()

def markup_join(seq):
    buf = []
    iterator = imap(soft_unicode, seq)
    for arg in iterator:
        buf.append(arg)
        if hasattr(arg, '__html__'):
            return Markup(u'').join(chain(buf, iterator))

    return concat(buf)


def unicode_join(seq):
    return concat(imap(unicode, seq))


def new_context(environment, template_name, blocks, vars = None, shared = None, globals = None, locals = None):
    if vars is None:
        vars = {}
    if shared:
        parent = vars
    else:
        parent = dict((globals or ()), **vars)
    if locals:
        if shared:
            parent = dict(parent)
        for key, value in locals.iteritems():
            if key[:2] == 'l_' and value is not missing:
                parent[key[2:]] = value

    return Context(environment, parent, template_name, blocks)


class TemplateReference(object):

    def __init__(self, context):
        self.__context = context

    def __getitem__(self, name):
        blocks = self.__context.blocks[name]
        return BlockReference(name, self.__context, blocks, 0)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__context.name)


class Context(object):
    __slots__ = ('parent', 'vars', 'environment', 'eval_ctx', 'exported_vars', 'name', 'blocks', '__weakref__')

    def __init__(self, environment, parent, name, blocks):
        self.parent = parent
        self.vars = {}
        self.environment = environment
        self.eval_ctx = EvalContext(self.environment, name)
        self.exported_vars = set()
        self.name = name
        self.blocks = dict(((k, [v]) for k, v in blocks.iteritems()))

    def super(self, name, current):
        try:
            blocks = self.blocks[name]
            index = blocks.index(current) + 1
            blocks[index]
        except LookupError:
            return self.environment.undefined('there is no parent block called %r.' % name, name='super')

        return BlockReference(name, self, blocks, index)

    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default

    def resolve(self, key):
        if key in self.vars:
            return self.vars[key]
        if key in self.parent:
            return self.parent[key]
        return self.environment.undefined(name=key)

    def get_exported(self):
        return dict(((k, self.vars[k]) for k in self.exported_vars))

    def get_all(self):
        return dict(self.parent, **self.vars)

    @internalcode
    def call(_Context__self, _Context__obj, *args, **kwargs):
        if isinstance(__obj, _context_function_types):
            if getattr(__obj, 'contextfunction', 0):
                args = (__self,) + args
            elif getattr(__obj, 'evalcontextfunction', 0):
                args = (__self.eval_ctx,) + args
            elif getattr(__obj, 'environmentfunction', 0):
                args = (__self.environment,) + args
        try:
            return __obj(*args, **kwargs)
        except StopIteration:
            return __self.environment.undefined('value was undefined because a callable raised a StopIteration exception')

    def derived(self, locals = None):
        context = new_context(self.environment, self.name, {}, self.parent, True, None, locals)
        context.vars.update(self.vars)
        context.eval_ctx = self.eval_ctx
        context.blocks.update(((k, list(v)) for k, v in self.blocks.iteritems()))
        return context

    def _all(meth):
        proxy = lambda self: getattr(self.get_all(), meth)()
        proxy.__doc__ = getattr(dict, meth).__doc__
        proxy.__name__ = meth
        return proxy

    keys = _all('keys')
    values = _all('values')
    items = _all('items')
    if hasattr(dict, 'iterkeys'):
        iterkeys = _all('iterkeys')
        itervalues = _all('itervalues')
        iteritems = _all('iteritems')
    del _all

    def __contains__(self, name):
        return name in self.vars or name in self.parent

    def __getitem__(self, key):
        item = self.resolve(key)
        if isinstance(item, Undefined):
            raise KeyError(key)
        return item

    def __repr__(self):
        return '<%s %s of %r>' % (self.__class__.__name__, repr(self.get_all()), self.name)


try:
    from collections import Mapping
    Mapping.register(Context)
except ImportError:
    pass

class BlockReference(object):

    def __init__(self, name, context, stack, depth):
        self.name = name
        self._context = context
        self._stack = stack
        self._depth = depth

    @property
    def super(self):
        if self._depth + 1 >= len(self._stack):
            return self._context.environment.undefined('there is no parent block called %r.' % self.name, name='super')
        return BlockReference(self.name, self._context, self._stack, self._depth + 1)

    @internalcode
    def __call__(self):
        rv = concat(self._stack[self._depth](self._context))
        if self._context.eval_ctx.autoescape:
            rv = Markup(rv)
        return rv


class LoopContext(object):

    def __init__(self, iterable, recurse = None):
        self._iterator = iter(iterable)
        self._recurse = recurse
        self._after = self._safe_next()
        self.index0 = -1
        try:
            self._length = len(iterable)
        except (TypeError, AttributeError):
            self._length = None

    def cycle(self, *args):
        if not args:
            raise TypeError('no items for cycling given')
        return args[self.index0 % len(args)]

    first = property(lambda x: x.index0 == 0)
    last = property(lambda x: x._after is _last_iteration)
    index = property(lambda x: x.index0 + 1)
    revindex = property(lambda x: x.length - x.index0)
    revindex0 = property(lambda x: x.length - x.index)

    def __len__(self):
        return self.length

    def __iter__(self):
        return LoopContextIterator(self)

    def _safe_next(self):
        try:
            return next(self._iterator)
        except StopIteration:
            return _last_iteration

    @internalcode
    def loop(self, iterable):
        if self._recurse is None:
            raise TypeError("Tried to call non recursive loop.  Maybe you forgot the 'recursive' modifier.")
        return self._recurse(iterable, self._recurse)

    __call__ = loop
    del loop

    @property
    def length(self):
        if self._length is None:
            iterable = tuple(self._iterator)
            self._iterator = iter(iterable)
            self._length = len(iterable) + self.index0 + 1
        return self._length

    def __repr__(self):
        return '<%s %r/%r>' % (self.__class__.__name__, self.index, self.length)


class LoopContextIterator(object):
    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        return self

    def next(self):
        ctx = self.context
        ctx.index0 += 1
        if ctx._after is _last_iteration:
            raise StopIteration()
        next_elem = ctx._after
        ctx._after = ctx._safe_next()
        return (next_elem, ctx)


class Macro(object):

    def __init__(self, environment, func, name, arguments, defaults, catch_kwargs, catch_varargs, caller):
        self._environment = environment
        self._func = func
        self._argument_count = len(arguments)
        self.name = name
        self.arguments = arguments
        self.defaults = defaults
        self.catch_kwargs = catch_kwargs
        self.catch_varargs = catch_varargs
        self.caller = caller

    @internalcode
    def __call__(self, *args, **kwargs):
        arguments = list(args[:self._argument_count])
        off = len(arguments)
        if off != self._argument_count:
            for idx, name in enumerate(self.arguments[len(arguments):]):
                try:
                    value = kwargs.pop(name)
                except KeyError:
                    try:
                        value = self.defaults[idx - self._argument_count + off]
                    except IndexError:
                        value = self._environment.undefined('parameter %r was not provided' % name, name=name)

                arguments.append(value)

        if self.caller:
            caller = kwargs.pop('caller', None)
            if caller is None:
                caller = self._environment.undefined('No caller defined', name='caller')
            arguments.append(caller)
        if self.catch_kwargs:
            arguments.append(kwargs)
        elif kwargs:
            raise TypeError('macro %r takes no keyword argument %r' % (self.name, next(iter(kwargs))))
        if self.catch_varargs:
            arguments.append(args[self._argument_count:])
        elif len(args) > self._argument_count:
            raise TypeError('macro %r takes not more than %d argument(s)' % (self.name, len(self.arguments)))
        return self._func(*arguments)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name is None and 'anonymous' or repr(self.name))


class Undefined(object):
    __slots__ = ('_undefined_hint', '_undefined_obj', '_undefined_name', '_undefined_exception')

    def __init__(self, hint = None, obj = missing, name = None, exc = UndefinedError):
        self._undefined_hint = hint
        self._undefined_obj = obj
        self._undefined_name = name
        self._undefined_exception = exc

    @internalcode
    def _fail_with_undefined_error(self, *args, **kwargs):
        if self._undefined_hint is None:
            if self._undefined_obj is missing:
                hint = '%r is undefined' % self._undefined_name
            elif not isinstance(self._undefined_name, basestring):
                hint = '%s has no element %r' % (object_type_repr(self._undefined_obj), self._undefined_name)
            else:
                hint = '%r has no attribute %r' % (object_type_repr(self._undefined_obj), self._undefined_name)
        else:
            hint = self._undefined_hint
        raise self._undefined_exception(hint)

    @internalcode
    def __getattr__(self, name):
        if name[:2] == '__':
            raise AttributeError(name)
        return self._fail_with_undefined_error()

    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = __float__ = __complex__ = __pow__ = __rpow__ = _fail_with_undefined_error

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u''

    def __len__(self):
        return 0

    def __iter__(self):
        pass

    def __nonzero__(self):
        return False

    def __repr__(self):
        return 'Undefined'


class DebugUndefined(Undefined):
    __slots__ = ()

    def __unicode__(self):
        if self._undefined_hint is None:
            if self._undefined_obj is missing:
                return u'{{ %s }}' % self._undefined_name
            return '{{ no such element: %s[%r] }}' % (object_type_repr(self._undefined_obj), self._undefined_name)
        return u'{{ undefined value printed: %s }}' % self._undefined_hint


class StrictUndefined(Undefined):
    __slots__ = ()
    __iter__ = __unicode__ = __str__ = __len__ = __nonzero__ = __eq__ = __ne__ = __bool__ = Undefined._fail_with_undefined_error


del Undefined.__slots__
del DebugUndefined.__slots__
del StrictUndefined.__slots__