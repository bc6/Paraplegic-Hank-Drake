#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cdsuc.py
import types
import inspect
import itertools

class EnumList(object):

    def __init__(self, *data):
        __data = {}
        for each in iter(data):
            if type(each) in types.StringTypes:
                val = intern(each.lower())
                __data[val] = val
                self.__dict__[val.upper()] = val

        self.__data = __data

    def __getattr__(self, name):
        lname = str(name).lower()
        val = self.__data.get(lname, None)
        if val:
            return val
        raise AttributeError, name

    def __iter__(self):
        for each in self.__data:
            yield each

    def __add__(self, other):
        l = list(itertools.chain(self, other))
        return EnumList(*l)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return itertools.ifilter(lambda x: x not in iter(other), self)

    def __str__(self):
        sortedUpperCaseKeys = map(lambda x: x.upper(), self.__data.keys())
        sortedUpperCaseKeys.sort()
        return ', '.join(sortedUpperCaseKeys)


class SpyMixin(object):

    def SetWatchAttributes(self, *args):
        object.__setattr__(self, 'attributesUnderWatch', [])
        for arg in args:
            self.attributesUnderWatch.append(arg)

    def __setattr__(self, name, value):
        if not hasattr(self, 'attributesUnderWatch'):
            object.__setattr__(self, 'attributesUnderWatch', [])
        if name in self.attributesUnderWatch:
            print 'Setting %s to value %s' % (name, repr(value))
        object.__setattr__(self, name, value)