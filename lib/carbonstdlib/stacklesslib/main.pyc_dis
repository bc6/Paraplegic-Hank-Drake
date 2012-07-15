#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\stacklesslib\main.py
import heapq
import sys
import time
import traceback
import stackless
stacklessio = None
_sleep = time.sleep
if sys.platform == 'win32':
    elapsed_time = time.clock
else:
    elapsed_time = time.time
SCHEDULING_ROUNDROBIN = 0
SCHEDULING_IMMEDIATE = 1
scheduling_mode = SCHEDULING_ROUNDROBIN

def set_scheduling_mode(mode):
    global scheduling_mode
    old = scheduling_mode
    if mode is not None:
        scheduling_mode = mode
    return old


def set_channel_pref(c):
    if scheduling_mode == SCHEDULING_ROUNDROBIN:
        c.preference = 0
    else:
        c.preference = -1


class EventQueue(object):

    def __init__(self):
        self.queue = []

    def reschedule(self, delta_t):
        self.queue = [ (t + delta_t, what) for t, what in self.queue ]

    def push_at(self, what, when):
        heapq.heappush(self.queue, (when, what))

    def push_after(self, what, delay):
        self.push_at(what, delay + self.time())

    def cancel(self, what):
        for i, e in enumerate(self.queue):
            if e[1] == what:
                del self.queue[i]
                heapq.heapify(self.queue)
                return

        raise ValueError, 'event not in queue'

    def pump(self):
        q = self.queue
        if q:
            batch = []
            now = self.time()
            while q and q[0][0] <= now:
                batch.append(heapq.heappop(q)[1])

            for what in batch:
                try:
                    what()
                except Exception:
                    self.handle_exception(sys.exc_info())

            return len(batch)
        return 0

    @property
    def is_due(self):
        return self.queue and self.queue[0][0] <= self.time()

    def next_time(self):
        if self.queue:
            return self.queue[0][0]

    def handle_exception(self, exc_info):
        traceback.print_exception(*exc_info)

    def time(self):
        return elapsed_time()


class LoopScheduler(object):

    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.chan = stackless.channel()
        set_channel_pref(self.chan)
        self.due = False

    def _get_wakeup(self):
        c = stackless.channel()
        set_channel_pref(c)

        def wakeup():
            if c.balance:
                c.send(None)

        return (wakeup, c)

    @property
    def is_due(self):
        return self.due

    def sleep(self, delay):
        if delay <= 0:
            self.due = True
            self.chan.receive()
        wakeup, c = self._get_wakeup()
        self.event_queue.push_after(wakeup, delay)
        c.receive()

    def sleep_next(self):
        self.chan.receive()

    def pump(self):
        self.due = False
        for i in xrange(-self.chan.balance):
            self.chan.send(None)


class MainLoop(object):

    def __init__(self):
        self.max_wait_time = 1.0
        self.running = True
        self.break_wait = False
        self.event_queue = event_queue
        self.scheduler = scheduler

    def get_wait_time(self, time, delay = None):
        if self.scheduler.is_due:
            return 0.0
        if delay is None:
            delay = self.max_wait_time
        next_event = self.event_queue.next_time()
        if next_event:
            delay = min(delay, next_event - time)
            delay = max(delay, 0.0)
        return delay

    def adjust_wait_times(self, deltaSeconds):
        self.event_queue.reschedule(deltaSeconds)

    def wait(self, delay):
        try:
            if delay:
                t1 = elapsed_time() + delay
                while True:
                    if self.break_wait:
                        if not event_queue.is_due and stackless.runcount == 1:
                            self.break_wait = False
                        else:
                            break
                    now = elapsed_time()
                    remaining = t1 - now
                    if remaining <= 0.0:
                        break
                    _sleep(min(remaining, 0.01))

        finally:
            self.break_wait = False

    def interrupt_wait(self):
        self.break_wait = True

    def wakeup_tasklets(self, time):
        self.scheduler.pump()
        self.event_queue.pump()

    def run_tasklets(self, run_for = 0):
        try:
            return stackless.run(run_for)
        except Exception:
            self.handle_run_error(sys.exc_info())

    def handle_run_error(self, ei):
        traceback.print_exception(*ei)

    def pump(self, run_for = 0):
        t = elapsed_time()
        wait_time = self.get_wait_time(t)
        if wait_time:
            self.wait(wait_time)
            t = elapsed_time()
        self.wakeup_tasklets(t + 0.001)
        return self.run_tasklets(run_for=run_for)

    def run(self):
        while self.running:
            self.pump()

    def stop(self):
        self.running = False

    def sleep(self, delay):
        self.scheduler.sleep(delay)

    def sleep_next(self):
        self.scheduler.sleep_next()


class SLIOMainLoop(MainLoop):

    def wait(self, delay):
        stacklessio.wait(delay)
        stacklessio.dispatch()

    def interrupt_wait(self):
        stacklessio.break_wait()


def sleep(delay):
    mainloop.sleep(delay)


def sleep_next():
    mainloop.sleep_next()


if stacklessio:
    mainloop = SLIOMainLoop
else:
    mainloop = MainLoop
event_queue = EventQueue()
scheduler = LoopScheduler(event_queue)
mainloop = MainLoop()