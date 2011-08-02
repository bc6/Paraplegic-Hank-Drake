import types
import blue
import weakref
import sys
try:
    import gc
except:
    gc = 'no gc availible'
    sys.exc_clear()

def GetBlueObjects(typeName = None):
    r = []
    for o in gc.get_objects():
        if type(o) != blue.BlueWrapper:
            continue
        if not typeName or typeName == o.__bluetype__:
            r.append(o)

    r.sort(lambda a, b: cmp(id(a), id(b)))
    return r



class ActiveBlueObjects(object):

    def __init__(self, name):
        self.name = name
        self.dict = weakref.WeakKeyDictionary()
        self.count = 0
        self.Update()



    def Update(self):
        r = weakref.WeakKeyDictionary()
        for o in GetBlueObjects(self.name):
            if o not in self.dict:
                r[o] = None
                self.dict[o] = self.count

        self.count += 1
        return r




def RefTree(*args):
    depth = 3
    if len(args) > 1:
        depth = args[1]
    omit = IdSet()
    if len(args) > 2:
        for o in args[2:]:
            omit.Insert(o)

    return RefNode(args, depth, omit)



def RefLeaves(*args):
    depth = 3
    if len(args) > 1:
        depth = args[1]
    omit = IdSet()
    if len(args) > 2:
        for o in args[2:]:
            omit.Insert(o)

    leaves = []
    omit.Insert(leaves)
    RefNode(args, depth, omit, leaves=leaves)
    return leaves



class RefNode(object):

    def __init__(self, objtuple, depth = 3, omit = None, parent = None, leaves = None):
        if not omit:
            omit = IdSet()
        self.children = []
        if depth:
            depth = depth - 1
            omit.Insert(objtuple[0])
            referrers = gc.get_referrers(objtuple[0])
            omit.Insert(referrers)
            leaf = True
            for r in referrers:
                if r is objtuple or r in omit:
                    continue
                if type(r) is types.TupleType and r[0] is objtuple[0] and r[-1] is None:
                    continue
                tmp = (r,)
                r = None
                self.children.append(RefNode(tmp, depth, omit, objtuple[0], leaves))
                leaf = False
                del tmp

            if leaf and leaves is not None:
                leaves.append(objtuple[0])
            omit.Remove(referrers)
            del referrers
        how = self._RefNode__Link(objtuple[0], parent)
        if how:
            self.repr = '%s in %s' % (how, self._RefNode__Repr(objtuple[0]))
        else:
            self.repr = self._RefNode__Repr(objtuple[0])



    def __str__(self):
        return self.repr



    def Print(self, indent = 0):
        i = ' ' * indent * 4
        print i + str(self)
        indent = indent + 1
        for c in self.children:
            c.Print(indent)




    def String(self, indent = 0):
        i = ' ' * indent * 4
        l = [i + str(self)]
        indent = indent + 1
        for c in self.children:
            l.append(c.String(indent))

        return '\n'.join(l)



    def __Link(self, item, parent):
        t = type(item)
        import types
        if issubclass(t, types.DictType):
            for (k, v,) in item.iteritems():
                if v is parent:
                    return '[%s]' % repr(k)

            for k in item.iterkeys():
                if k is parent:
                    return 'key'

        elif t is types.ListType or t is types.TupleType:
            for i in xrange(len(item)):
                if item[i] is parent:
                    return '[%s]' % i




    def __Repr(self, object):
        t = type(object)
        if t in (types.ListType, types.TupleType, types.DictType):
            return '<%s object at %#x>' % (t.__name__, id(object))
        return repr(object)




class IdSet(object):

    def __init__(self):
        self.set = {}



    def Insert(self, obj):
        self.set[id(obj)] = True



    def Remove(self, obj):
        del self.set[id(obj)]



    def __contains__(self, obj):
        return self.set.has_key(id(obj))




def PrettyStr(obj, maxlen = 20, depth = -1, indent = 1, showid = 0, prune = 0):
    if prune:
        showid = 1
        omitset = IdSet()
    else:
        omitset = None
    return PPRecurse(obj, maxlen, depth, indent, showid, omitset)



def PrettyPrint(obj, maxlen = 20, depth = -1, indent = 1, showid = 0, prune = 0):
    gunk = PrettyStr(obj, maxlen, depth, indent, showid, prune)
    for line in gunk.split('\n'):
        print line




def PPRecurse(obj, maxlen, depth, indent, showid, omitset):
    objType = type(obj)
    if objType in [types.NoneType,
     types.IntType,
     types.LongType,
     types.FloatType,
     types.StringType,
     types.ComplexType,
     types.UnicodeType]:
        return repr(obj)
    if (depth > 0 or depth < 0) and objType in [types.TupleType,
     types.ListType,
     types.DictType,
     types.InstanceType]:
        depth = depth - 1
        truncate = 0
        if objType in [types.TupleType, types.ListType, types.DictType]:
            length = len(obj)
            if maxlen >= 0 and length > maxlen:
                truncate = 1
                length = maxlen
            if objType != types.DictType:
                vals = obj[:length]
                keys = None
                if objType == types.TupleType:
                    head = '('
                    tail = ')'
                else:
                    head = '['
                tail = ']'
            else:
                it = obj.items()
                it.sort()
            keys = [ repr(key) + ' : ' for (key, val,) in it[:length] ]
            vals = [ val for (key, val,) in it[:length] ]
            head = '{'
            tail = '}'
        else:
            keys = [ key for key in dir(obj) if key.find('__') != 0 if type(getattr(obj, key)) != types.MethodType ]
            length = len(keys)
            if maxlen >= 0 and length > maxlen:
                truncate = 1
                length = maxlen
            vals = [ getattr(obj, key) for key in keys ]
            keys = [ repr(key) + ' = ' for key in keys ]
            head = '<inst of %s: ' % obj.__class__.__name__
            tail = '>'
        if showid:
            head += '(id %s)' % id(obj)
        if omitset is not None:
            if obj in omitset:
                return head + '*skipped*' + tail
            omitset.insert(obj)
        if depth == 0:
            indent = 0
        return PPAssemble(head, keys, vals, tail, truncate, maxlen, depth, indent, showid, omitset)
    if showid:
        ids = '(id %s) ' % id(obj)
    else:
        ids = ''
    if objType == types.InstanceType:
        return '<%sinst of class %s>' % (ids, obj.__class__.__name__)
    if objType == types.ClassType:
        return '<class %s>' % obj.__name__
    if objType == types.ModuleType:
        return '<module %s>' % obj.__name__
    return '<%s%s>' % (ids, repr(objType))



def PPAssemble(head, prefixes, values, tail, ellipsis, maxlen, depth, indent, showid, omitset):
    lines = []
    for i in range(len(values)):
        if prefixes:
            line = prefixes[i]
        else:
            line = ''
        line += PPRecurse(values[i], maxlen, depth, indent, showid, omitset)
        lines.append(line)

    if ellipsis:
        lines.append('...')
    if indent:
        bulk = PPIndent(',\n'.join(lines))
        result = '\n'.join([head, bulk, tail])
    else:
        result = head + ', '.join(lines) + tail
    return result



def PPIndent(text, nIndents = 1):
    return '\n'.join([ '\t' * nIndents + line for line in text.split('\n') ])



def PPIndentRest(text, nIndents = 1):
    lines = text.split('\n')
    return '\n'.join([lines[0]] + [ '\t' * nIndents + line for line in lines[1:] ])


exports = {'reftree.RefTree': RefTree,
 'reftree.RefLeaves': RefLeaves,
 'reftree.PrettyPrint': PrettyPrint,
 'reftree.PrettyStr': PrettyStr,
 'reftree.GetBlueObjects': GetBlueObjects,
 'reftree.ActiveBlueObjects': ActiveBlueObjects}

