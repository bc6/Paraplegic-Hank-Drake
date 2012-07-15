#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\iterio.py
try:
    from py.magic import greenlet
except:
    greenlet = None

class IterIO(object):

    def __new__(cls, obj):
        try:
            iterator = iter(obj)
        except TypeError:
            return IterI(obj)

        return IterO(iterator)

    def __iter__(self):
        return self

    def tell(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        return self.pos

    def isatty(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        return False

    def seek(self, pos, mode = 0):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def truncate(self, size = None):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def write(self, s):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def writelines(self, list):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def read(self, n = -1):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def readlines(self, sizehint = 0):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def readline(self, length = None):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def flush(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        raise IOError(9, 'Bad file descriptor')

    def next(self):
        if self.closed:
            raise StopIteration()
        line = self.readline()
        if not line:
            raise StopIteration()
        return line


class IterI(IterIO):

    def __new__(cls, func):
        if greenlet is None:
            raise RuntimeError('IterI requires greenlet support')
        stream = object.__new__(cls)
        stream.__init__(greenlet.getcurrent())

        def run():
            func(stream)
            stream.flush()

        g = greenlet(run, stream._parent)
        while 1:
            rv = g.switch()
            if not rv:
                return
            yield rv[0]

    def __init__(self, parent):
        self._parent = parent
        self._buffer = []
        self.closed = False
        self.pos = 0

    def close(self):
        if not self.closed:
            self.closed = True

    def write(self, s):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        self.pos += len(s)
        self._buffer.append(s)

    def writelines(self, list):
        self.write(''.join(list))

    def flush(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        data = ''.join(self._buffer)
        self._buffer = []
        self._parent.switch((data,))


class IterO(IterIO):

    def __new__(cls, gen):
        return object.__new__(cls)

    def __init__(self, gen):
        self._gen = gen
        self._buf = ''
        self.closed = False
        self.pos = 0

    def __iter__(self):
        return self

    def close(self):
        if not self.closed:
            self.closed = True
            if hasattr(self._gen, 'close'):
                self._gen.close()

    def seek(self, pos, mode = 0):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if mode == 1:
            pos += self.pos
        else:
            if mode == 2:
                self.read()
                self.pos = min(self.pos, self.pos + pos)
                return
            if mode != 0:
                raise IOError('Invalid argument')
        buf = []
        try:
            tmp_end_pos = len(self._buf)
            while pos > tmp_end_pos:
                item = self._gen.next()
                tmp_end_pos += len(item)
                buf.append(item)

        except StopIteration:
            pass

        if buf:
            self._buf += ''.join(buf)
        self.pos = max(0, pos)

    def read(self, n = -1):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if n < 0:
            self._buf += ''.join(self._gen)
            result = self._buf[self.pos:]
            self.pos += len(result)
            return result
        new_pos = self.pos + n
        buf = []
        try:
            tmp_end_pos = len(self._buf)
            while new_pos > tmp_end_pos:
                item = self._gen.next()
                tmp_end_pos += len(item)
                buf.append(item)

        except StopIteration:
            pass

        if buf:
            self._buf += ''.join(buf)
        new_pos = max(0, new_pos)
        try:
            return self._buf[self.pos:new_pos]
        finally:
            self.pos = min(new_pos, len(self._buf))

    def readline(self, length = None):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        nl_pos = self._buf.find('\n', self.pos)
        buf = []
        try:
            pos = self.pos
            while nl_pos < 0:
                item = self._gen.next()
                local_pos = item.find('\n')
                buf.append(item)
                if local_pos >= 0:
                    nl_pos = pos + local_pos
                    break
                pos += len(item)

        except StopIteration:
            pass

        if buf:
            self._buf += ''.join(buf)
        if nl_pos < 0:
            new_pos = len(self._buf)
        else:
            new_pos = nl_pos + 1
        if length is not None and self.pos + length < new_pos:
            new_pos = self.pos + length
        try:
            return self._buf[self.pos:new_pos]
        finally:
            self.pos = min(new_pos, len(self._buf))

    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()

        return lines