import threading
import sys
from paste.util import filemixin

class PrintCatcher(filemixin.FileMixin):

    def __init__(self, default = None, factory = None, paramwriter = None, leave_stdout = False):
        if leave_stdout:
            default = sys.stdout
        if default:
            self._defaultfunc = self._writedefault
        elif factory:
            self._defaultfunc = self._writefactory
        elif paramwriter:
            self._defaultfunc = self._writeparam
        else:
            self._defaultfunc = self._writeerror
        self._default = default
        self._factory = factory
        self._paramwriter = paramwriter
        self._catchers = {}



    def write(self, v, currentThread = threading.currentThread):
        name = currentThread().getName()
        catchers = self._catchers
        if not catchers.has_key(name):
            self._defaultfunc(name, v)
        else:
            catcher = catchers[name]
            catcher.write(v)



    def seek(self, *args):
        name = threading.currentThread().getName()
        catchers = self._catchers
        if name not in catchers:
            self._default.seek(*args)
        else:
            catchers[name].seek(*args)



    def read(self, *args):
        name = threading.currentThread().getName()
        catchers = self._catchers
        if name not in catchers:
            self._default.read(*args)
        else:
            catchers[name].read(*args)



    def _writedefault(self, name, v):
        self._default.write(v)



    def _writefactory(self, name, v):
        self._factory(name).write(v)



    def _writeparam(self, name, v):
        self._paramwriter(name, v)



    def _writeerror(self, name, v):
        pass



    def register(self, catcher, name = None, currentThread = threading.currentThread):
        if name is None:
            name = currentThread().getName()
        self._catchers[name] = catcher



    def deregister(self, name = None, currentThread = threading.currentThread):
        if name is None:
            name = currentThread().getName()
        del self._catchers[name]



_printcatcher = None
_oldstdout = None

def install(**kw):
    global deregister
    global _oldstdout
    global register
    global _printcatcher
    if not _printcatcher or sys.stdout is not _printcatcher:
        _oldstdout = sys.stdout
        _printcatcher = sys.stdout = PrintCatcher(**kw)
        register = _printcatcher.register
        deregister = _printcatcher.deregister



def uninstall():
    global deregister
    global _printcatcher
    global register
    global _oldstdout
    if _printcatcher:
        sys.stdout = _oldstdout
        _printcatcher = _oldstdout = None
        register = not_installed_error
        deregister = not_installed_error



def not_installed_error(*args, **kw):
    pass


register = deregister = not_installed_error

class StdinCatcher(filemixin.FileMixin):

    def __init__(self, default = None, factory = None, paramwriter = None):
        if default:
            self._defaultfunc = self._readdefault
        elif factory:
            self._defaultfunc = self._readfactory
        elif paramwriter:
            self._defaultfunc = self._readparam
        else:
            self._defaultfunc = self._readerror
        self._default = default
        self._factory = factory
        self._paramwriter = paramwriter
        self._catchers = {}



    def read(self, size = None, currentThread = threading.currentThread):
        name = currentThread().getName()
        catchers = self._catchers
        if not catchers.has_key(name):
            return self._defaultfunc(name, size)
        else:
            catcher = catchers[name]
            return catcher.read(size)



    def _readdefault(self, name, size):
        self._default.read(size)



    def _readfactory(self, name, size):
        self._factory(name).read(size)



    def _readparam(self, name, size):
        self._paramreader(name, size)



    def _readerror(self, name, size):
        pass



    def register(self, catcher, name = None, currentThread = threading.currentThread):
        if name is None:
            name = currentThread().getName()
        self._catchers[name] = catcher



    def deregister(self, catcher, name = None, currentThread = threading.currentThread):
        if name is None:
            name = currentThread().getName()
        del self._catchers[name]



_stdincatcher = None
_oldstdin = None

def install_stdin(**kw):
    global _stdincatcher
    global _oldstdin
    global register_stdin
    global deregister_stdin
    if not _stdincatcher:
        _oldstdin = sys.stdin
        _stdincatcher = sys.stdin = StdinCatcher(**kw)
        register_stdin = _stdincatcher.register
        deregister_stdin = _stdincatcher.deregister



def uninstall():
    global _stdincatcher
    global deregister_stdin
    global register_stdin
    if _stdincatcher:
        sys.stdin = _oldstdin
        _stdincatcher = _oldstdin = None
        register_stdin = deregister_stdin = not_installed_error_stdin



def not_installed_error_stdin(*args, **kw):
    pass



