import os
import blue
import stackless
import sys
import types
import util
import uthread
import log
import yaml

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



def ResFileToCache(respath):
    try:
        filename = respath[(respath.rfind('/') + 1):]
        targetName = blue.os.ResolvePath(u'cache:/Temp/') + filename
        if not os.path.exists(targetName):
            resFile = blue.ResFile()
            resFile.Open(respath)
            rawData = resFile.read()
            resFile.close()
            outImage = file(targetName, 'wb')
            outImage.writelines(rawData)
            outImage.close()
        return targetName
    except:
        sys.exc_clear()
        return ''



def BlueFile(bluefilename, mode = 'r', bufsize = -1):
    filename = blue.rot.PathToFilename(bluefilename)
    try:
        f = file(filename, mode, bufsize)
    except IOError:
        f = ResFile(bluefilename, mode, bufsize)
        sys.exc_clear()
    return f



def DelTree(path):

    def DelFiles(arg, dirname, fnames):
        for each in fnames:
            tmp = os.path.join(dirname, each)
            if not os.path.isdir(tmp):
                os.remove(tmp)



    os.path.walk(path, DelFiles, None)
    _RemoveDirs(path, 0)



def _RemoveDirs(path, nukebase):
    for each in os.listdir(path):
        _RemoveDirs(os.path.join(path, each), 1)

    if nukebase:
        os.rmdir(path)



def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return 

    return obj



def HasAttrs(obj, *names):
    for name in names:
        if not hasattr(obj, name):
            return False
        obj = getattr(obj, name, None)

    return True



def TryDel(dictOrSet, key):
    try:
        if isinstance(dictOrSet, set):
            dictOrSet.remove(key)
        else:
            del dictOrSet[key]
    except KeyError:
        sys.exc_clear()



def SecsFromBlueTimeDelta(t):
    return t / 10000000L



def HoursMinsSecsFromSecs(s):
    s = max(0, s)
    secs = int(s % 60)
    mins = int(s / 60 % 60)
    hours = int(s / 3600)
    return (hours, mins, secs)



def Clamp(val, min_, max_):
    return min(max_, max(min_, val))



def Doppleganger(wrap, original):
    return types.FunctionType(wrap.func_code, wrap.func_globals, original.func_name, closure=wrap.func_closure)



def Decorator(f):

    def deco(inner, *args, **kw):
        return Doppleganger(f(inner, *args, **kw), inner)


    return deco


Decorator = Decorator(Decorator)

def Uthreaded(f, name = None):
    if name is None:
        name = f.__name__

    def deco(*args, **kw):
        uthread.worker(name, lambda : f(*args, **kw))


    return deco


Uthreaded = Decorator(Uthreaded)

def RunOnceMethod(fn):
    runAlreadyName = '_run%s%sAlready' % (fn.__name__, id(fn))

    def deco(self, *args, **kw):
        if not hasattr(self, runAlreadyName):
            setattr(self, runAlreadyName, True)
            fn(self, *args, **kw)


    return deco



class Despammer:
    ___guid__ = 'util.Despammer'

    def __init__(self, fn, delay = 0):
        self._fn = fn
        self._delay = delay
        self._channel = stackless.channel()
        uthread.worker('Despammed::%s' % self._fn.__name__, self._Receiver)
        self._running = True



    def Send(self, *args, **kw):
        if self._running:
            self._channel.send((args, kw))


    Send = Uthreaded(Send)

    def Stop(self):
        if self._running:
            self._running = False
            self._channel.send_exception(self._StopExc)
            del self._channel
            del self._fn



    class _StopExc(Exception):
        pass

    def _Receiver(self):
        ch = self._channel
        while True:
            try:
                (args, kw,) = ch.receive()
                blue.pyos.synchro.SleepWallclock(self._delay)
                while ch.balance != 0:
                    (args, kw,) = ch.receive()

                self._fn(*args, **kw)
            except self._StopExc:
                sys.exc_clear()
                return 
            except Exception:
                log.LogException()
                sys.exc_clear()





def ReadYamlFile(path):
    data = None
    rf = blue.ResFile()
    if rf.FileExists(path):
        rf.Open(path)
        yamlStr = rf.read()
        rf.close()
        data = yaml.load(yamlStr)
    return data


exports = util.AutoExports('util', globals())

