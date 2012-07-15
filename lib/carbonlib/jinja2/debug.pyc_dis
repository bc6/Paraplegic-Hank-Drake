#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\debug.py
import sys
import traceback
from types import TracebackType
from jinja2.utils import CodeType, missing, internal_code
from jinja2.exceptions import TemplateSyntaxError
try:
    from __pypy__ import tproxy
except ImportError:
    tproxy = None

try:
    exec "raise TypeError, 'foo'"
except SyntaxError:
    raise_helper = 'raise __jinja_exception__[1]'
except TypeError:
    raise_helper = 'raise __jinja_exception__[0], __jinja_exception__[1]'

class TracebackFrameProxy(object):

    def __init__(self, tb):
        self.tb = tb
        self._tb_next = None

    @property
    def tb_next(self):
        return self._tb_next

    def set_next(self, next):
        if tb_set_next is not None:
            try:
                tb_set_next(self.tb, next and next.tb or None)
            except Exception:
                pass

        self._tb_next = next

    @property
    def is_jinja_frame(self):
        return '__jinja_template__' in self.tb.tb_frame.f_globals

    def __getattr__(self, name):
        return getattr(self.tb, name)


def make_frame_proxy(frame):
    proxy = TracebackFrameProxy(frame)
    if tproxy is None:
        return proxy

    def operation_handler(operation, *args, **kwargs):
        if operation in ('__getattribute__', '__getattr__'):
            return getattr(proxy, args[0])
        if operation == '__setattr__':
            proxy.__setattr__(*args, **kwargs)
        else:
            return getattr(proxy, operation)(*args, **kwargs)

    return tproxy(TracebackType, operation_handler)


class ProcessedTraceback(object):

    def __init__(self, exc_type, exc_value, frames):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.frames = frames
        prev_tb = None
        for tb in self.frames:
            if prev_tb is not None:
                prev_tb.set_next(tb)
            prev_tb = tb

        prev_tb.set_next(None)

    def render_as_text(self, limit = None):
        lines = traceback.format_exception(self.exc_type, self.exc_value, self.frames[0], limit=limit)
        return ''.join(lines).rstrip()

    def render_as_html(self, full = False):
        from jinja2.debugrenderer import render_traceback
        return u'%s\n\n<!--\n%s\n-->' % (render_traceback(self, full=full), self.render_as_text().decode('utf-8', 'replace'))

    @property
    def is_template_syntax_error(self):
        return isinstance(self.exc_value, TemplateSyntaxError)

    @property
    def exc_info(self):
        return (self.exc_type, self.exc_value, self.frames[0])

    @property
    def standard_exc_info(self):
        tb = self.frames[0]
        if type(tb) is not TracebackType:
            tb = tb.tb
        return (self.exc_type, self.exc_value, tb)


def make_traceback(exc_info, source_hint = None):
    exc_type, exc_value, tb = exc_info
    if isinstance(exc_value, TemplateSyntaxError):
        exc_info = translate_syntax_error(exc_value, source_hint)
        initial_skip = 0
    else:
        initial_skip = 1
    return translate_exception(exc_info, initial_skip)


def translate_syntax_error(error, source = None):
    error.source = source
    error.translated = True
    exc_info = (error.__class__, error, None)
    filename = error.filename
    if filename is None:
        filename = '<unknown>'
    return fake_exc_info(exc_info, filename, error.lineno)


def translate_exception(exc_info, initial_skip = 0):
    tb = exc_info[2]
    frames = []
    for x in xrange(initial_skip):
        if tb is not None:
            tb = tb.tb_next

    initial_tb = tb
    while tb is not None:
        if tb.tb_frame.f_code in internal_code:
            tb = tb.tb_next
            continue
        next = tb.tb_next
        template = tb.tb_frame.f_globals.get('__jinja_template__')
        if template is not None:
            lineno = template.get_corresponding_lineno(tb.tb_lineno)
            tb = fake_exc_info(exc_info[:2] + (tb,), template.filename, lineno)[2]
        frames.append(make_frame_proxy(tb))
        tb = next

    if not frames:
        raise exc_info[0], exc_info[1], exc_info[2]
    return ProcessedTraceback(exc_info[0], exc_info[1], frames)


def fake_exc_info(exc_info, filename, lineno):
    exc_type, exc_value, tb = exc_info
    if tb is not None:
        real_locals = tb.tb_frame.f_locals.copy()
        ctx = real_locals.get('context')
        if ctx:
            locals = ctx.get_all()
        else:
            locals = {}
        for name, value in real_locals.iteritems():
            if name.startswith('l_') and value is not missing:
                locals[name[2:]] = value

        locals.pop('__jinja_exception__', None)
    else:
        locals = {}
    globals = {'__name__': filename,
     '__file__': filename,
     '__jinja_exception__': exc_info[:2],
     '__jinja_template__': None}
    code = compile('\n' * (lineno - 1) + raise_helper, filename, 'exec')
    try:
        if tb is None:
            location = 'template'
        else:
            function = tb.tb_frame.f_code.co_name
            if function == 'root':
                location = 'top-level template code'
            elif function.startswith('block_'):
                location = 'block "%s"' % function[6:]
            else:
                location = 'template'
        code = CodeType(0, code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code, code.co_consts, code.co_names, code.co_varnames, filename, location, code.co_firstlineno, code.co_lnotab, (), ())
    except:
        pass

    try:
        exec code in globals, locals
    except:
        exc_info = sys.exc_info()
        new_tb = exc_info[2].tb_next

    return exc_info[:2] + (new_tb,)


def _init_ugly_crap():
    import ctypes
    from types import TracebackType
    if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
        _Py_ssize_t = ctypes.c_int64
    else:
        _Py_ssize_t = ctypes.c_int

    class _PyObject(ctypes.Structure):
        pass

    _PyObject._fields_ = [('ob_refcnt', _Py_ssize_t), ('ob_type', ctypes.POINTER(_PyObject))]
    if hasattr(sys, 'getobjects'):

        class _PyObject(ctypes.Structure):
            pass

        _PyObject._fields_ = [('_ob_next', ctypes.POINTER(_PyObject)),
         ('_ob_prev', ctypes.POINTER(_PyObject)),
         ('ob_refcnt', _Py_ssize_t),
         ('ob_type', ctypes.POINTER(_PyObject))]

    class _Traceback(_PyObject):
        pass

    _Traceback._fields_ = [('tb_next', ctypes.POINTER(_Traceback)),
     ('tb_frame', ctypes.POINTER(_PyObject)),
     ('tb_lasti', ctypes.c_int),
     ('tb_lineno', ctypes.c_int)]

    def tb_set_next(tb, next):
        if not (isinstance(tb, TracebackType) and (next is None or isinstance(next, TracebackType))):
            raise TypeError('tb_set_next arguments must be traceback objects')
        obj = _Traceback.from_address(id(tb))
        if tb.tb_next is not None:
            old = _Traceback.from_address(id(tb.tb_next))
            old.ob_refcnt -= 1
        if next is None:
            obj.tb_next = ctypes.POINTER(_Traceback)()
        else:
            next = _Traceback.from_address(id(next))
            next.ob_refcnt += 1
            obj.tb_next = ctypes.pointer(next)

    return tb_set_next


tb_set_next = None
if tproxy is None:
    try:
        from jinja2._debugsupport import tb_set_next
    except ImportError:
        try:
            tb_set_next = _init_ugly_crap()
        except:
            pass

    del _init_ugly_crap