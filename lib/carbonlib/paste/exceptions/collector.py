import sys
import traceback
import time
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import linecache
from paste.exceptions import serial_number_generator
import warnings
DEBUG_EXCEPTION_FORMATTER = True
DEBUG_IDENT_PREFIX = 'E-'
FALLBACK_ENCODING = 'UTF-8'
__all__ = ['collect_exception', 'ExceptionCollector']

class ExceptionCollector(object):
    show_revisions = 0

    def __init__(self, limit = None):
        self.limit = limit



    def getLimit(self):
        limit = self.limit
        if limit is None:
            limit = getattr(sys, 'tracebacklimit', None)
        return limit



    def getRevision(self, globals):
        if not self.show_revisions:
            return 
        revision = globals.get('__revision__', None)
        if revision is None:
            revision = globals.get('__version__', None)
        if revision is not None:
            try:
                revision = str(revision).strip()
            except:
                revision = '???'
        return revision



    def collectSupplement(self, supplement, tb):
        result = {}
        for name in ('object', 'source_url', 'line', 'column', 'expression', 'warnings'):
            result[name] = getattr(supplement, name, None)

        func = getattr(supplement, 'getInfo', None)
        if func:
            result['info'] = func()
        else:
            result['info'] = None
        func = getattr(supplement, 'extraData', None)
        if func:
            result['extra'] = func()
        else:
            result['extra'] = None
        return SupplementaryData(**result)



    def collectLine(self, tb, extra_data):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        globals = f.f_globals
        locals = f.f_locals
        if not hasattr(locals, 'has_key'):
            warnings.warn('Frame %s has an invalid locals(): %r' % (globals.get('__name__', 'unknown'), locals))
            locals = {}
        data = {}
        data['modname'] = globals.get('__name__', None)
        data['filename'] = filename
        data['lineno'] = lineno
        data['revision'] = self.getRevision(globals)
        data['name'] = name
        data['tbid'] = id(tb)
        if locals.has_key('__traceback_supplement__'):
            tbs = locals['__traceback_supplement__']
        elif globals.has_key('__traceback_supplement__'):
            tbs = globals['__traceback_supplement__']
        else:
            tbs = None
        if tbs is not None:
            factory = tbs[0]
            args = tbs[1:]
            try:
                supp = factory(*args)
                data['supplement'] = self.collectSupplement(supp, tb)
                if data['supplement'].extra:
                    for (key, value,) in data['supplement'].extra.items():
                        extra_data.setdefault(key, []).append(value)

            except:
                if DEBUG_EXCEPTION_FORMATTER:
                    out = StringIO()
                    traceback.print_exc(file=out)
                    text = out.getvalue()
                    data['supplement_exception'] = text
        try:
            tbi = locals.get('__traceback_info__', None)
            if tbi is not None:
                data['traceback_info'] = str(tbi)
        except:
            pass
        marker = []
        for name in ('__traceback_hide__', '__traceback_log__', '__traceback_decorator__'):
            try:
                tbh = locals.get(name, globals.get(name, marker))
                if tbh is not marker:
                    data[name[2:-2]] = tbh
            except:
                pass

        return data



    def collectExceptionOnly(self, etype, value):
        return traceback.format_exception_only(etype, value)



    def collectException(self, etype, value, tb, limit = None):
        __exception_formatter__ = 1
        frames = []
        ident_data = []
        traceback_decorators = []
        if limit is None:
            limit = self.getLimit()
        n = 0
        extra_data = {}
        while tb is not None and (limit is None or n < limit):
            if tb.tb_frame.f_locals.get('__exception_formatter__'):
                frames.append('(Recursive formatException() stopped)\n')
                break
            data = self.collectLine(tb, extra_data)
            frame = ExceptionFrame(**data)
            frames.append(frame)
            if frame.traceback_decorator is not None:
                traceback_decorators.append(frame.traceback_decorator)
            ident_data.append(frame.modname or '?')
            ident_data.append(frame.name or '?')
            tb = tb.tb_next
            n = n + 1

        ident_data.append(str(etype))
        ident = serial_number_generator.hash_identifier(' '.join(ident_data), length=5, upper=True, prefix=DEBUG_IDENT_PREFIX)
        result = CollectedException(frames=frames, exception_formatted=self.collectExceptionOnly(etype, value), exception_type=etype, exception_value=self.safeStr(value), identification_code=ident, date=time.localtime(), extra_data=extra_data)
        if etype is ImportError:
            extra_data[('important', 'sys.path')] = [sys.path]
        for decorator in traceback_decorators:
            try:
                new_result = decorator(result)
                if new_result is not None:
                    result = new_result
            except:
                pass

        return result



    def safeStr(self, obj):
        try:
            return str(obj)
        except UnicodeEncodeError:
            try:
                return unicode(obj).encode(FALLBACK_ENCODING, 'replace')
            except UnicodeEncodeError:
                return repr(obj)



limit = 200

class Bunch(object):

    def __init__(self, **attrs):
        for (name, value,) in attrs.items():
            setattr(self, name, value)




    def __repr__(self):
        name = '<%s ' % self.__class__.__name__
        name += ' '.join([ '%s=%r' % (name, str(value)[:30]) for (name, value,) in self.__dict__.items() if not name.startswith('_') ])
        return name + '>'




class CollectedException(Bunch):
    frames = []
    exception_formatted = None
    exception_type = None
    exception_value = None
    identification_code = None
    date = None
    extra_data = {}


class SupplementaryData(Bunch):
    object = None
    source_url = None
    line = None
    column = None
    expression = None
    warnings = None
    info = None


class ExceptionFrame(Bunch):
    modname = None
    filename = None
    lineno = None
    revision = None
    name = None
    supplement = None
    supplement_exception = None
    traceback_info = None
    traceback_hide = False
    traceback_decorator = None
    tbid = None

    def get_source_line(self, context = 0):
        if not self.filename or not self.lineno:
            return None
        lines = []
        for lineno in range(self.lineno - context, self.lineno + context + 1):
            lines.append(linecache.getline(self.filename, lineno))

        return ''.join(lines)



if hasattr(sys, 'tracebacklimit'):
    limit = min(limit, sys.tracebacklimit)
col = ExceptionCollector()

def collect_exception(t, v, tb, limit = None):
    return col.collectException(t, v, tb, limit=limit)



