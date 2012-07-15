#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/sys/row.py
import blue
import types
import sys

class Row:
    __guid__ = 'util.Row'
    __passbyvalue__ = 1

    def __init__(self, header = None, line = None):
        self.__dict__['header'] = header or []
        self.__dict__['line'] = line or []

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __getattr__(self, name):
        try:
            return self.__dict__['line'][self.__dict__['header'].index(name)]
        except ValueError:
            raise AttributeError, name
        except KeyError:
            raise AttributeError, name

    def __getitem__(self, i):
        if type(i) == types.StringType:
            return getattr(self, i)
        return self.line[i]

    def __setitem__(self, key, value):
        if type(key) == types.StringType:
            return setattr(self, key, value)
        self.line[key] = value

    def __setattr__(self, key, value):
        if key == 'header':
            self.__dict__['header'] = value
        elif key == 'line':
            self.__dict__['line'] = value
        else:
            try:
                self.line[self.header.index(key)] = value
            except ValueError:
                self.__dict__[key] = value
                sys.exc_clear()

    def __repr__(self):
        header = self.__dict__['header']
        line = self.__dict__['line']
        if len(header) > len(line):
            return '<Row MANGLED ROW,%s,%r>' % (header, line)
        ret = '<Row '
        for i in range(len(header)):
            ret += '%s:%r,' % (header[i], line[i])

        return ret[:-1] + '>'

    def __len__(self):
        return len(self.__dict__['line'])

    def __getslice__(self, i, j):
        return self.__class__(self.header[i:j], self.line[i:j])

    def __cmp__(self, other):
        if type(other) != types.InstanceType:
            return -1
        elif self.header != other.header:
            return cmp(self.header, other.header)
        else:
            return cmp(self.line, other.line)