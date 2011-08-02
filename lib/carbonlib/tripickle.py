import copy_reg
import blue
reducers = {}
constructors = {}

def RegisterReducer(typename, reducer):
    reducers[typename] = reducer



def RegisterConstructor(typename, constructor):
    constructors[typename] = constructor



def ConstructBlueObject(blueObClass, args):
    if constructors.has_key(blueObClass):
        return apply(constructors[blueObClass], args)
    else:
        memStream = blue.os.CreateInstance('blue.MemStream')
        buff = args
        memStream.Write(buff)
        memStream.Seek(0)
        rot = blue.os.CreateInstance('blue.Rot')
        return rot.GetCopy(memStream)



def ReduceBlueObject(ob):
    blueObClass = ob.__typename__
    if reducers.has_key(blueObClass):
        return (ConstructBlueObject, (blueObClass,) + (reducers[blueObClass](ob),))
    else:
        ret = blue.os.CreateInstance('blue.MemStream')
        ob.SaveTo(ret)
        ret.Seek(0)
        return (ConstructBlueObject, (blueObClass,) + (str(ret.Read(ret.size)),))



def ReduceTriVector(vec):
    return (vec.x, vec.y, vec.z)


RegisterReducer('TriVector', ReduceTriVector)

def ReduceTriQuaternion(q):
    return (q.x,
     q.y,
     q.z,
     q.w)


RegisterReducer('TriQuaternion', ReduceTriQuaternion)
try:
    import blue
    test = blue.os.CreateInstance('trinity.')
except:
    pass
import trinity
RegisterConstructor('TriVector', trinity.TriVector)
RegisterConstructor('TriQuaternion', trinity.TriQuaternion)
copy_reg.pickle(type(blue.os), ReduceBlueObject, ConstructBlueObject)

