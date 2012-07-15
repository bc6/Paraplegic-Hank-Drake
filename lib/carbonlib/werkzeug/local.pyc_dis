#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\local.py
try:
    from greenlet import getcurrent as get_current_greenlet
except ImportError:
    try:
        from py.magic import greenlet
        get_current_greenlet = greenlet.getcurrent
        del greenlet
    except:
        get_current_greenlet = int

try:
    from thread import get_ident as get_current_thread, allocate_lock
except ImportError:
    from dummy_thread import get_ident as get_current_thread, allocate_lock

from werkzeug.wsgi import ClosingIterator
from werkzeug._internal import _patch_wrapper
if get_current_greenlet is int:
    get_ident = get_current_thread
else:
    get_ident = lambda : (get_current_thread(), get_current_greenlet())

def release_local(local):
    local.__release_local__()


class Local(object):
    __slots__ = ('__storage__', '__lock__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__lock__', allocate_lock())

    def __iter__(self):
        return self.__storage__.iteritems()

    def __call__(self, proxy):
        return LocalProxy(self, proxy)

    def __release_local__(self):
        self.__storage__.pop(get_ident(), None)

    def __getattr__(self, name):
        self.__lock__.acquire()
        try:
            return self.__storage__[get_ident()][name]
        except KeyError:
            raise AttributeError(name)
        finally:
            self.__lock__.release()

    def __setattr__(self, name, value):
        self.__lock__.acquire()
        try:
            ident = get_ident()
            storage = self.__storage__
            if ident in storage:
                storage[ident][name] = value
            else:
                storage[ident] = {name: value}
        finally:
            self.__lock__.release()

    def __delattr__(self, name):
        self.__lock__.acquire()
        try:
            del self.__storage__[get_ident()][name]
        except KeyError:
            raise AttributeError(name)
        finally:
            self.__lock__.release()


class LocalStack(object):

    def __init__(self):
        self._local = Local()
        self._lock = allocate_lock()

    def __release_local__(self):
        self._local.__release_local__()

    def __call__(self):

        def _lookup():
            rv = self.top
            if rv is None:
                raise RuntimeError('object unbound')
            return rv

        return LocalProxy(_lookup)

    def push(self, obj):
        self._lock.acquire()
        try:
            rv = getattr(self._local, 'stack', None)
            if rv is None:
                self._local.stack = rv = []
            rv.append(obj)
            return rv
        finally:
            self._lock.release()

    def pop(self):
        self._lock.acquire()
        try:
            stack = getattr(self._local, 'stack', None)
            if stack is None:
                return
            if len(stack) == 1:
                release_local(self._local)
                return stack[-1]
            return stack.pop()
        finally:
            self._lock.release()

    @property
    def top(self):
        try:
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None


class LocalManager(object):

    def __init__(self, locals = None):
        if locals is None:
            self.locals = []
        elif isinstance(locals, Local):
            self.locals = [locals]
        else:
            self.locals = list(locals)

    def get_ident(self):
        return get_ident()

    def cleanup(self):
        ident = self.get_ident()
        for local in self.locals:
            release_local(local)

    def make_middleware(self, app):

        def application(environ, start_response):
            return ClosingIterator(app(environ, start_response), self.cleanup)

        return application

    def middleware(self, func):
        return _patch_wrapper(func, self.make_middleware(func))

    def __repr__(self):
        return '<%s storages: %d>' % (self.__class__.__name__, len(self.locals))


class LocalProxy(object):
    __slots__ = ('__local', '__dict__', '__name__')

    def __init__(self, local, name = None):
        object.__setattr__(self, '_LocalProxy__local', local)
        object.__setattr__(self, '__name__', name)

    def _get_current_object(self):
        if not hasattr(self.__local, '__release_local__'):
            return self.__local()
        try:
            return getattr(self.__local, self.__name__)
        except AttributeError:
            raise RuntimeError('no object bound to %s' % self.__name__)

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:
            return AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self._get_current_object()
        except RuntimeError:
            return '<%s unbound>' % self.__class__.__name__

        return repr(obj)

    def __nonzero__(self):
        try:
            return bool(self._get_current_object())
        except RuntimeError:
            return False

    def __unicode__(self):
        try:
            return unicode(self._get_current_object())
        except RuntimeError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)

    def __setitem__(self, key, value):
        self._get_current_object()[key] = value

    def __delitem__(self, key):
        del self._get_current_object()[key]

    def __setslice__(self, i, j, seq):
        self._get_current_object()[i:j] = seq

    def __delslice__(self, i, j):
        del self._get_current_object()[i:j]

    __setattr__ = lambda x, n, v: setattr(x._get_current_object(), n, v)
    __delattr__ = lambda x, n: delattr(x._get_current_object(), n)
    __str__ = lambda x: str(x._get_current_object())
    __lt__ = lambda x, o: x._get_current_object() < o
    __le__ = lambda x, o: x._get_current_object() <= o
    __eq__ = lambda x, o: x._get_current_object() == o
    __ne__ = lambda x, o: x._get_current_object() != o
    __gt__ = lambda x, o: x._get_current_object() > o
    __ge__ = lambda x, o: x._get_current_object() >= o
    __cmp__ = lambda x, o: cmp(x._get_current_object(), o)
    __hash__ = lambda x: hash(x._get_current_object())
    __call__ = lambda x, *a, **kw: x._get_current_object()(*a, **kw)
    __len__ = lambda x: len(x._get_current_object())
    __getitem__ = lambda x, i: x._get_current_object()[i]
    __iter__ = lambda x: iter(x._get_current_object())
    __contains__ = lambda x, i: i in x._get_current_object()
    __getslice__ = lambda x, i, j: x._get_current_object()[i:j]
    __add__ = lambda x, o: x._get_current_object() + o
    __sub__ = lambda x, o: x._get_current_object() - o
    __mul__ = lambda x, o: x._get_current_object() * o
    __floordiv__ = lambda x, o: x._get_current_object() // o
    __mod__ = lambda x, o: x._get_current_object() % o
    __divmod__ = lambda x, o: x._get_current_object().__divmod__(o)
    __pow__ = lambda x, o: x._get_current_object() ** o
    __lshift__ = lambda x, o: x._get_current_object() << o
    __rshift__ = lambda x, o: x._get_current_object() >> o
    __and__ = lambda x, o: x._get_current_object() & o
    __xor__ = lambda x, o: x._get_current_object() ^ o
    __or__ = lambda x, o: x._get_current_object() | o
    __div__ = lambda x, o: x._get_current_object().__div__(o)
    __truediv__ = lambda x, o: x._get_current_object().__truediv__(o)
    __neg__ = lambda x: -x._get_current_object()
    __pos__ = lambda x: +x._get_current_object()
    __abs__ = lambda x: abs(x._get_current_object())
    __invert__ = lambda x: ~x._get_current_object()
    __complex__ = lambda x: complex(x._get_current_object())
    __int__ = lambda x: int(x._get_current_object())
    __long__ = lambda x: long(x._get_current_object())
    __float__ = lambda x: float(x._get_current_object())
    __oct__ = lambda x: oct(x._get_current_object())
    __hex__ = lambda x: hex(x._get_current_object())
    __index__ = lambda x: x._get_current_object().__index__()
    __coerce__ = lambda x, o: x.__coerce__(x, o)
    __enter__ = lambda x: x.__enter__()
    __exit__ = lambda x, *a, **kw: x.__exit__(*a, **kw)