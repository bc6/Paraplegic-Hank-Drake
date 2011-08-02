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
        self.queue_a = []
        self.queue_b = []



    def push_at(self, what, when):
        heapq.heappush(self.queue_a, (when, what))



    def push_after(self, what, delay):
        self.push_at(what, delay + elapsed_time())



    def push_yield(self, what):
        self.queue_b.append(what)



    def cancel(self, what):
        try:
            self.queue_b.remove(what)
        except ValueError:
            pass
        for e in self.queue_a:
            if e[1] == what:
                self.queue_a.remove(e)
                return 

        raise ValueError, 'event not in queue'



    def pump(self):
        now = elapsed_time()
        batch_a = []
        while self.queue_a and self.queue_a[0][0] <= now:
            batch_a.append(heapq.heappop(self.queue_a))

        (batch_b, self.queue_b,) = (self.queue_b, [])
        batch_a.extend(batch_b)
        for (when, what,) in batch_a:
            try:
                what()
            except Exception:
                self.handle_exception(sys.exc_info())

        return len(batch_a)



    @property
    def is_due(self):
        when = self.next_time()
        if when is not None:
            return when <= elapsed_time()



    def next_time(self):
        try:
            return self.queue_a[0][0]
        except IndexError:
            return None



    def handle_exception(self, exc_info):
        traceback.print_exception(*exc_info)




class MainLoop(object):

    def __init__(self):
        self.max_wait_time = 1.0
        self.running = True
        self.break_wait = False



    def get_wait_time(self, time):
        delay = self.max_wait_time
        next_event = event_queue.next_time()
        if next_event:
            delay = min(delay, next_event - time)
            delay = max(delay, 0.0)
        return delay



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
        event_queue.pump()



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
        c = stackless.channel()
        set_channel_pref(c)

        def wakeup():
            if c.balance:
                c.send(None)


        event_queue.push_after(wakeup, delay)
        c.receive()




class SLIOMainLoop(MainLoop):

    def wait(self, delay):
        stacklessio.wait(delay)
        stacklessio.dispatch()



    def interrupt_wait(self):
        stacklessio.break_wait()




def sleep(delay):
    c = stackless.channel()
    set_channel_pref(c)

    def wakeup():
        if c.balance:
            c.send(None)


    event_queue.push_after(wakeup, delay)
    c.receive()


event_queue = EventQueue()
if stacklessio:
    mainloop = SLIOMainLoop()
else:
    mainloop = MainLoop()

