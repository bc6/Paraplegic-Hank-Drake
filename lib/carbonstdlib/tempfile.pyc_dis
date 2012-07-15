#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\tempfile.py
__all__ = ['NamedTemporaryFile',
 'TemporaryFile',
 'SpooledTemporaryFile',
 'mkstemp',
 'mkdtemp',
 'mktemp',
 'TMP_MAX',
 'gettempprefix',
 'tempdir',
 'gettempdir']
import os as _os
import errno as _errno
from random import Random as _Random
try:
    from cStringIO import StringIO as _StringIO
except ImportError:
    from StringIO import StringIO as _StringIO

try:
    import fcntl as _fcntl
except ImportError:

    def _set_cloexec(fd):
        pass


else:

    def _set_cloexec(fd):
        try:
            flags = _fcntl.fcntl(fd, _fcntl.F_GETFD, 0)
        except IOError:
            pass
        else:
            flags |= _fcntl.FD_CLOEXEC
            _fcntl.fcntl(fd, _fcntl.F_SETFD, flags)


try:
    import thread as _thread
except ImportError:
    import dummy_thread as _thread

_allocate_lock = _thread.allocate_lock
_text_openflags = _os.O_RDWR | _os.O_CREAT | _os.O_EXCL
if hasattr(_os, 'O_NOINHERIT'):
    _text_openflags |= _os.O_NOINHERIT
if hasattr(_os, 'O_NOFOLLOW'):
    _text_openflags |= _os.O_NOFOLLOW
_bin_openflags = _text_openflags
if hasattr(_os, 'O_BINARY'):
    _bin_openflags |= _os.O_BINARY
if hasattr(_os, 'TMP_MAX'):
    TMP_MAX = _os.TMP_MAX
else:
    TMP_MAX = 10000
template = 'tmp'
_once_lock = _allocate_lock()
if hasattr(_os, 'lstat'):
    _stat = _os.lstat
elif hasattr(_os, 'stat'):
    _stat = _os.stat
else:

    def _stat(fn):
        try:
            f = open(fn)
        except IOError:
            raise _os.error

        f.close()


def _exists(fn):
    try:
        _stat(fn)
    except _os.error:
        return False

    return True


class _RandomNameSequence:
    characters = 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '0123456789_'

    def __init__(self):
        self.mutex = _allocate_lock()
        self.rng = _Random()
        self.normcase = _os.path.normcase

    def __iter__(self):
        return self

    def next(self):
        m = self.mutex
        c = self.characters
        choose = self.rng.choice
        m.acquire()
        try:
            letters = [ choose(c) for dummy in '123456' ]
        finally:
            m.release()

        return self.normcase(''.join(letters))


def _candidate_tempdir_list():
    dirlist = []
    for envname in ('TMPDIR', 'TEMP', 'TMP'):
        dirname = _os.getenv(envname)
        if dirname:
            dirlist.append(dirname)

    if _os.name == 'riscos':
        dirname = _os.getenv('Wimp$ScrapDir')
        if dirname:
            dirlist.append(dirname)
    elif _os.name == 'nt':
        dirlist.extend(['c:\\temp',
         'c:\\tmp',
         '\\temp',
         '\\tmp'])
    else:
        dirlist.extend(['/tmp', '/var/tmp', '/usr/tmp'])
    try:
        dirlist.append(_os.getcwd())
    except (AttributeError, _os.error):
        dirlist.append(_os.curdir)

    return dirlist


def _get_default_tempdir():
    namer = _RandomNameSequence()
    dirlist = _candidate_tempdir_list()
    flags = _text_openflags
    for dir in dirlist:
        if dir != _os.curdir:
            dir = _os.path.normcase(_os.path.abspath(dir))
        for seq in xrange(100):
            name = namer.next()
            filename = _os.path.join(dir, name)
            try:
                fd = _os.open(filename, flags, 384)
                fp = _os.fdopen(fd, 'w')
                fp.write('blat')
                fp.close()
                _os.unlink(filename)
                del fp
                del fd
                return dir
            except (OSError, IOError) as e:
                if e[0] != _errno.EEXIST:
                    break

    raise IOError, (_errno.ENOENT, 'No usable temporary directory found in %s' % dirlist)


_name_sequence = None

def _get_candidate_names():
    global _name_sequence
    if _name_sequence is None:
        _once_lock.acquire()
        try:
            if _name_sequence is None:
                _name_sequence = _RandomNameSequence()
        finally:
            _once_lock.release()

    return _name_sequence


def _mkstemp_inner(dir, pre, suf, flags):
    names = _get_candidate_names()
    for seq in xrange(TMP_MAX):
        name = names.next()
        file = _os.path.join(dir, pre + name + suf)
        try:
            fd = _os.open(file, flags, 384)
            _set_cloexec(fd)
            return (fd, _os.path.abspath(file))
        except OSError as e:
            if e.errno == _errno.EEXIST:
                continue
            raise 

    raise IOError, (_errno.EEXIST, 'No usable temporary file name found')


def gettempprefix():
    return template


tempdir = None

def gettempdir():
    global tempdir
    if tempdir is None:
        _once_lock.acquire()
        try:
            if tempdir is None:
                tempdir = _get_default_tempdir()
        finally:
            _once_lock.release()

    return tempdir


def mkstemp(suffix = '', prefix = template, dir = None, text = False):
    if dir is None:
        dir = gettempdir()
    if text:
        flags = _text_openflags
    else:
        flags = _bin_openflags
    return _mkstemp_inner(dir, prefix, suffix, flags)


def mkdtemp(suffix = '', prefix = template, dir = None):
    if dir is None:
        dir = gettempdir()
    names = _get_candidate_names()
    for seq in xrange(TMP_MAX):
        name = names.next()
        file = _os.path.join(dir, prefix + name + suffix)
        try:
            _os.mkdir(file, 448)
            return file
        except OSError as e:
            if e.errno == _errno.EEXIST:
                continue
            raise 

    raise IOError, (_errno.EEXIST, 'No usable temporary directory name found')


def mktemp(suffix = '', prefix = template, dir = None):
    if dir is None:
        dir = gettempdir()
    names = _get_candidate_names()
    for seq in xrange(TMP_MAX):
        name = names.next()
        file = _os.path.join(dir, prefix + name + suffix)
        if not _exists(file):
            return file

    raise IOError, (_errno.EEXIST, 'No usable temporary filename found')


class _TemporaryFileWrapper:

    def __init__(self, file, name, delete = True):
        self.file = file
        self.name = name
        self.close_called = False
        self.delete = delete

    def __getattr__(self, name):
        file = self.__dict__['file']
        a = getattr(file, name)
        if not issubclass(type(a), type(0)):
            setattr(self, name, a)
        return a

    def __enter__(self):
        self.file.__enter__()
        return self

    if _os.name != 'nt':
        unlink = _os.unlink

        def close(self):
            if not self.close_called:
                self.close_called = True
                self.file.close()
                if self.delete:
                    self.unlink(self.name)

        def __del__(self):
            self.close()

        def __exit__(self, exc, value, tb):
            result = self.file.__exit__(exc, value, tb)
            self.close()
            return result

    else:

        def __exit__(self, exc, value, tb):
            self.file.__exit__(exc, value, tb)


def NamedTemporaryFile(mode = 'w+b', bufsize = -1, suffix = '', prefix = template, dir = None, delete = True):
    if dir is None:
        dir = gettempdir()
    if 'b' in mode:
        flags = _bin_openflags
    else:
        flags = _text_openflags
    if _os.name == 'nt' and delete:
        flags |= _os.O_TEMPORARY
    fd, name = _mkstemp_inner(dir, prefix, suffix, flags)
    file = _os.fdopen(fd, mode, bufsize)
    return _TemporaryFileWrapper(file, name, delete)


if _os.name != 'posix' or _os.sys.platform == 'cygwin':
    TemporaryFile = NamedTemporaryFile
else:

    def TemporaryFile(mode = 'w+b', bufsize = -1, suffix = '', prefix = template, dir = None):
        if dir is None:
            dir = gettempdir()
        if 'b' in mode:
            flags = _bin_openflags
        else:
            flags = _text_openflags
        fd, name = _mkstemp_inner(dir, prefix, suffix, flags)
        try:
            _os.unlink(name)
            return _os.fdopen(fd, mode, bufsize)
        except:
            _os.close(fd)
            raise 


class SpooledTemporaryFile:
    _rolled = False

    def __init__(self, max_size = 0, mode = 'w+b', bufsize = -1, suffix = '', prefix = template, dir = None):
        self._file = _StringIO()
        self._max_size = max_size
        self._rolled = False
        self._TemporaryFileArgs = (mode,
         bufsize,
         suffix,
         prefix,
         dir)

    def _check(self, file):
        if self._rolled:
            return
        max_size = self._max_size
        if max_size and file.tell() > max_size:
            self.rollover()

    def rollover(self):
        if self._rolled:
            return
        file = self._file
        newfile = self._file = TemporaryFile(*self._TemporaryFileArgs)
        del self._TemporaryFileArgs
        newfile.write(file.getvalue())
        newfile.seek(file.tell(), 0)
        self._rolled = True

    def __enter__(self):
        if self._file.closed:
            raise ValueError('Cannot enter context with closed file')
        return self

    def __exit__(self, exc, value, tb):
        self._file.close()

    def __iter__(self):
        return self._file.__iter__()

    def close(self):
        self._file.close()

    @property
    def closed(self):
        return self._file.closed

    @property
    def encoding(self):
        return self._file.encoding

    def fileno(self):
        self.rollover()
        return self._file.fileno()

    def flush(self):
        self._file.flush()

    def isatty(self):
        return self._file.isatty()

    @property
    def mode(self):
        return self._file.mode

    @property
    def name(self):
        return self._file.name

    @property
    def newlines(self):
        return self._file.newlines

    def next(self):
        return self._file.next

    def read(self, *args):
        return self._file.read(*args)

    def readline(self, *args):
        return self._file.readline(*args)

    def readlines(self, *args):
        return self._file.readlines(*args)

    def seek(self, *args):
        self._file.seek(*args)

    @property
    def softspace(self):
        return self._file.softspace

    def tell(self):
        return self._file.tell()

    def truncate(self):
        self._file.truncate()

    def write(self, s):
        file = self._file
        rv = file.write(s)
        self._check(file)
        return rv

    def writelines(self, iterable):
        file = self._file
        rv = file.writelines(iterable)
        self._check(file)
        return rv

    def xreadlines(self, *args):
        return self._file.xreadlines(*args)