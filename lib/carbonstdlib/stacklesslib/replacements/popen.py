import os
import sys
import threading
import stackless
try:
    threading = threading.realthreading
except AttributeError:
    pass

class FileReadMixin(object):

    def __iter__(self):
        if self.closed:
            raise IOError, 'iter operation on a closed file'
        return self



    def next(self):
        r = self.readline()
        if r:
            return r
        raise StopIteration



    def readlines(self, sizehint = None):
        return list(self)




class FileChannel(stackless.channel, FileReadMixin):

    def __init__(self):
        self.buffer = ['']
        self.eof = False



    def read(self, size = -1):
        try:
            return self._read(size)
        except:
            import traceback
            traceback.print_exc()
            raise 



    def _read(self, size = -1):
        if size < 0:
            while not self.eof:
                r = self.receive()
                if r is None:
                    self.eof = True
                else:
                    self.buffer.append(r)

            r = ''.join(self.buffer)
            self.buffer = ['']
            return r
        if len(self.buffer) > 1:
            self.buffer = [''.join(self.buffer)]
        if not self.buffer[0] and not self.eof:
            r = self.receive()
            if r is None:
                self.eof = True
            else:
                self.buffer.append(r)
        b = ''.join(self.buffer)
        r = b[:size]
        self.buffer = [b[size:]]
        return r



    def readline(self, size = -1):
        if size >= 0:
            r = self.read(size)
        else:
            stuff = []
            while True:
                b = self.read(512)
                stuff.append(b)
                if not b or '\n' in b:
                    break

            r = ''.join(stuff)
        where = r.find('\n')
        if r >= 0:
            result = r[:(where + 1)]
            self.buffer[0:0] = [r[(where + 1):]]
        else:
            result = r
        return result



if hasattr(os, 'popen4'):
    os_popen4 = os.popen4

    def popen4(cmd, mode = 't', bufsize = -1):
        (pstdin, pstdout,) = (FileChannel(), FileChannel())

        def func():
            try:
                try:
                    (fstdin, fstdout,) = os_popen4(cmd, mode, bufsize)
                    try:
                        for l in fstdout:
                            pstdout.send(l)


                    finally:
                        fstdout.close()

                except Exception:
                    (c, e,) = sys.exc_info()[:2]
                    pstdout.send_exception(c, e)

            finally:
                pstdout.send(None)



        t = threading.Thread(target=func)
        t.start()
        return (pstdin, pstdout)



