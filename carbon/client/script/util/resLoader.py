import blue
import util

class _ResFileRaw(object):
    __slots__ = ['resfile', 'closed']

    def __init__(self, respath):
        self.resfile = blue.ResFile()
        self.resfile.OpenAlways(respath)
        self.closed = False



    def read(self, size = -1):
        if self.closed:
            raise ValueError('file is closed')
        return self.resfile.Read(size)



    def seek(self, offset, whence = 0):
        if whence == 0:
            r = self.resfile.Seek(offset)
        elif whence == 1:
            r = self.resfile.Seek(offset + self.file.pos)
        elif whence == -1:
            r = self.resfile.Seek(self.file.size - offset)
        else:
            raise ValueError("'whence' must be 0, 1 or -1, not %s" % whence)



    def tell(self):
        return self.resfile.pos



    def close(self):
        if not self.closed:
            self.resfile.Close()
        self.closed = True




def ResFile(respath, mode = 'rb', bufsize = -1):
    if mode.count('b'):
        return _ResFileRaw(respath)
    else:
        s = _ResFileRaw(respath).read().replace('\r\n', '\n')
        import StringIO
        return StringIO.StringIO(s)


exports = util.AutoExports('util', globals())

