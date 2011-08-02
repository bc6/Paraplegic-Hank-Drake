import pstats
import sys
import types
import log
import cProfile
import util
from functools import wraps

def Trace(fn):

    @wraps(fn)
    def deco(*args, **kw):
        no_ret = []

        def logStuff(beginOrEnd, ret = no_ret):
            if not settings.generic.Get('logDbgTrace', False):
                return 
            if args and hasattr(args[0], '__guid__'):
                meth = '.'.join((args[0].__guid__, fn.func_name))
                rest = args[1:]
            else:
                meth = fn.func_name
                rest = args
            spos = map(Prettify, rest)
            skw = [ '%s=%s' % (name, Prettify(val)) for (name, val,) in kw.iteritems() ]
            sargs = ', '.join(spos + skw)
            if ret is no_ret:
                sret = ''
            else:
                sret = ' -> %s' % Prettify(ret)
            import dbg
            me = dbg.GetCharacterName()
            what = (beginOrEnd, me + ':', '%s(%s)%s' % (meth, sargs, sret))
            log.methodcalls.Log(' '.join(map(unicode, what)), log.LGNOTICE)


        logStuff('BEGIN')
        ret = fn(*args, **kw)
        logStuff('END', ret)
        return ret


    return deco



def TraceAll(locals, ignore = ()):
    for (name, val,) in locals.items():
        if name not in ignore and callable(val):
            locals[name] = Trace(val)




def Prettify(o):
    if isinstance(o, util.KeyVal) and getattr(o, 'charID', None) is not None:
        import dbg
        name = dbg.GetCharacterName(o)
        return name
    else:
        if hasattr(o, 'name') and hasattr(o, '__guid__'):
            return '%s (%s)' % (o.name, o.__guid__)
        return str(o)



def ImportHack(name):
    return sys.modules.setdefault(name, types.ModuleType(name))



def TraceLocals(locals, *varnames):

    def Eval(expr):
        try:
            return eval(expr, {}, locals)
        except:
            (excType, exc,) = sys.exc_info()[:2]
            return '<exception: %s%s>' % (excType.__name__, exc.args)


    log.methodcalls.Log(' '.join(map(unicode, [ '%s=%r' % (name, Eval(name)) for name in varnames ])), log.LGNOTICE)



def WithLogStdout(f):
    if not hasattr(WithLogStdout, 'logStream'):
        WithLogStdout.logStream = log.LogChannelStream(log.methodcalls, log.LGNOTICE)

    @wraps(f)
    def deco(*args, **kw):
        old = sys.stdout
        sys.stdout = WithLogStdout.logStream
        try:
            return f(*args, **kw)

        finally:
            sys.stdout = old



    return deco



@WithLogStdout
def Profile(fn, *args, **kw):
    print 'Profile BEGIN -----------------------------------'
    p = cProfile.Profile()
    ret = p.runcall(fn, *args, **kw)
    pstats.Stats(p).sort_stats('time', 'cumulative').print_stats()
    print 'Profile END -------------------------------------'
    return ret



def Profiled(fn):

    @wraps(fn)
    def deco(*args, **kw):
        return Profile(fn, *args, **kw)


    return deco


exports = util.AutoExports('dbg', locals())

