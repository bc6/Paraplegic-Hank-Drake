import os
import sys
import time
import threading
import traceback
from paste.util.classinstance import classinstancemethod

def install(poll_interval = 1):
    mon = Monitor(poll_interval=poll_interval)
    t = threading.Thread(target=mon.periodic_reload)
    t.setDaemon(True)
    t.start()



class Monitor(object):
    instances = []
    global_extra_files = []
    global_file_callbacks = []

    def __init__(self, poll_interval):
        self.module_mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = list(self.global_extra_files)
        self.instances.append(self)
        self.file_callbacks = list(self.global_file_callbacks)



    def periodic_reload(self):
        while True:
            if not self.check_reload():
                os._exit(3)
                break
            time.sleep(self.poll_interval)




    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print >> sys.stderr, 'Error calling paste.reloader callback %r:' % file_callback
                traceback.print_exc()

        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError) as exc:
                continue
            if filename is not None:
                filenames.append(filename)

        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            elif filename.endswith('$py.class') and os.path.exists(filename[:-9] + '.py'):
                mtime = max(os.stat(filename[:-9] + '.py').st_mtime, mtime)
            if not self.module_mtimes.has_key(filename):
                self.module_mtimes[filename] = mtime
            else:
                if self.module_mtimes[filename] < mtime:
                    print >> sys.stderr, '%s changed; reloading...' % filename
                    return False

        return True



    def watch_file(self, cls, filename):
        filename = os.path.abspath(filename)
        if self is None:
            for instance in cls.instances:
                instance.watch_file(filename)

            cls.global_extra_files.append(filename)
        else:
            self.extra_files.append(filename)


    watch_file = classinstancemethod(watch_file)

    def add_file_callback(self, cls, callback):
        if self is None:
            for instance in cls.instances:
                instance.add_file_callback(callback)

            cls.global_file_callbacks.append(callback)
        else:
            self.file_callbacks.append(callback)


    add_file_callback = classinstancemethod(add_file_callback)

if sys.platform.startswith('java'):
    try:
        from _systemrestart import SystemRestart
    except ImportError:
        pass
    else:

        class JythonMonitor(Monitor):

            def periodic_reload(self):
                while True:
                    if not self.check_reload():
                        raise SystemRestart()
                    time.sleep(self.poll_interval)




watch_file = Monitor.watch_file
add_file_callback = Monitor.add_file_callback

