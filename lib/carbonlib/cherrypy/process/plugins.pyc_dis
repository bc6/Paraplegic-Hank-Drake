#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\process\plugins.py
import os
import re
import signal as _signal
import sys
import time
import threading
from cherrypy._cpcompat import basestring, get_daemon, get_thread_ident, ntob, set
_module__file__base = os.getcwd()

class SimplePlugin(object):
    bus = None

    def __init__(self, bus):
        self.bus = bus

    def subscribe(self):
        for channel in self.bus.listeners:
            method = getattr(self, channel, None)
            if method is not None:
                self.bus.subscribe(channel, method)

    def unsubscribe(self):
        for channel in self.bus.listeners:
            method = getattr(self, channel, None)
            if method is not None:
                self.bus.unsubscribe(channel, method)


class SignalHandler(object):
    handlers = {}
    signals = {}
    for k, v in vars(_signal).items():
        if k.startswith('SIG') and not k.startswith('SIG_'):
            signals[v] = k

    del k
    del v

    def __init__(self, bus):
        self.bus = bus
        self.handlers = {'SIGTERM': self.bus.exit,
         'SIGHUP': self.handle_SIGHUP,
         'SIGUSR1': self.bus.graceful}
        if sys.platform[:4] == 'java':
            del self.handlers['SIGUSR1']
            self.handlers['SIGUSR2'] = self.bus.graceful
            self.bus.log('SIGUSR1 cannot be set on the JVM platform. Using SIGUSR2 instead.')
            self.handlers['SIGINT'] = self._jython_SIGINT_handler
        self._previous_handlers = {}

    def _jython_SIGINT_handler(self, signum = None, frame = None):
        self.bus.log('Keyboard Interrupt: shutting down bus')
        self.bus.exit()

    def subscribe(self):
        for sig, func in self.handlers.items():
            try:
                self.set_handler(sig, func)
            except ValueError:
                pass

    def unsubscribe(self):
        for signum, handler in self._previous_handlers.items():
            signame = self.signals[signum]
            if handler is None:
                self.bus.log('Restoring %s handler to SIG_DFL.' % signame)
                handler = _signal.SIG_DFL
            else:
                self.bus.log('Restoring %s handler %r.' % (signame, handler))
            try:
                our_handler = _signal.signal(signum, handler)
                if our_handler is None:
                    self.bus.log('Restored old %s handler %r, but our handler was not registered.' % (signame, handler), level=30)
            except ValueError:
                self.bus.log('Unable to restore %s handler %r.' % (signame, handler), level=40, traceback=True)

    def set_handler(self, signal, listener = None):
        if isinstance(signal, basestring):
            signum = getattr(_signal, signal, None)
            if signum is None:
                raise ValueError('No such signal: %r' % signal)
            signame = signal
        else:
            try:
                signame = self.signals[signal]
            except KeyError:
                raise ValueError('No such signal: %r' % signal)

            signum = signal
        prev = _signal.signal(signum, self._handle_signal)
        self._previous_handlers[signum] = prev
        if listener is not None:
            self.bus.log('Listening for %s.' % signame)
            self.bus.subscribe(signame, listener)

    def _handle_signal(self, signum = None, frame = None):
        signame = self.signals[signum]
        self.bus.log('Caught signal %s.' % signame)
        self.bus.publish(signame)

    def handle_SIGHUP(self):
        if os.isatty(sys.stdin.fileno()):
            self.bus.log('SIGHUP caught but not daemonized. Exiting.')
            self.bus.exit()
        else:
            self.bus.log('SIGHUP caught while daemonized. Restarting.')
            self.bus.restart()


try:
    import pwd, grp
except ImportError:
    pwd, grp = (None, None)

class DropPrivileges(SimplePlugin):

    def __init__(self, bus, umask = None, uid = None, gid = None):
        SimplePlugin.__init__(self, bus)
        self.finalized = False
        self.uid = uid
        self.gid = gid
        self.umask = umask

    def _get_uid(self):
        return self._uid

    def _set_uid(self, val):
        if val is not None:
            if pwd is None:
                self.bus.log('pwd module not available; ignoring uid.', level=30)
                val = None
            elif isinstance(val, basestring):
                val = pwd.getpwnam(val)[2]
        self._uid = val

    uid = property(_get_uid, _set_uid, doc='The uid under which to run. Availability: Unix.')

    def _get_gid(self):
        return self._gid

    def _set_gid(self, val):
        if val is not None:
            if grp is None:
                self.bus.log('grp module not available; ignoring gid.', level=30)
                val = None
            elif isinstance(val, basestring):
                val = grp.getgrnam(val)[2]
        self._gid = val

    gid = property(_get_gid, _set_gid, doc='The gid under which to run. Availability: Unix.')

    def _get_umask(self):
        return self._umask

    def _set_umask(self, val):
        if val is not None:
            try:
                os.umask
            except AttributeError:
                self.bus.log('umask function not available; ignoring umask.', level=30)
                val = None

        self._umask = val

    umask = property(_get_umask, _set_umask, doc='The default permission mode for newly created files and directories.\n        \n        Usually expressed in octal format, for example, ``0644``.\n        Availability: Unix, Windows.\n        ')

    def start(self):

        def current_ids():
            name, group = (None, None)
            if pwd:
                name = pwd.getpwuid(os.getuid())[0]
            if grp:
                group = grp.getgrgid(os.getgid())[0]
            return (name, group)

        if self.finalized:
            if not (self.uid is None and self.gid is None):
                self.bus.log('Already running as uid: %r gid: %r' % current_ids())
        elif self.uid is None and self.gid is None:
            if pwd or grp:
                self.bus.log('uid/gid not set', level=30)
        else:
            self.bus.log('Started as uid: %r gid: %r' % current_ids())
            if self.gid is not None:
                os.setgid(self.gid)
                os.setgroups([])
            if self.uid is not None:
                os.setuid(self.uid)
            self.bus.log('Running as uid: %r gid: %r' % current_ids())
        if self.finalized:
            if self.umask is not None:
                self.bus.log('umask already set to: %03o' % self.umask)
        elif self.umask is None:
            self.bus.log('umask not set', level=30)
        else:
            old_umask = os.umask(self.umask)
            self.bus.log('umask old: %03o, new: %03o' % (old_umask, self.umask))
        self.finalized = True

    start.priority = 77


class Daemonizer(SimplePlugin):

    def __init__(self, bus, stdin = '/dev/null', stdout = '/dev/null', stderr = '/dev/null'):
        SimplePlugin.__init__(self, bus)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.finalized = False

    def start(self):
        if self.finalized:
            self.bus.log('Already deamonized.')
        if threading.activeCount() != 1:
            self.bus.log('There are %r active threads. Daemonizing now may cause strange failures.' % threading.enumerate(), level=30)
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            pid = os.fork()
            if pid == 0:
                pass
            else:
                self.bus.log('Forking once.')
                os._exit(0)
        except OSError:
            exc = sys.exc_info()[1]
            sys.exit('%s: fork #1 failed: (%d) %s\n' % (sys.argv[0], exc.errno, exc.strerror))

        os.setsid()
        try:
            pid = os.fork()
            if pid > 0:
                self.bus.log('Forking twice.')
                os._exit(0)
        except OSError:
            exc = sys.exc_info()[1]
            sys.exit('%s: fork #2 failed: (%d) %s\n' % (sys.argv[0], exc.errno, exc.strerror))

        os.chdir('/')
        os.umask(0)
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        self.bus.log('Daemonized to PID: %s' % os.getpid())
        self.finalized = True

    start.priority = 65


class PIDFile(SimplePlugin):

    def __init__(self, bus, pidfile):
        SimplePlugin.__init__(self, bus)
        self.pidfile = pidfile
        self.finalized = False

    def start(self):
        pid = os.getpid()
        if self.finalized:
            self.bus.log('PID %r already written to %r.' % (pid, self.pidfile))
        else:
            open(self.pidfile, 'wb').write(ntob('%s' % pid, 'utf8'))
            self.bus.log('PID %r written to %r.' % (pid, self.pidfile))
            self.finalized = True

    start.priority = 70

    def exit(self):
        try:
            os.remove(self.pidfile)
            self.bus.log('PID file removed: %r.' % self.pidfile)
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            pass


class PerpetualTimer(threading._Timer):

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.isSet():
                return
            try:
                self.function(*self.args, **self.kwargs)
            except Exception:
                self.bus.log('Error in perpetual timer thread function %r.' % self.function, level=40, traceback=True)
                raise 


class BackgroundTask(threading.Thread):

    def __init__(self, interval, function, args = [], kwargs = {}):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.running = False

    def cancel(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.interval)
            if not self.running:
                return
            try:
                self.function(*self.args, **self.kwargs)
            except Exception:
                self.bus.log('Error in background task thread function %r.' % self.function, level=40, traceback=True)
                raise 

    def _set_daemon(self):
        return True


class Monitor(SimplePlugin):
    callback = None
    frequency = 60
    thread = None

    def __init__(self, bus, callback, frequency = 60, name = None):
        SimplePlugin.__init__(self, bus)
        self.callback = callback
        self.frequency = frequency
        self.thread = None
        self.name = name

    def start(self):
        if self.frequency > 0:
            threadname = self.name or self.__class__.__name__
            if self.thread is None:
                self.thread = BackgroundTask(self.frequency, self.callback)
                self.thread.bus = self.bus
                self.thread.setName(threadname)
                self.thread.start()
                self.bus.log('Started monitor thread %r.' % threadname)
            else:
                self.bus.log('Monitor thread %r already started.' % threadname)

    start.priority = 70

    def stop(self):
        if self.thread is None:
            self.bus.log('No thread running for %s.' % self.name or self.__class__.__name__)
        else:
            if self.thread is not threading.currentThread():
                name = self.thread.getName()
                self.thread.cancel()
                if not get_daemon(self.thread):
                    self.bus.log('Joining %r' % name)
                    self.thread.join()
                self.bus.log('Stopped thread %r.' % name)
            self.thread = None

    def graceful(self):
        self.stop()
        self.start()


class Autoreloader(Monitor):
    files = None
    frequency = 1
    match = '.*'

    def __init__(self, bus, frequency = 1, match = '.*'):
        self.mtimes = {}
        self.files = set()
        self.match = match
        Monitor.__init__(self, bus, self.run, frequency)

    def start(self):
        if self.thread is None:
            self.mtimes = {}
        Monitor.start(self)

    start.priority = 70

    def sysfiles(self):
        files = set()
        for k, m in sys.modules.items():
            if re.match(self.match, k):
                if hasattr(m, '__loader__') and hasattr(m.__loader__, 'archive'):
                    f = m.__loader__.archive
                else:
                    f = getattr(m, '__file__', None)
                    if f is not None and not os.path.isabs(f):
                        f = os.path.normpath(os.path.join(_module__file__base, f))
                files.add(f)

        return files

    def run(self):
        for filename in self.sysfiles() | self.files:
            if filename:
                if filename.endswith('.pyc'):
                    filename = filename[:-1]
                oldtime = self.mtimes.get(filename, 0)
                if oldtime is None:
                    continue
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    mtime = None

                if filename not in self.mtimes:
                    self.mtimes[filename] = mtime
                elif mtime is None or mtime > oldtime:
                    self.bus.log('Restarting because %s changed.' % filename)
                    self.thread.cancel()
                    self.bus.log('Stopped thread %r.' % self.thread.getName())
                    self.bus.restart()
                    return


class ThreadManager(SimplePlugin):
    threads = None

    def __init__(self, bus):
        self.threads = {}
        SimplePlugin.__init__(self, bus)
        self.bus.listeners.setdefault('acquire_thread', set())
        self.bus.listeners.setdefault('start_thread', set())
        self.bus.listeners.setdefault('release_thread', set())
        self.bus.listeners.setdefault('stop_thread', set())

    def acquire_thread(self):
        thread_ident = get_thread_ident()
        if thread_ident not in self.threads:
            i = len(self.threads) + 1
            self.threads[thread_ident] = i
            self.bus.publish('start_thread', i)

    def release_thread(self):
        thread_ident = get_thread_ident()
        i = self.threads.pop(thread_ident, None)
        if i is not None:
            self.bus.publish('stop_thread', i)

    def stop(self):
        for thread_ident, i in self.threads.items():
            self.bus.publish('stop_thread', i)

        self.threads.clear()

    graceful = stop