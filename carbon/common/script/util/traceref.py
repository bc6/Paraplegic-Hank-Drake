import gc
import inspect
import sys
import types
import stackless
import blue
import util

def ObjectHistogram(deltaFrom = {}):
    hist = {}
    for obj in gc.get_objects():
        try:
            objType = ClassOrType(obj)
        except ReferenceError:
            continue
        hist[objType] = hist.get(objType, 0) + 1

    for objType in set(hist).union(deltaFrom):
        hist[objType] = hist.get(objType, 0) - deltaFrom.get(objType, 0)

    report = _SortList([ (count, (objType, count)) for (objType, count,) in hist.iteritems() ])
    report.reverse()
    print 'Histogram BEGIN -----------------------------------'
    if deltaFrom:
        print '(Delta from previous.)'
    print '%s%20s' % ('Type', 'Count')
    for (objType, count,) in report:
        if count != 0:
            print '%s%20s' % (objType, count)

    print 'Histogram END -------------------------------------'
    return hist



def GetLiveObjectsByTypeName(typeName):
    ret = []
    for obj in gc.get_objects():
        try:
            if typeName in ClassOrType(obj).__name__:
                ret.append(obj)
        except ReferenceError:
            pass

    return ret



def GetLiveObjectsByType(type_):
    return [ obj for obj in gc.get_objects() if isinstance(obj, type_) ]



def _RawRefGraph(ob, ignore = (), depthLimit = None, breadthLimit = None):

    def Ignore(*obs):
        for ob in obs:
            ignored.add(id(ob))




    def IgnoreFrame(f):
        Ignore(f, f.f_locals)



    def IgnoreCallStack():
        f = inspect.currentframe()
        while f is not None:
            IgnoreFrame(f)
            f = f.f_back




    def Graph(ob, depth = 0):
        blue.pyos.BeNice()
        if depthLimit is not None and depth > depthLimit:
            return 
        IgnoreCallStack()
        ret[id(ob)] = rfrs = []
        l = gc.get_referrers(ob)
        Ignore(rfrs, l)
        breadth = 0
        for rfr in l:
            if id(rfr) not in ignored:
                breadth += 1
                if breadthLimit is not None and breadth > breadthLimit:
                    return 
                rfrs.append(rfr)
                if id(rfr) not in ret:
                    for type_ in [stackless.module,
                     stackless.modict,
                     stackless.frame,
                     stackless.function,
                     stackless.listiterator]:
                        if isinstance(rfr, type_):
                            break
                    else:
                        Graph(rfr, depth + 1)




    ret = {}
    ignored = set()
    Ignore(ret, ignored, sys.modules['__main__'].__dict__, *ignore)
    IgnoreFrame(inspect.currentframe())
    Graph(ob)
    return ret



def TestRawRefGraph():

    class A:
        pass
    o = A()
    d = {'a si': a}
    a.dd = d
    import pprint
    pprint.pprint(_RawRefGraph(a))



def TestAnnotatedRefGraph(verbose = False):

    def ImportHack(name):
        return sys.modules.setdefault(name, types.ModuleType(name))


    foo = ImportHack('foo')
    bar = ImportHack('bar')

    class Blah:
        pass
    o = Blah()
    foo.o = o
    foo.alias = o
    o.self = o
    p = bar.p = Blah()
    p.oo = p.oOo = o
    l = foo.l = [o, 'blah', o]
    t = foo.t = (o, 'bleh', o)
    d = bar.d = {'o si': o,
     'o si also': o}
    q = Blah()
    q.o = o
    m = [o]
    u = (o,)
    e = {'o': o}
    die = False

    def f():
        b = o
        while not die:
            blue.pyos.synchro.SleepWallclock(0)



    import uthread
    uthread.new(f)
    blue.pyos.synchro.SleepWallclock(0)
    try:
        PrintRefPaths(o, verbose=verbose)

    finally:
        die = True




def PrintRefPaths(obj, ignore = (), verbose = False, depthLimit = None, breadthLimit = None):

    class loop:
        pass

    def PathsFromRef(ref, prevPath = []):
        newPath = prevPath + [ref]
        if ref.refs:
            ret = []
            for ref in ref.refs:
                blue.pyos.BeNice()
                if ref in newPath:
                    ret.append([ref, loop])
                else:
                    for path in PathsFromRef(ref, newPath):
                        ret.append([ref] + path)


            return ret
        else:
            return [[]]



    def PathStr(path):
        rev = path
        rev.reverse()
        if rev[0] is loop:
            prefix = ['(CYCLE)']
            rev = rev[1:]
        else:
            root = rev[0].obj
            if isinstance(root, stackless.frame) or isinstance(root, stackless.function):
                prefix = []
            elif isinstance(root, stackless.module):
                prefix = [root.__name__]
            elif isinstance(root, stackless.modict):
                prefix = [root.__module__]
            else:
                prefix = ['<%s at %x>' % (ClassOrType(root).__name__, id(root))]
        if verbose:

            def fn(ref):
                if ClassOrType(ref.obj) in (list,
                 tuple,
                 dict,
                 stackless.frame):
                    return ref.expr()
                else:
                    typeName = getattr(ref.obj, '__guid__', ClassOrType(ref.obj).__name__)
                    return '(%s)%s' % (typeName, ref.expr())


        else:
            fn = lambda ref: ref.expr()
        return ''.join(prefix + [ fn(each) for each in rev ])


    refs = _AnnotatedRefGraph(obj, ignore, depthLimit, breadthLimit)
    allPaths = []
    for ref in refs:
        allPaths.extend([ [ref] + path for path in PathsFromRef(ref) ])

    pathStrs = map(PathStr, allPaths)
    pathStrs.sort()
    print 'Paths are (in alphabetical order):'
    for each in pathStrs:
        print '   ',
        print each

    del allPaths[:]
    allPurged = set()

    def PurgeRef(ref):
        if id(ref) in allPurged:
            return 
        allPurged.add(id(ref))
        map(PurgeRef, ref.refs)
        del ref.refs[:]


    map(PurgeRef, refs)



def _AnnotatedRefGraph(obj, ignore = (), depthLimit = None, breadthLimit = None):
    handledAnnotations = {}
    handledIndices = set()

    def IndexHandled(obID, refID, categ, index):
        ret = (obID,
         refID,
         categ,
         index) in handledIndices
        handledIndices.add((obID,
         refID,
         categ,
         index))
        handledIndices.add((obID,
         refID,
         'unknown',
         None))
        return ret



    class Ref:

        def __init__(self, obj, categ, index):
            self.obj = obj
            self.categ = categ
            self.index = index
            self.refs = handledAnnotations[id(obj)]



        def __str__(self):
            return 'Ref(%s, %s, <%s at %x>)' % (self.categ,
             self.index,
             ClassOrType(self.obj).__name__,
             id(self.obj))



        def expr(self):
            if self.categ == 'frame_local':
                return "<local '%s' at %s:%s(%s)>" % (self.index,
                 self.obj.f_code.co_filename,
                 self.obj.f_code.co_firstlineno,
                 self.obj.f_code.co_name)
            else:
                if self.categ == 'func_closure':
                    return '<closed over at %s:%s(%s)>' % (self.obj.func_code.co_filename, self.obj.func_code.co_firstlineno, self.obj.func_name)
                if self.categ == 'attr':
                    return '.%s' % self.index
                if self.categ in ('seq', 'dict'):
                    return '[%r]' % self.index
                return '<%s>' % self



    handledAnnotations[id(None)] = []
    omitted = Ref(None, 'omitted', None)

    def FrameDetails(obj, rfr):
        if not isinstance(rfr, stackless.frame):
            return None
        for (name, val,) in rfr.f_locals.iteritems():
            if val is obj and not IndexHandled(id(obj), id(rfr), 'frame_local', name):
                return (rfr, 'frame_local', name)




    def FuncDetails(obj, rfr):
        for rfrfr in GetRefs(rfr):
            if isinstance(rfrfr, stackless.function):
                for (name, val,) in rfrfr.func_dict.iteritems():
                    if val is obj and not IndexHandled(id(obj), id(rfrfr), 'func_dict', name):
                        return (rfrfr, 'func_dict', i)

            elif isinstance(rfr, stackless.cell):
                for rfrfrfr in GetRefs(rfrfr):
                    if isinstance(rfrfrfr, stackless.function):
                        for (i, cell,) in enumerate(rfrfrfr.func_closure or ()):
                            if cell is rfr and not IndexHandled(id(obj), id(rfrfrfr), 'func_closure', i):
                                IndexHandled(id(obj), id(rfr), 'seq', i)
                                return (rfrfrfr, 'func_closure', i)






    def AttrDetails(obj, rfr):
        if isinstance(rfr, stackless.modict):
            ret = DictDetails(obj, rfr)
            if ret is not None:
                (rfr, categ, index,) = ret
                return (rfr, 'attr', index)
        for rfrfr in GetRefs(rfr):
            for name in dir(rfrfr):
                try:
                    if getattr(rfrfr, name, None) is obj and not IndexHandled(id(obj), id(rfr), 'dict', name):
                        return (rfrfr, 'attr', name)
                except TypeError:
                    sys.exc_clear()





    def DictDetails(obj, rfr):
        if not hasattr(rfr, 'iteritems'):
            return None
        for (key, val,) in rfr.iteritems():
            if val is obj and not IndexHandled(id(obj), id(rfr), 'dict', key):
                return (rfr, 'dict', key)




    def SequenceDetails(obj, rfr):
        try:
            for (i, val,) in enumerate(rfr):
                if val is obj and not IndexHandled(id(obj), id(rfr), 'seq', i):
                    return (rfr, 'seq', i)

        except TypeError:
            try:
                enumerate(rfr)
            except TypeError:
                sys.exc_clear()
                return None
            raise 



    def UnknownDetails(obj, rfr):
        if not IndexHandled(id(obj), id(rfr), 'unknown', None):
            return (rfr, 'unknown', None)



    def NextAnnotation(obj, rfr):
        for func in [FrameDetails,
         FuncDetails,
         AttrDetails,
         DictDetails,
         SequenceDetails,
         UnknownDetails]:
            ref = func(obj, rfr)
            if ref is not None:
                return ref




    def AnnotateRefs(obj):
        ret = []
        handledAnnotations[id(obj)] = []
        for rfr in GetRefs(obj):
            while True:
                next = NextAnnotation(obj, rfr)
                if next is None:
                    break
                (ostensibleRfr, categ, index,) = next
                if id(ostensibleRfr) not in handledAnnotations:
                    AnnotateRefs(ostensibleRfr)
                ret.append(Ref(ostensibleRfr, categ, index))


        handledAnnotations[id(obj)].extend(ret)
        return ret


    raw = _RawRefGraph(obj, ignore, depthLimit, breadthLimit)

    def GetRefs(obj):
        return raw.get(id(obj), [])


    try:
        return AnnotateRefs(obj)

    finally:
        raw.clear()




def ClassOrType(obj):
    return getattr(obj, '__class__', type(obj))



def _SortList(lst):
    lst.sort()
    return [ item[1] for item in lst ]


exports = util.AutoExports('util', locals())

