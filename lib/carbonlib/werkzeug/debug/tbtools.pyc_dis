#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\debug\tbtools.py
import re
import os
import sys
import inspect
import traceback
import codecs
from tokenize import TokenError
from werkzeug.utils import cached_property
from werkzeug.debug.console import Console
from werkzeug.debug.utils import render_template
_coding_re = re.compile('coding[:=]\\s*([-\\w.]+)')
_line_re = re.compile('^(.*?)$(?m)')
_funcdef_re = re.compile('^(\\s*def\\s)|(.*(?<!\\w)lambda(:|\\s))|^(\\s*@)')
UTF8_COOKIE = '\xef\xbb\xbf'
system_exceptions = (SystemExit, KeyboardInterrupt)
try:
    system_exceptions += (GeneratorExit,)
except NameError:
    pass

def get_current_traceback(ignore_system_exceptions = False, show_hidden_frames = False, skip = 0):
    exc_type, exc_value, tb = sys.exc_info()
    if ignore_system_exceptions and exc_type in system_exceptions:
        raise 
    for x in xrange(skip):
        if tb.tb_next is None:
            break
        tb = tb.tb_next

    tb = Traceback(exc_type, exc_value, tb)
    if not show_hidden_frames:
        tb.filter_hidden_frames()
    return tb


class Line(object):
    __slots__ = ('lineno', 'code', 'in_frame', 'current')

    def __init__(self, lineno, code):
        self.lineno = lineno
        self.code = code
        self.in_frame = False
        self.current = False

    def classes(self):
        rv = ['line']
        if self.in_frame:
            rv.append('in-frame')
        if self.current:
            rv.append('current')
        return rv

    classes = property(classes)


class Traceback(object):

    def __init__(self, exc_type, exc_value, tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        if not isinstance(exc_type, str):
            exception_type = exc_type.__name__
            if exc_type.__module__ not in ('__builtin__', 'exceptions'):
                exception_type = exc_type.__module__ + '.' + exception_type
        else:
            exception_type = exc_type
        self.exception_type = exception_type
        self.frames = []
        while tb:
            self.frames.append(Frame(exc_type, exc_value, tb))
            tb = tb.tb_next

    def filter_hidden_frames(self):
        new_frames = []
        hidden = False
        for frame in self.frames:
            hide = frame.hide
            if hide in ('before', 'before_and_this'):
                new_frames = []
                hidden = False
                if hide == 'before_and_this':
                    continue
            elif hide in ('reset', 'reset_and_this'):
                hidden = False
                if hide == 'reset_and_this':
                    continue
            elif hide in ('after', 'after_and_this'):
                hidden = True
                if hide == 'after_and_this':
                    continue
            elif hide or hidden:
                continue
            new_frames.append(frame)

        if self.frames[-1] in new_frames:
            self.frames[:] = new_frames

    def is_syntax_error(self):
        return isinstance(self.exc_value, SyntaxError)

    is_syntax_error = property(is_syntax_error)

    def exception(self):
        buf = traceback.format_exception_only(self.exc_type, self.exc_value)
        return ''.join(buf).strip().decode('utf-8', 'replace')

    exception = property(exception)

    def log(self, logfile = None):
        if logfile is None:
            logfile = sys.stderr
        tb = self.plaintext.encode('utf-8', 'replace').rstrip() + '\n'
        logfile.write(tb)

    def paste(self):
        from xmlrpclib import ServerProxy
        srv = ServerProxy('http://paste.pocoo.org/xmlrpc/')
        return srv.pastes.newPaste('pytb', self.plaintext)

    def render_summary(self, include_title = True):
        return render_template('traceback_summary.html', traceback=self, include_title=include_title)

    def render_full(self, evalex = False):
        return render_template('traceback_full.html', traceback=self, evalex=evalex)

    def plaintext(self):
        return render_template('traceback_plaintext.html', traceback=self)

    plaintext = cached_property(plaintext)
    id = property(lambda x: id(x))


class Frame(object):

    def __init__(self, exc_type, exc_value, tb):
        self.lineno = tb.tb_lineno
        self.function_name = tb.tb_frame.f_code.co_name
        self.locals = tb.tb_frame.f_locals
        self.globals = tb.tb_frame.f_globals
        fn = inspect.getsourcefile(tb) or inspect.getfile(tb)
        if fn[-4:] in ('.pyo', '.pyc'):
            fn = fn[:-1]
        if os.path.isfile(fn):
            fn = os.path.realpath(fn)
        self.filename = fn
        self.module = self.globals.get('__name__')
        self.loader = self.globals.get('__loader__')
        self.code = tb.tb_frame.f_code
        self.hide = self.locals.get('__traceback_hide__', False)
        info = self.locals.get('__traceback_info__')
        if info is not None:
            try:
                info = unicode(info)
            except UnicodeError:
                info = str(info).decode('utf-8', 'replace')

        self.info = info

    def render(self):
        return render_template('frame.html', frame=self)

    def render_source(self):
        lines = [ Line(idx + 1, x) for idx, x in enumerate(self.sourcelines) ]
        if hasattr(self.code, 'co_firstlineno'):
            lineno = self.code.co_firstlineno - 1
            while lineno > 0:
                if _funcdef_re.match(lines[lineno].code):
                    break
                lineno -= 1

            try:
                offset = len(inspect.getblock([ x.code + '\n' for x in lines[lineno:] ]))
            except TokenError:
                offset = 0

            for line in lines[lineno:lineno + offset]:
                line.in_frame = True

        try:
            lines[self.lineno - 1].current = True
        except IndexError:
            pass

        return render_template('source.html', frame=self, lines=lines)

    def eval(self, code, mode = 'single'):
        if isinstance(code, basestring):
            if isinstance(code, unicode):
                code = UTF8_COOKIE + code.encode('utf-8')
            code = compile(code, '<interactive>', mode)
        if mode != 'exec':
            return eval(code, self.globals, self.locals)
        exec code in self.globals, self.locals

    @cached_property
    def sourcelines(self):
        source = None
        if self.loader is not None:
            try:
                if hasattr(self.loader, 'get_source'):
                    source = self.loader.get_source(self.module)
                elif hasattr(self.loader, 'get_source_by_code'):
                    source = self.loader.get_source_by_code(self.code)
            except:
                pass

        if source is None:
            try:
                f = file(self.filename)
            except IOError:
                return []

            try:
                source = f.read()
            finally:
                f.close()

        if isinstance(source, unicode):
            return source.splitlines()
        charset = 'utf-8'
        if source.startswith(UTF8_COOKIE):
            source = source[3:]
        else:
            for idx, match in enumerate(_line_re.finditer(source)):
                match = _line_re.search(match.group())
                if match is not None:
                    charset = match.group(1)
                    break
                if idx > 1:
                    break

        try:
            codecs.lookup(charset)
        except LookupError:
            charset = 'utf-8'

        return source.decode(charset, 'replace').splitlines()

    @property
    def current_line(self):
        try:
            return self.sourcelines[self.lineno - 1]
        except IndexError:
            return u''

    @cached_property
    def console(self):
        return Console(self.globals, self.locals)

    id = property(lambda x: id(x))