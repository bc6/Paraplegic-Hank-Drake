import time

class MethodTimeEntry(object):

    def __init__(self):
        self.count = 0
        self.total = 0
        self.min = 1000000000.0
        self.max = -1000000000.0




class PythonTimer(object):
    _PythonTimer__shared_state = {}

    def __init__(self):
        self.__dict__ = self._PythonTimer__shared_state
        if not hasattr(self, 'methodTimes'):
            self.methodTimes = {}



    def ClearTimings(self):
        self.methodTimes.clear()



    def PrintTimings(self):
        maxSortOrder = {}
        for each in self.methodTimes:
            maxSortOrder[each] = self.methodTimes[each].max

        maxSortOrder = maxSortOrder.items()
        maxSortOrder.sort(key=lambda x: x[1], reverse=True)
        print 'Function\tCalled\tTotaltime\tavg\tmin\tmax'
        for t in maxSortOrder:
            each = t[0]
            entry = self.methodTimes[each]
            print '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(each, entry.count, entry.total, entry.total / entry.count, entry.min, entry.max)




    def timeit(self, method):

        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            delta = te - ts
            entry = self.methodTimes.get(method.__name__, MethodTimeEntry())
            entry.count += 1
            entry.total += delta
            entry.min = min(entry.min, delta)
            entry.max = max(entry.max, delta)
            self.methodTimes[method.__name__] = entry
            return result


        return timed




