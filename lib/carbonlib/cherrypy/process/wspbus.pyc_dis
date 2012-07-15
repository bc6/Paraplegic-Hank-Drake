#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\process\wspbus.py
import atexit
import os
import sys
import threading
import time
import traceback as _traceback
import warnings
from cherrypy._cpcompat import set
_startup_cwd = os.getcwd()

class ChannelFailures(Exception):
    delimiter = '\n'

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self._exceptions = list()

    def handle_exception(self):
        self._exceptions.append(sys.exc_info())

    def get_instances(self):
        return [ instance for cls, instance, traceback in self._exceptions ]

    def __str__(self):
        exception_strings = map(repr, self.get_instances())
        return self.delimiter.join(exception_strings)

    __repr__ = __str__

    def __nonzero__(self):
        return bool(self._exceptions)


class _StateEnum(object):

    class State(object):
        name = None

        def __repr__(self):
            return 'states.%s' % self.name

    def __setattr__(self, key, value):
        if isinstance(value, self.State):
            value.name = key
        object.__setattr__(self, key, value)


states = _StateEnum()
states.STOPPED = states.State()
states.STARTING = states.State()
states.STARTED = states.State()
states.STOPPING = states.State()
states.EXITING = states.State()

class Bus(object):
    states = states
    state = states.STOPPED
    execv = False

    def __init__(self):
        self.execv = False
        self.state = states.STOPPED
        self.listeners = dict([ (channel, set()) for channel in ('start', 'stop', 'exit', 'graceful', 'log', 'main') ])
        self._priorities = {}

    def subscribe(self, channel, callback, priority = None):
        if channel not in self.listeners:
            self.listeners[channel] = set()
        self.listeners[channel].add(callback)
        if priority is None:
            priority = getattr(callback, 'priority', 50)
        self._priorities[channel, callback] = priority

    def unsubscribe(self, channel, callback):
        listeners = self.listeners.get(channel)
        if listeners and callback in listeners:
            listeners.discard(callback)
            del self._priorities[channel, callback]

    def publish(self, channel, *args, **kwargs):
        if channel not in self.listeners:
            return []
        exc = ChannelFailures()
        output = []
        items = [ (self._priorities[channel, listener], listener) for listener in self.listeners[channel] ]
        items.sort()
        for priority, listener in items:
            try:
                output.append(listener(*args, **kwargs))
            except KeyboardInterrupt:
                raise 
            except SystemExit as e:
                if exc and e.code == 0:
                    e.code = 1
                raise 
            except:
                exc.handle_exception()
                if channel == 'log':
                    pass
                else:
                    self.log('Error in %r listener %r' % (channel, listener), level=40, traceback=True)

        if exc:
            raise exc
        return output

    def _clean_exit(self):
        if self.state != states.EXITING:
            warnings.warn('The main thread is exiting, but the Bus is in the %r state; shutting it down automatically now. You must either call bus.block() after start(), or call bus.exit() before the main thread exits.' % self.state, RuntimeWarning)
            self.exit()

    def start(self):
        atexit.register(self._clean_exit)
        self.state = states.STARTING
        self.log('Bus STARTING')
        try:
            self.publish('start')
            self.state = states.STARTED
            self.log('Bus STARTED')
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            self.log('Shutting down due to error in start listener:', level=40, traceback=True)
            e_info = sys.exc_info()
            try:
                self.exit()
            except:
                pass

            raise e_info[0], e_info[1], e_info[2]

    def exit(self):
        exitstate = self.state
        try:
            self.stop()
            self.state = states.EXITING
            self.log('Bus EXITING')
            self.publish('exit')
            self.log('Bus EXITED')
        except:
            os._exit(70)

        if exitstate == states.STARTING:
            os._exit(70)

    def restart(self):
        self.execv = True
        self.exit()

    def graceful(self):
        self.log('Bus graceful')
        self.publish('graceful')

    def block(self, interval = 0.1):
        try:
            self.wait(states.EXITING, interval=interval, channel='main')
        except (KeyboardInterrupt, IOError):
            self.log('Keyboard Interrupt: shutting down bus')
            self.exit()
        except SystemExit:
            self.log('SystemExit raised: shutting down bus')
            self.exit()
            raise 

        self.log('Waiting for child threads to terminate...')
        for t in threading.enumerate():
            if t != threading.currentThread() and t.isAlive():
                if hasattr(threading.Thread, 'daemon'):
                    d = t.daemon
                else:
                    d = t.isDaemon()
                if not d:
                    self.log('Waiting for thread %s.' % t.getName())
                    t.join()

        if self.execv:
            self._do_execv()

    def wait(self, state, interval = 0.1, channel = None):
        if isinstance(state, (tuple, list)):
            states = state
        else:
            states = [state]

        def _wait():
            while self.state not in states:
                time.sleep(interval)
                self.publish(channel)

        try:
            sys.modules['psyco'].cannotcompile(_wait)
        except (KeyError, AttributeError):
            pass

        _wait()

    def _do_execv(self):
        args = sys.argv[:]
        self.log('Re-spawning %s' % ' '.join(args))
        if sys.platform[:4] == 'java':
            from _systemrestart import SystemRestart
            raise SystemRestart
        else:
            args.insert(0, sys.executable)
            if sys.platform == 'win32':
                args = [ '"%s"' % arg for arg in args ]
            os.chdir(_startup_cwd)
            os.execv(sys.executable, args)

    def stop(self):
        self.state = states.STOPPING
        self.log('Bus STOPPING')
        self.publish('stop')
        self.state = states.STOPPED
        self.log('Bus STOPPED')

    def start_with_callback(self, func, args = None, kwargs = None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        args = (func,) + args

        def _callback(func, *a, **kw):
            self.wait(states.STARTED)
            func(*a, **kw)

        t = threading.Thread(target=_callback, args=args, kwargs=kwargs)
        t.setName('Bus Callback ' + t.getName())
        t.start()
        self.start()
        return t

    def log(self, msg = '', level = 20, traceback = False):
        if traceback:
            exc = sys.exc_info()
            msg += '\n' + ''.join(_traceback.format_exception(*exc))
        self.publish('log', msg, level)


bus = Bus()