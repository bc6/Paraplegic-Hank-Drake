#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\test\test_states.py
from cherrypy._cpcompat import BadStatusLine, ntob
import os
import sys
import threading
import time
import cherrypy
engine = cherrypy.engine
thisdir = os.path.join(os.getcwd(), os.path.dirname(__file__))

class Dependency:

    def __init__(self, bus):
        self.bus = bus
        self.running = False
        self.startcount = 0
        self.gracecount = 0
        self.threads = {}

    def subscribe(self):
        self.bus.subscribe('start', self.start)
        self.bus.subscribe('stop', self.stop)
        self.bus.subscribe('graceful', self.graceful)
        self.bus.subscribe('start_thread', self.startthread)
        self.bus.subscribe('stop_thread', self.stopthread)

    def start(self):
        self.running = True
        self.startcount += 1

    def stop(self):
        self.running = False

    def graceful(self):
        self.gracecount += 1

    def startthread(self, thread_id):
        self.threads[thread_id] = None

    def stopthread(self, thread_id):
        del self.threads[thread_id]


db_connection = Dependency(engine)

def setup_server():

    class Root:

        def index(self):
            return 'Hello World'

        index.exposed = True

        def ctrlc(self):
            raise KeyboardInterrupt()

        ctrlc.exposed = True

        def graceful(self):
            engine.graceful()
            return 'app was (gracefully) restarted succesfully'

        graceful.exposed = True

        def block_explicit(self):
            while True:
                if cherrypy.response.timed_out:
                    cherrypy.response.timed_out = False
                    return 'broken!'
                time.sleep(0.01)

        block_explicit.exposed = True

        def block_implicit(self):
            time.sleep(0.5)
            return 'response.timeout = %s' % cherrypy.response.timeout

        block_implicit.exposed = True

    cherrypy.tree.mount(Root())
    cherrypy.config.update({'environment': 'test_suite',
     'engine.deadlock_poll_freq': 0.1})
    db_connection.subscribe()


from cherrypy.test import helper

class ServerStateTests(helper.CPWebCase):
    setup_server = staticmethod(setup_server)

    def setUp(self):
        cherrypy.server.socket_timeout = 0.1

    def test_0_NormalStateFlow(self):
        engine.stop()
        self.assertEqual(db_connection.running, False)
        self.assertEqual(db_connection.startcount, 1)
        self.assertEqual(len(db_connection.threads), 0)
        engine.start()
        self.assertEqual(engine.state, engine.states.STARTED)
        host = cherrypy.server.socket_host
        port = cherrypy.server.socket_port
        self.assertRaises(IOError, cherrypy._cpserver.check_port, host, port)
        self.assertEqual(db_connection.running, True)
        self.assertEqual(db_connection.startcount, 2)
        self.assertEqual(len(db_connection.threads), 0)
        self.getPage('/')
        self.assertBody('Hello World')
        self.assertEqual(len(db_connection.threads), 1)
        engine.stop()
        self.assertEqual(engine.state, engine.states.STOPPED)
        self.assertEqual(db_connection.running, False)
        self.assertEqual(len(db_connection.threads), 0)

        def exittest():
            self.getPage('/')
            self.assertBody('Hello World')
            engine.exit()

        cherrypy.server.start()
        engine.start_with_callback(exittest)
        engine.block()
        self.assertEqual(engine.state, engine.states.EXITING)

    def test_1_Restart(self):
        cherrypy.server.start()
        engine.start()
        self.assertEqual(db_connection.running, True)
        grace = db_connection.gracecount
        self.getPage('/')
        self.assertBody('Hello World')
        self.assertEqual(len(db_connection.threads), 1)
        engine.graceful()
        self.assertEqual(engine.state, engine.states.STARTED)
        self.getPage('/')
        self.assertBody('Hello World')
        self.assertEqual(db_connection.running, True)
        self.assertEqual(db_connection.gracecount, grace + 1)
        self.assertEqual(len(db_connection.threads), 1)
        self.getPage('/graceful')
        self.assertEqual(engine.state, engine.states.STARTED)
        self.assertBody('app was (gracefully) restarted succesfully')
        self.assertEqual(db_connection.running, True)
        self.assertEqual(db_connection.gracecount, grace + 2)
        self.assertEqual(len(db_connection.threads), 0)
        engine.stop()
        self.assertEqual(engine.state, engine.states.STOPPED)
        self.assertEqual(db_connection.running, False)
        self.assertEqual(len(db_connection.threads), 0)

    def test_2_KeyboardInterrupt(self):
        engine.start()
        cherrypy.server.start()
        self.persistent = True
        try:
            self.getPage('/')
            self.assertStatus('200 OK')
            self.assertBody('Hello World')
            self.assertNoHeader('Connection')
            cherrypy.server.httpserver.interrupt = KeyboardInterrupt
            engine.block()
            self.assertEqual(db_connection.running, False)
            self.assertEqual(len(db_connection.threads), 0)
            self.assertEqual(engine.state, engine.states.EXITING)
        finally:
            self.persistent = False

        engine.start()
        cherrypy.server.start()
        try:
            self.getPage('/ctrlc')
        except BadStatusLine:
            pass
        else:
            print self.body
            self.fail('AssertionError: BadStatusLine not raised')

        engine.block()
        self.assertEqual(db_connection.running, False)
        self.assertEqual(len(db_connection.threads), 0)

    def test_3_Deadlocks(self):
        cherrypy.config.update({'response.timeout': 0.2})
        engine.start()
        cherrypy.server.start()
        try:
            self.assertNotEqual(engine.timeout_monitor.thread, None)
            self.assertEqual(engine.timeout_monitor.servings, [])
            self.getPage('/')
            self.assertBody('Hello World')
            while engine.timeout_monitor.servings:
                sys.stdout.write('.')
                time.sleep(0.01)

            self.getPage('/block_explicit')
            self.assertBody('broken!')
            self.getPage('/block_implicit')
            self.assertStatus(500)
            self.assertInBody('raise cherrypy.TimeoutError()')
        finally:
            engine.exit()

    def test_4_Autoreload(self):
        p = helper.CPProcess(ssl=self.scheme.lower() == 'https')
        p.write_conf(extra='test_case_name: "test_4_Autoreload"')
        p.start(imports='cherrypy.test._test_states_demo')
        try:
            self.getPage('/start')
            start = float(self.body)
            time.sleep(2)
            os.utime(os.path.join(thisdir, '_test_states_demo.py'), None)
            time.sleep(2)
            host = cherrypy.server.socket_host
            port = cherrypy.server.socket_port
            cherrypy._cpserver.wait_for_occupied_port(host, port)
            self.getPage('/start')
            self.assert_(float(self.body) > start)
        finally:
            self.getPage('/exit')

        p.join()

    def test_5_Start_Error(self):
        p = helper.CPProcess(ssl=self.scheme.lower() == 'https', wait=True)
        p.write_conf(extra='starterror: True\ntest_case_name: "test_5_Start_Error"\n')
        p.start(imports='cherrypy.test._test_states_demo')
        if p.exit_code == 0:
            self.fail('Process failed to return nonzero exit code.')


class PluginTests(helper.CPWebCase):

    def test_daemonize(self):
        if os.name not in ('posix',):
            return self.skip('skipped (not on posix) ')
        self.HOST = '127.0.0.1'
        self.PORT = 8081
        p = helper.CPProcess(ssl=self.scheme.lower() == 'https', wait=True, daemonize=True, socket_host='127.0.0.1', socket_port=8081)
        p.write_conf(extra='test_case_name: "test_daemonize"')
        p.start(imports='cherrypy.test._test_states_demo')
        try:
            self.getPage('/pid')
            self.assertStatus(200)
            page_pid = int(self.body)
            self.assertEqual(page_pid, p.get_pid())
        finally:
            self.getPage('/exit')

        p.join()
        if p.exit_code != 0:
            self.fail('Daemonized parent process failed to exit cleanly.')


class SignalHandlingTests(helper.CPWebCase):

    def test_SIGHUP_tty(self):
        try:
            from signal import SIGHUP
        except ImportError:
            return self.skip('skipped (no SIGHUP) ')

        p = helper.CPProcess(ssl=self.scheme.lower() == 'https')
        p.write_conf(extra='test_case_name: "test_SIGHUP_tty"')
        p.start(imports='cherrypy.test._test_states_demo')
        os.kill(p.get_pid(), SIGHUP)
        p.join()

    def test_SIGHUP_daemonized(self):
        try:
            from signal import SIGHUP
        except ImportError:
            return self.skip('skipped (no SIGHUP) ')

        if os.name not in ('posix',):
            return self.skip('skipped (not on posix) ')
        p = helper.CPProcess(ssl=self.scheme.lower() == 'https', wait=True, daemonize=True)
        p.write_conf(extra='test_case_name: "test_SIGHUP_daemonized"')
        p.start(imports='cherrypy.test._test_states_demo')
        pid = p.get_pid()
        try:
            os.kill(pid, SIGHUP)
            time.sleep(2)
            self.getPage('/pid')
            self.assertStatus(200)
            new_pid = int(self.body)
            self.assertNotEqual(new_pid, pid)
        finally:
            self.getPage('/exit')

        p.join()

    def test_SIGTERM(self):
        try:
            from signal import SIGTERM
        except ImportError:
            return self.skip('skipped (no SIGTERM) ')

        try:
            from os import kill
        except ImportError:
            return self.skip('skipped (no os.kill) ')

        p = helper.CPProcess(ssl=self.scheme.lower() == 'https')
        p.write_conf(extra='test_case_name: "test_SIGTERM"')
        p.start(imports='cherrypy.test._test_states_demo')
        os.kill(p.get_pid(), SIGTERM)
        p.join()
        if os.name in ('posix',):
            p = helper.CPProcess(ssl=self.scheme.lower() == 'https', wait=True, daemonize=True)
            p.write_conf(extra='test_case_name: "test_SIGTERM_2"')
            p.start(imports='cherrypy.test._test_states_demo')
            os.kill(p.get_pid(), SIGTERM)
            p.join()

    def test_signal_handler_unsubscribe(self):
        try:
            from signal import SIGTERM
        except ImportError:
            return self.skip('skipped (no SIGTERM) ')

        try:
            from os import kill
        except ImportError:
            return self.skip('skipped (no os.kill) ')

        p = helper.CPProcess(ssl=self.scheme.lower() == 'https')
        p.write_conf(extra='unsubsig: True\ntest_case_name: "test_signal_handler_unsubscribe"\n')
        p.start(imports='cherrypy.test._test_states_demo')
        os.kill(p.get_pid(), SIGTERM)
        p.join()
        target_line = open(p.error_log, 'rb').readlines()[-10]
        if ntob('I am an old SIGTERM handler.') not in target_line:
            self.fail('Old SIGTERM handler did not run.\n%r' % target_line)