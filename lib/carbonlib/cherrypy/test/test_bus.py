from cherrypy.test import test
test.prefer_parent_path()
try:
    set
except NameError:
    from sets import Set as set
import threading
import time
import unittest
import cherrypy
from cherrypy.process import wspbus
msg = 'Listener %d on channel %s: %s.'

class PublishSubscribeTests(unittest.TestCase):

    def get_listener(self, channel, index):

        def listener(arg = None):
            self.responses.append(msg % (index, channel, arg))


        return listener



    def test_builtin_channels(self):
        b = wspbus.Bus()
        (self.responses, expected,) = ([], [])
        for channel in b.listeners:
            for (index, priority,) in enumerate([100,
             50,
             0,
             51]):
                b.subscribe(channel, self.get_listener(channel, index), priority)


        for channel in b.listeners:
            b.publish(channel)
            expected.extend([ msg % (i, channel, None) for i in (2, 1, 3, 0) ])
            b.publish(channel, arg=79347)
            expected.extend([ msg % (i, channel, 79347) for i in (2, 1, 3, 0) ])

        self.assertEqual(self.responses, expected)



    def test_custom_channels(self):
        b = wspbus.Bus()
        (self.responses, expected,) = ([], [])
        custom_listeners = ('hugh', 'louis', 'dewey')
        for channel in custom_listeners:
            for (index, priority,) in enumerate([None,
             10,
             60,
             40]):
                b.subscribe(channel, self.get_listener(channel, index), priority)


        for channel in custom_listeners:
            b.publish(channel, 'ah so')
            expected.extend([ msg % (i, channel, 'ah so') for i in (1, 3, 0, 2) ])
            b.publish(channel)
            expected.extend([ msg % (i, channel, None) for i in (1, 3, 0, 2) ])

        self.assertEqual(self.responses, expected)



    def test_listener_errors(self):
        b = wspbus.Bus()
        (self.responses, expected,) = ([], [])
        channels = [ c for c in b.listeners if c != 'log' ]
        for channel in channels:
            b.subscribe(channel, self.get_listener(channel, 1))
            b.subscribe(channel, lambda : None, priority=20)

        for channel in channels:
            self.assertRaises(wspbus.ChannelFailures, b.publish, channel, 123)
            expected.append(msg % (1, channel, 123))

        self.assertEqual(self.responses, expected)




class BusMethodTests(unittest.TestCase):

    def log(self, bus):
        self._log_entries = []

        def logit(msg, level):
            self._log_entries.append(msg)


        bus.subscribe('log', logit)



    def assertLog(self, entries):
        self.assertEqual(self._log_entries, entries)



    def get_listener(self, channel, index):

        def listener(arg = None):
            self.responses.append(msg % (index, channel, arg))


        return listener



    def test_start(self):
        b = wspbus.Bus()
        self.log(b)
        self.responses = []
        num = 3
        for index in range(num):
            b.subscribe('start', self.get_listener('start', index))

        b.start()
        try:
            self.assertEqual(set(self.responses), set([ msg % (i, 'start', None) for i in range(num) ]))
            self.assertEqual(b.state, b.states.STARTED)
            self.assertLog(['Bus STARTING', 'Bus STARTED'])

        finally:
            b.exit()




    def test_stop(self):
        b = wspbus.Bus()
        self.log(b)
        self.responses = []
        num = 3
        for index in range(num):
            b.subscribe('stop', self.get_listener('stop', index))

        b.stop()
        self.assertEqual(set(self.responses), set([ msg % (i, 'stop', None) for i in range(num) ]))
        self.assertEqual(b.state, b.states.STOPPED)
        self.assertLog(['Bus STOPPING', 'Bus STOPPED'])



    def test_graceful(self):
        b = wspbus.Bus()
        self.log(b)
        self.responses = []
        num = 3
        for index in range(num):
            b.subscribe('graceful', self.get_listener('graceful', index))

        b.graceful()
        self.assertEqual(set(self.responses), set([ msg % (i, 'graceful', None) for i in range(num) ]))
        self.assertLog(['Bus graceful'])



    def test_exit(self):
        b = wspbus.Bus()
        self.log(b)
        self.responses = []
        num = 3
        for index in range(num):
            b.subscribe('stop', self.get_listener('stop', index))
            b.subscribe('exit', self.get_listener('exit', index))

        b.exit()
        self.assertEqual(set(self.responses), set([ msg % (i, 'stop', None) for i in range(num) ] + [ msg % (i, 'exit', None) for i in range(num) ]))
        self.assertEqual(b.state, b.states.EXITING)
        self.assertLog(['Bus STOPPING',
         'Bus STOPPED',
         'Bus EXITING',
         'Bus EXITED'])



    def test_wait(self):
        b = wspbus.Bus()

        def f(method):
            time.sleep(0.2)
            getattr(b, method)()


        for (method, states,) in [('start', [b.states.STARTED]),
         ('stop', [b.states.STOPPED]),
         ('start', [b.states.STARTING, b.states.STARTED]),
         ('exit', [b.states.EXITING])]:
            threading.Thread(target=f, args=(method,)).start()
            b.wait(states)
            if b.state not in states:
                self.fail('State %r not in %r' % (b.state, states))




    def test_block(self):
        b = wspbus.Bus()
        self.log(b)

        def f():
            time.sleep(0.2)
            b.exit()



        def g():
            time.sleep(0.4)


        threading.Thread(target=f).start()
        threading.Thread(target=g).start()
        self.assertEqual(len(threading.enumerate()), 3)
        b.block()
        self.assertEqual(b.state, b.states.EXITING)
        self.assertEqual(len(threading.enumerate()), 1)
        self.assertLog(['Bus STOPPING',
         'Bus STOPPED',
         'Bus EXITING',
         'Bus EXITED',
         'Waiting for child threads to terminate...'])



    def test_start_with_callback(self):
        b = wspbus.Bus()
        self.log(b)
        try:
            events = []

            def f(*args, **kwargs):
                events.append(('f', args, kwargs))



            def g():
                events.append('g')


            b.subscribe('start', g)
            b.start_with_callback(f, (1, 3, 5), {'foo': 'bar'})
            time.sleep(0.2)
            self.assertEqual(b.state, b.states.STARTED)
            self.assertEqual(events, ['g', ('f', (1, 3, 5), {'foo': 'bar'})])

        finally:
            b.exit()




    def test_log(self):
        b = wspbus.Bus()
        self.log(b)
        self.assertLog([])
        expected = []
        for msg in ["O mah darlin'"] * 3 + ['Clementiiiiiiiine']:
            b.log(msg)
            expected.append(msg)
            self.assertLog(expected)

        try:
            foo
        except NameError:
            b.log('You are lost and gone forever', traceback=True)
            lastmsg = self._log_entries[-1]
            if 'Traceback' not in lastmsg or 'NameError' not in lastmsg:
                self.fail('Last log message %r did not contain the expected traceback.' % lastmsg)
        else:
            self.fail('NameError was not raised as expected.')



if __name__ == '__main__':
    unittest.main()

