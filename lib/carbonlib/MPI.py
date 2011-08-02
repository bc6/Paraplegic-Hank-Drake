__docformat__ = 'reStructuredText'
__author__ = 'Lisandro Dalcin'
__credits__ = 'MPI Forum, MPICH Team, Open MPI Team.'
__date__ = '13 Oct 2006'
__version__ = '0.4.0'
__revision__ = '$Id: MPI.py 23 2007-02-24 00:18:19Z dalcinl $'
import mpilib
import _mpi
import _pickle
import _marshal
import _op

class Pickle(object):
    PROTOCOL = _pickle.HIGH_PROT
    dump = classmethod(_pickle.dump)
    load = classmethod(_pickle.load)

    def __new__(cls, *targs, **kargs):
        from types import MethodType as method
        pkl = object.__new__(cls)
        if cls is Pickle or 'dump' not in cls.__dict__:
            pkl.dump = method(_pickle.dump, pkl, cls)
        if cls is Pickle or 'load' not in cls.__dict__:
            pkl.load = method(_pickle.load, pkl, cls)
        return pkl



    def __init__(self, protocol = _pickle.HIGH_PROT):
        self.PROTOCOL = protocol




class Marshal(object):
    PROTOCOL = _marshal.VERSION
    dump = classmethod(_marshal.dump)
    load = classmethod(_marshal.load)

    def __new__(cls, *targs, **kargs):
        from types import MethodType as method
        msh = object.__new__(cls)
        if cls is Marshal or 'dump' not in cls.__dict__:
            msh.dump = method(_marshal.dump, msh, cls)
        if cls is Marshal or 'load' not in cls.__dict__:
            msh.load = method(_marshal.load, msh, cls)
        return msh



    def __init__(self, protocol = _marshal.VERSION):
        self.PROTOCOL = protocol




def Buffer(*args):
    data = None
    count = None
    datatype = BYTE
    if args:
        if len(args) == 1:
            (data,) = args
        if len(args) == 2:
            (data, datatype,) = args
        elif len(args) == 3:
            (data, count, datatype,) = args
        else:
            raise TypeError('Buffer() takes at most 3 arguments (%d given))' % (len(args) + 1))
    return (data, count, datatype)


UNDEFINED = _mpi.UNDEFINED
PROC_NULL = _mpi.PROC_NULL
ANY_SOURCE = _mpi.ANY_SOURCE
ROOT = _mpi.ROOT
ANY_TAG = _mpi.ANY_TAG
BSEND_OVERHEAD = _mpi.BSEND_OVERHEAD
BOTTOM = _mpi.BOTTOM
IN_PLACE = _mpi.IN_PLACE
CART = _mpi.CART
GRAPH = _mpi.GRAPH
IDENT = _mpi.IDENT
CONGRUENT = _mpi.CONGRUENT
SIMILAR = _mpi.SIMILAR
UNEQUAL = _mpi.UNEQUAL
ORDER_C = _mpi.ORDER_C
ORDER_FORTRAN = _mpi.ORDER_FORTRAN
DISTRIBUTE_NONE = _mpi.DISTRIBUTE_NONE
DISTRIBUTE_BLOCK = _mpi.DISTRIBUTE_BLOCK
DISTRIBUTE_CYCLIC = _mpi.DISTRIBUTE_CYCLIC
DISTRIBUTE_DFLT_DARG = _mpi.DISTRIBUTE_DFLT_DARG

class Datatype(_mpi.Datatype):

    def __init__(self, datatype = None):
        _mpi.Datatype.__init__(self, datatype)



    def Get_extent(self):
        return _mpi.type_get_extent(self)



    def Get_size(self):
        return _mpi.type_size(self)



    def Dup(self):
        newtype = _mpi.type_dup(self)
        return type(self)(newtype)



    def Create_contiguous(self, count):
        newtype = _mpi.type_contiguous(count, self)
        return type(self)(newtype)



    def Create_vector(self, count, blocklength, stride):
        newtype = _mpi.type_vector(count, blocklength, stride, self)
        return type(self)(newtype)



    def Create_hvector(self, count, blocklength, stride):
        newtype = _mpi.type_hvector(count, blocklength, stride, self)
        return type(self)(newtype)



    def Create_indexed(self, blocklengths, displacements):
        newtype = _mpi.type_indexed(blocklengths, displacements, self)
        return type(self)(newtype)



    def Create_indexed_block(self, blocklength, displacements):
        newtype = _mpi.type_indexed_block(blocklength, displacements, self)
        return type(self)(newtype)



    def Create_hindexed(self, blocklengths, displacements):
        newtype = _mpi.type_hindexed(blocklengths, displacements, self)
        return type(self)(newtype)



    def Create_subarray(self, sizes, subsizes, starts, order = None):
        newtype = _mpi.type_subarray(sizes, subsizes, starts, order, self)
        return type(self)(newtype)



    def Create_darray(self, size, rank, gsizes, distribs, dargs, psizes, order = None):
        newtype = _mpi.type_darray(size, rank, gsizes, distribs, dargs, psizes, order, self)
        return type(self)(newtype)



    def Create_struct(cls, blocklengths, displacements, datatypes):
        newtype = _mpi.type_struct(blocklengths, displacements, datatypes)
        return cls(newtype)


    Create_struct = classmethod(Create_struct)

    def Commit(self):
        _mpi.type_commit(self)



    def Free(self):
        _mpi.type_free(self)



    def Create_resized(self, lb, extent):
        newtype = _mpi.type_resized(self, lb, extent)
        return type(self)(newtype)


    Resized = Create_resized

    def Get_true_extent(self):
        return _mpi.type_true_extent(self)



    def Pack(self, inbuf, outbuf, position, comm):
        return _mpi.pack(inbuf, self, outbuf, position, comm)



    def Unpack(self, inbuf, position, outbuf, comm):
        return _mpi.unpack(inbuf, position, outbuf, self, comm)



    def Pack_size(self, count, comm):
        return _mpi.pack_size(count, self, comm)



    def Pack_external(self, datarep, inbuf, outbuf, position):
        return _mpi.pack_external(datarep, inbuf, self, outbuf, position)



    def Unpack_external(self, datarep, inbuf, position, outbuf):
        return _mpi.unpack_external(datarep, inbuf, position, outbuf, self)



    def Pack_external_size(self, datarep, count):
        return _mpi.pack_external_size(datarep, count, self)



    def Get_name(self):
        return _mpi.type_get_name(self)



    def Set_name(self, name):
        return _mpi.type_set_name(self, name)


    size = property(_mpi.type_size, doc='datatype size, in bytes.')
    extent = property(_mpi.type_ex, doc='datatype extent.')
    lb = property(_mpi.type_lb, doc='datatype lower bound.')
    ub = property(_mpi.type_ub, doc='datatype upper bound.')
    name = property(_mpi.type_get_name, _mpi.type_set_name, doc='datatype name')

DATATYPE_NULL = Datatype(_mpi.DATATYPE_NULL)
CHAR = Datatype(_mpi.CHAR)
WCHAR = Datatype(_mpi.WCHAR)
SIGNED_CHAR = Datatype(_mpi.SIGNED_CHAR)
UNSIGNED_CHAR = Datatype(_mpi.UNSIGNED_CHAR)
SHORT = Datatype(_mpi.SHORT)
UNSIGNED_SHORT = Datatype(_mpi.UNSIGNED_SHORT)
INT = Datatype(_mpi.INT)
UNSIGNED = Datatype(_mpi.UNSIGNED)
LONG = Datatype(_mpi.LONG)
UNSIGNED_LONG = Datatype(_mpi.UNSIGNED_LONG)
FLOAT = Datatype(_mpi.FLOAT)
DOUBLE = Datatype(_mpi.DOUBLE)
LONG_DOUBLE = Datatype(_mpi.LONG_DOUBLE)
BYTE = Datatype(_mpi.BYTE)
PACKED = Datatype(_mpi.PACKED)
SHORT_INT = Datatype(_mpi.SHORT_INT)
TWOINT = Datatype(_mpi.TWOINT)
INT_INT = Datatype(_mpi.INT_INT)
LONG_INT = Datatype(_mpi.LONG_INT)
FLOAT_INT = Datatype(_mpi.FLOAT_INT)
DOUBLE_INT = Datatype(_mpi.DOUBLE_INT)
LONG_DOUBLE_INT = Datatype(_mpi.LONG_DOUBLE_INT)
LONG_LONG = Datatype(_mpi.LONG_LONG)
LONG_LONG_INT = Datatype(_mpi.LONG_LONG_INT)
UNSIGNED_LONG_LONG = Datatype(_mpi.UNSIGNED_LONG_LONG)
UB = Datatype(_mpi.UB)
LB = Datatype(_mpi.LB)

def Get_address(location):
    return _mpi.get_address(location)



def Alloc_mem(size, info = None):
    return _mpi.alloc_mem(size, info)



def Free_mem(base):
    return _mpi.free_mem(base)



def Attach_buffer(buf):
    return _mpi.buffer_attach(buf)



def Detach_buffer():
    return _mpi.buffer_detach()



class Status(_mpi.Status):

    def __init__(self, status = None):
        _mpi.Status.__init__(self, status)



    def Get_source(self):
        return self.MPI_SOURCE



    def Get_tag(self):
        return self.MPI_TAG



    def Get_error(self):
        return self.MPI_ERROR



    def Set_source(self, source):
        self.MPI_SOURCE = source



    def Set_tag(self, tag):
        self.MPI_TAG = tag



    def Set_error(self, error):
        self.MPI_ERROR = error



    def Get_count(self, datatype = None):
        if datatype is None:
            datatype = BYTE
        return _mpi.get_count(self, datatype)



    def Get_elements(self, datatype = None):
        if datatype is None:
            datatype = BYTE
        return _mpi.get_elements(self, datatype)



    def Is_cancelled(self):
        return _mpi.test_cancelled(self)


    source = property(Get_source, Set_source, doc='message source')
    tag = property(Get_tag, Set_tag, doc='message tag')
    error = property(Get_error, Set_error, doc='message error')


class Request(_mpi.Request):

    def __init__(self, request = None):
        _mpi.Request.__init__(self, request)



    def Wait(self, status = None):
        return _mpi.wait(self, status)



    def Test(self, status = None):
        return _mpi.test(self, status)



    def Free(self):
        return _mpi.request_free(self)



    def Get_status(self, status = None):
        return _mpi.request_get_status(self, status)



    def Waitany(requests, status = None):
        return _mpi.waitany(requests, status)


    Waitany = staticmethod(Waitany)

    def Testany(requests, status = None):
        return _mpi.testany(requests, status)


    Testany = staticmethod(Testany)

    def Waitall(requests, statuses = None):
        return _mpi.waitall(requests, statuses)


    Waitall = staticmethod(Waitall)

    def Testall(requests, statuses = None):
        return _mpi.testall(requests, statuses)


    Testall = staticmethod(Testall)

    def Waitsome(requests, statuses = None):
        return _mpi.waitsome(requests, statuses)


    Waitsome = staticmethod(Waitsome)

    def Testsome(requests, statuses = None):
        return _mpi.testsome(requests, statuses)


    Testsome = staticmethod(Testsome)

    def Cancel(self):
        return _mpi.cancel(self)




class Prequest(Request):

    def __init__(self, prequest = None):
        Request.__init__(self, prequest)



    def Start(self):
        _mpi.start(self)



    def Startall(requests):
        _mpi.startall(requests)


    Startall = staticmethod(Startall)

REQUEST_NULL = Request(_mpi.REQUEST_NULL)

class Op(_mpi.Op):

    def __new__(cls, op = None, *targs, **kargs):
        newop = _mpi.Op.__new__(cls, op)
        if newop is not op:
            if targs or kargs:
                newop.Init(*targs, **kargs)
            else:
                newop.Init(None, False)
        return newop



    def __init__(self, op = None, *targs, **kargs):
        _mpi.Op.__init__(self, op, *targs, **kargs)



    def __call__(self, x, y):
        return self._Op__function(x, y)



    def Init(self, function, commute = False):
        if callable(function):
            self._Op__function = function
            self._Op__commute = bool(commute)
        elif function is not None:
            _mpi.op_create(function, commute, self)
        self._Op__function = lambda x, y: _mpi._raise(_mpi.ERR_OP)
        self._Op__commute = bool(commute)



    def Free(self):
        _mpi.op_free(self)



OP_NULL = Op(_mpi.OP_NULL)
MAX = Op(_mpi.MAX, _op.MAX, True)
MIN = Op(_mpi.MIN, _op.MIN, True)
SUM = Op(_mpi.SUM, _op.SUM, True)
PROD = Op(_mpi.PROD, _op.PROD, True)
LAND = Op(_mpi.LAND, _op.LAND, True)
BAND = Op(_mpi.BAND, _op.BAND, True)
LOR = Op(_mpi.LOR, _op.LOR, True)
BOR = Op(_mpi.BOR, _op.BOR, True)
LXOR = Op(_mpi.LXOR, _op.LXOR, True)
BXOR = Op(_mpi.BXOR, _op.BXOR, True)
MAXLOC = Op(_mpi.MAXLOC, _op.MAXLOC, True)
MINLOC = Op(_mpi.MINLOC, _op.MINLOC, True)
REPLACE = Op(_mpi.REPLACE, _op.REPLACE, False)

class Info(_mpi.Info):

    def __init__(self, info = None):
        _mpi.Info.__init__(self, info)



    def __len__(self):
        if self == _mpi.INFO_NULL:
            return 0
        else:
            return _mpi.info_get_nkeys(self)



    def __getitem__(self, key):
        (value, flag,) = _mpi.info_get(self, key)
        if not flag:
            raise KeyError(key)
        return value



    def __setitem__(self, key, value):
        return _mpi.info_set(self, key, value)



    def __delitem__(self, key):
        _mpi.info_delete(self, key)



    def __contains__(self, key):
        return _mpi.info_get_valuelen(self, key)[1]



    def __iter__(self):
        if self == _mpi.INFO_NULL:
            return 
        nkeys = _mpi.info_get_nkeys(self)
        for nthkey in xrange(nkeys):
            yield _mpi.info_get_nthkey(self, nthkey)




    def Create(cls):
        info = _mpi.info_create()
        return cls(info)


    Create = classmethod(Create)

    def Dup(self):
        info = _mpi.info_dup(self)
        return type(self)(info)



    def Free(self):
        _mpi.info_free(self)



    def Set(self, key, value):
        _mpi.info_set(self, key, value)



    def Delete(self, key):
        _mpi.info_delete(self, key)



    def Get(self, key, maxlen = -1):
        return _mpi.info_get(self, key, maxlen)



    def Get_nkeys(self):
        return _mpi.info_get_nkeys(self)



    def Get_nthkey(self, n):
        return _mpi.info_get_nthkey(self, n)



INFO_NULL = Info(_mpi.INFO_NULL)

class Group(_mpi.Group):

    def __init__(self, group = None):
        _mpi.Group.__init__(self, group)



    def Get_size(self):
        return _mpi.group_size(self)



    def Get_rank(self):
        return _mpi.group_rank(self)



    def Translate_ranks(group1, ranks1, group2):
        return _mpi.group_transl_rank(group1, ranks1, group2)


    Translate_ranks = staticmethod(Translate_ranks)

    def Compare(group1, group2):
        return _mpi.group_compare(group1, group2)


    Compare = staticmethod(Compare)

    def Union(cls, group1, group2):
        newgroup = _mpi.group_union(group1, group2)
        return cls(newgroup)


    Union = classmethod(Union)

    def Intersect(cls, group1, group2):
        newgroup = _mpi.group_intersection(group1, group2)
        return cls(newgroup)


    Intersect = classmethod(Intersect)

    def Difference(cls, group1, group2):
        newgroup = _mpi.group_difference(group1, group2)
        return cls(newgroup)


    Difference = classmethod(Difference)

    def Incl(self, ranks):
        newgroup = _mpi.group_incl(self, ranks)
        return type(self)(newgroup)



    def Excl(self, ranks):
        newgroup = _mpi.group_excl(self, ranks)
        return type(self)(newgroup)



    def Range_incl(self, ranks):
        newgroup = _mpi.group_range_incl(self, ranks)
        return type(self)(newgroup)



    def Range_excl(self, ranks):
        newgroup = _mpi.group_range_excl(self, ranks)
        return type(self)(newgroup)



    def Free(self):
        return _mpi.group_free(self)


    size = property(_mpi.group_size, doc='number of processes in group')
    rank = property(_mpi.group_rank, doc='rank of this process in group')

GROUP_NULL = Group(_mpi.GROUP_NULL)
GROUP_EMPTY = Group(_mpi.GROUP_EMPTY)

class Comm(_mpi.Comm):

    def __init__(self, comm = None):
        _mpi.Comm.__init__(self, comm)
        _mpi.comm_check_any(self)


    SERIALIZER = Pickle

    def Get_group(self):
        group = _mpi.comm_group(self)
        return Group(group)



    def Get_size(self):
        return _mpi.comm_size(self)



    def Get_rank(self):
        return _mpi.comm_rank(self)



    def Compare(comm1, comm2):
        return _mpi.comm_compare(comm1, comm2)


    Compare = staticmethod(Compare)

    def Clone(self):
        newcomm = _mpi.comm_dup(self)
        return type(self)(newcomm)



    def Free(self):
        _mpi.comm_free(self)



    def Send(self, buf, dest = 0, tag = 0):
        (buf, fastmode,) = _mpi.make_buf(buf)
        if fastmode:
            _mpi.send(buf, dest, tag, self)
            return 
        else:
            if dest != _mpi.PROC_NULL:
                buf = self.SERIALIZER.dump(buf)
            else:
                buf = None
            _mpi.send_string(buf, dest, tag, self)
            return 



    def Recv(self, buf = None, source = 0, tag = 0, status = None):
        (buf, fastmode,) = _mpi.make_buf(buf)
        if fastmode:
            _mpi.recv(buf, source, tag, self, status)
            return None
        else:
            buf = _mpi.recv_string(buf, source, tag, self, status)
            if source != _mpi.PROC_NULL:
                buf = self.SERIALIZER.load(buf)
            return buf



    def Sendrecv(self, sendbuf, dest = 0, sendtag = 0, recvbuf = None, source = 0, recvtag = 0, status = None):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.sendrecv(sendbuf, dest, sendtag, recvbuf, source, recvtag, self, status)
            return 
        else:
            serializer = self.SERIALIZER
            if dest != _mpi.PROC_NULL:
                sendbuf = serializer.dump(sendbuf)
            else:
                sendbuf = None
            recvbuf = _mpi.sendrecv_string(sendbuf, dest, sendtag, recvbuf, source, recvtag, self, status)
            if recvbuf is not None:
                recvbuf = serializer.load(recvbuf)
            return recvbuf



    def Sendrecv_replace(self, buf, dest = 0, sendtag = 0, source = 0, recvtag = 0, status = None):
        _mpi.sendrecv_replace(buf, dest, sendtag, source, recvtag, self, status)



    def Isend(self, buf, dest = 0, tag = 0):
        request = _mpi.isend(buf, dest, tag, self)
        return Request(request)



    def Irecv(self, buf, source = 0, tag = 0):
        request = _mpi.irecv(buf, source, tag, self)
        return Request(request)



    def Probe(self, source = 0, tag = 0, status = None):
        return _mpi.probe(source, tag, self, status)



    def Iprobe(self, source = 0, tag = 0, status = None):
        return _mpi.iprobe(source, tag, self, status)



    def Send_init(self, buf, dest = 0, tag = 0):
        prequest = _mpi.send_init(buf, dest, tag, self)
        return Prequest(prequest)



    def Recv_init(self, buf, source = 0, tag = 0):
        prequest = _mpi.recv_init(buf, source, tag, self)
        return Prequest(prequest)



    def Bsend(self, buf, dest = 0, tag = 0):
        return _mpi.send(buf, dest, tag, self, 'B')



    def Ssend(self, buf, dest = 0, tag = 0):
        return _mpi.send(buf, dest, tag, self, 'S')



    def Rsend(self, buf, dest = 0, tag = 0):
        return _mpi.send(buf, dest, tag, self, 'R')



    def Ibsend(self, buf, dest = 0, tag = 0):
        request = _mpi.isend(buf, dest, tag, self, 'B')
        return Request(request)



    def Issend(self, buf, dest = 0, tag = 0):
        request = _mpi.isend(buf, dest, tag, self, 'S')
        return Request(request)



    def Irsend(self, buf, dest = 0, tag = 0):
        request = _mpi.isend(buf, dest, tag, self, 'R')
        return Request(request)



    def Bsend_init(self, buf, dest = 0, tag = 0):
        prequest = _mpi.send_init(buf, dest, tag, self, 'B')
        return Prequest(prequest)



    def Ssend_init(self, buf, dest = 0, tag = 0):
        prequest = _mpi.send_init(buf, dest, tag, self, 'S')
        return Prequest(prequest)



    def Rsend_init(self, buf, dest = 0, tag = 0):
        prequest = _mpi.send_init(buf, dest, tag, self, 'R')
        return Prequest(prequest)



    def Barrier(self):
        _mpi.barrier(self)



    def Bcast(self, buf = None, root = 0):
        (buf, fastmode,) = _mpi.make_buf(buf)
        if fastmode:
            _mpi.bcast(buf, root, self)
            return 
        else:
            serializer = self.SERIALIZER
            if _mpi.comm_test_inter(self):
                if root == _mpi.ROOT:
                    buf = serializer.dump(buf)
                else:
                    buf = None
            elif root == _mpi.comm_rank(self):
                buf = serializer.dump(buf)
            else:
                buf = None
            buf = _mpi.bcast_string(buf, root, self)
            if buf is not None:
                buf = serializer.load(buf)
            return buf



    def Gather(self, sendbuf, recvbuf = None, root = 0):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.gather(sendbuf, recvbuf, root, self)
            return 
        else:
            serializer = self.SERIALIZER
            if _mpi.comm_test_inter(self):
                if root != _mpi.ROOT and root != _mpi.PROC_NULL:
                    sendbuf = serializer.dump(sendbuf)
                else:
                    sendbuf = None
            else:
                sendbuf = serializer.dump(sendbuf)
            recvbuf = _mpi.gather_string(sendbuf, recvbuf, root, self)
            if recvbuf is not None:
                recvbuf = map(serializer.load, recvbuf)
            return recvbuf



    def Scatter(self, sendbuf = None, recvbuf = None, root = 0):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.scatter(sendbuf, recvbuf, root, self)
            return 
        else:
            serializer = self.SERIALIZER
            if _mpi.comm_test_inter(self):
                if root == _mpi.ROOT:
                    sendbuf = map(serializer.dump, sendbuf)
                else:
                    sendbuf = None
            elif root == _mpi.comm_rank(self):
                sendbuf = map(serializer.dump, sendbuf)
            else:
                sendbuf = None
            recvbuf = _mpi.scatter_string(sendbuf, recvbuf, root, self)
            if recvbuf is not None:
                recvbuf = serializer.load(recvbuf)
            return recvbuf



    def Allgather(self, sendbuf, recvbuf = None):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.allgather(sendbuf, recvbuf, self)
            return None
        else:
            serializer = self.SERIALIZER
            sendbuf = serializer.dump(sendbuf)
            recvbuf = _mpi.allgather_string(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            return recvbuf



    def Alltoall(self, sendbuf, recvbuf = None):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.alltoall(sendbuf, recvbuf, self)
            return None
        else:
            serializer = self.SERIALIZER
            sendbuf = map(serializer.dump, sendbuf)
            recvbuf = _mpi.alltoall_string(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            return recvbuf



    def Reduce(self, sendbuf, recvbuf = None, op = SUM, root = 0):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.reduce(sendbuf, recvbuf, op, root, self)
            return 
        else:
            recvbuf = self.Gather(sendbuf, None, root)
            if recvbuf is not None:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, xrange(len(recvbuf)))
                recvbuf = reduce(op, recvbuf)
            return recvbuf



    def Allreduce(self, sendbuf, recvbuf = None, op = SUM):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.allreduce(sendbuf, recvbuf, op, self)
            return None
        else:
            serializer = self.SERIALIZER
            sendbuf = serializer.dump(sendbuf)
            recvbuf = _mpi.allgather_string(sendbuf, recvbuf, self)
            recvbuf = map(serializer.load, recvbuf)
            if op in (MAXLOC, MINLOC):
                recvbuf = zip(recvbuf, xrange(len(recvbuf)))
            recvbuf = reduce(op, recvbuf)
            return recvbuf



    def Get_errhandler(self):
        eh = _mpi.comm_get_errhandler(self)
        return Errhandler(eh)



    def Set_errhandler(self, errhandler):
        _mpi.comm_set_errhandler(self, errhandler)



    def Abort(self, errorcode = 0):
        _mpi.comm_abort(self, errorcode)



    def Is_inter(self):
        return _mpi.comm_test_inter(self)



    def Is_intra(self):
        return not _mpi.comm_test_inter(self)



    def Get_topology(self):
        return _mpi.topo_test(self)



    def Get_parent():
        newcomm = _mpi.comm_get_parent()
        return Intercomm(newcomm)


    Get_parent = staticmethod(Get_parent)

    def Disconnect(self):
        _mpi.comm_disconnect(self)



    def Join(fd):
        newcomm = _mpi.comm_join(fd)
        return Intercomm(newcomm)


    Join = staticmethod(Join)

    def Get_name(self):
        return _mpi.comm_get_name(self)



    def Set_name(self, name):
        return _mpi.comm_set_name(self, name)



    class Port(object):
        TAG = _mpi.TAG_UB - 1

        def __init__(self, comm, pid):
            if pid not in xrange(len(comm)):
                raise ValueError('port number out of range')
            self._comm = comm
            self._pid = pid



        def Send(self, buf, tag = 0):
            return self.comm.Send(buf, self.pid, tag)



        def Recv(self, buf = None, tag = 0):
            return self.comm.Recv(buf, self.pid, tag)



        def Bcast(self, buf = None):
            return self.comm.Bcast(buf, self.pid)



        def Gather(self, sbuf, rbuf = None):
            return self.comm.Gather(sbuf, rbuf, self.pid)



        def Scatter(self, sbuf = None, rbuf = None):
            return self.comm.Scatter(sbuf, rbuf, self.pid)



        def Reduce(self, sbuf, rbuf = None, op = SUM):
            return self.comm.Reduce(sbuf, rbuf, op, self.pid)



        def __lshift__(self, stream):
            if type(stream) is not list:
                raise TypeError('input stream must be a list')
            self.Send(stream, self.TAG)



        def __rshift__(self, stream):
            if type(stream) is not list:
                raise TypeError('output stream must be a list')
            stream.extend(self.Recv(None, self.TAG))


        comm = property(lambda self: self._comm, doc='associated communicator')
        pid = property(lambda self: self._pid, doc='associated process *id*')


    def __len__(self):
        if self == _mpi.COMM_NULL:
            return 0
        else:
            if _mpi.comm_test_inter(self):
                return _mpi.comm_remote_size(self)
            return _mpi.comm_size(self)



    def __getitem__(self, i):
        if type(i) is not int:
            raise TypeError('indices must be integers')
        if i < 0:
            i += len(self)
        if i < 0 or i >= len(self):
            raise IndexError('index out of range')
        return self.__class__.Port(self, i)



    def __iter__(self):
        i = 0
        port = self.__class__.Port
        while i < len(self):
            yield port(self, i)
            i += 1



    size = property(_mpi.comm_size, doc='number of processes in group')
    rank = property(_mpi.comm_rank, doc='rank of this process in group')
    is_inter = property(_mpi.comm_test_inter, doc='True if is an intercommunicator')
    is_intra = property(_mpi.comm_test_intra, doc='True if is an intracommunicator')
    topology = property(_mpi.topo_test, doc='type of topology (if any)')
    name = property(_mpi.comm_get_name, _mpi.comm_set_name, doc='communicator name')

COMM_NULL = Comm(_mpi.COMM_NULL)

class Intracomm(Comm):

    def __init__(self, comm = None):
        Comm.__init__(self, comm)
        _mpi.comm_check_intra(self)



    def Dup(self):
        newcomm = _mpi.comm_dup(self)
        return Intracomm(newcomm)



    def Create(self, group):
        newcomm = _mpi.comm_create(self, group)
        return Intracomm(newcomm)



    def Split(self, color, key = 0):
        newcomm = _mpi.comm_split(self, color, key)
        return Intracomm(newcomm)



    def Create_intercomm(self, local_leader, peer_comm, remote_leader, tag = 0):
        newcomm = _mpi.intercomm_create(self, local_leader, peer_comm, remote_leader, tag)
        return Intercomm(newcomm)



    def Create_cart(self, dims, periods = None, reorder = False):
        if periods is None:
            periods = [False] * len(dims)
        newcomm = _mpi.cart_create(self, dims, periods, reorder)
        return Cartcomm(newcomm)



    def Create_graph(self, index, edges, reorder = False):
        newcomm = _mpi.graph_create(self, index, edges, reorder)
        return Graphcomm(newcomm)



    def Scan(self, sendbuf, recvbuf = None, op = SUM):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.scan(sendbuf, recvbuf, op, self)
            return None
        else:
            recvbuf = self.Gather(sendbuf, root=0)
            if _mpi.comm_rank(self) == 0:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, xrange(len(recvbuf)))
                for i in xrange(1, len(recvbuf)):
                    recvbuf[i] = op(recvbuf[(i - 1)], recvbuf[i])

            recvbuf = self.Scatter(recvbuf, root=0)
            return recvbuf



    def Exscan(self, sendbuf, recvbuf = None, op = SUM):
        (sendbuf, sfastmode,) = _mpi.make_buf(sendbuf)
        (recvbuf, rfastmode,) = _mpi.make_buf(recvbuf)
        if sfastmode or rfastmode:
            _mpi.exscan(sendbuf, recvbuf, op, self)
            return 
        else:
            recvbuf = self.Gather(sendbuf, root=0)
            if _mpi.comm_rank(self) == 0:
                if op in (MAXLOC, MINLOC):
                    recvbuf = zip(recvbuf, xrange(len(recvbuf)))
                for i in xrange(1, len(recvbuf)):
                    recvbuf[i] = op(recvbuf[(i - 1)], recvbuf[i])

                recvbuf.insert(0, None)
                recvbuf.pop(-1)
            recvbuf = self.Scatter(recvbuf, root=0)
            return recvbuf



    def Spawn(self, command, args = None, maxprocs = 1, info = None, root = 0):
        newcomm = _mpi.comm_spawn(command, args, maxprocs, info, root, self)
        return Intercomm(newcomm)



    def Accept(self, port_name, info = None, root = 0):
        newcomm = _mpi.comm_accept(port_name, info, root, self)
        return Intercomm(newcomm)



    def Connect(self, port_name, info = None, root = 0):
        newcomm = _mpi.comm_connect(port_name, info, root, self)
        return Intercomm(newcomm)



__COMM_SELF__ = Intracomm(_mpi.COMM_SELF)
__COMM_WORLD__ = Intracomm(_mpi.COMM_WORLD)
COMM_SELF = SELF = Intracomm(_mpi.COMM_SELF_DUP)
COMM_WORLD = WORLD = Intracomm(_mpi.COMM_WORLD_DUP)

def Compute_dims(nnodes, dims):
    return _mpi.dims_create(nnodes, dims)



class Cartcomm(Intracomm):

    def __init__(self, comm = None):
        Intracomm.__init__(self, comm)
        _mpi.comm_check_cart(self)



    def Dup(self):
        newcomm = _mpi.comm_dup(self)
        return Cartcomm(newcomm)



    def Get_dim(self):
        return _mpi.cartdim_get(self)



    def Get_topo(self):
        return _mpi.cart_get(self)



    def Get_cart_rank(self, coords):
        return _mpi.cart_rank(self, coords)



    def Get_coords(self, rank):
        return _mpi.cart_coords(self, rank)



    def Shift(self, direction, disp):
        return _mpi.cart_shift(self, direction, disp)



    def Sub(self, remain_dims):
        newcomm = _mpi.cart_sub(self, remain_dims)
        return Cartcomm(newcomm)



    def Map(self, dims, periods):
        return _mpi.cart_map(self, dims, periods)


    dim = property(_mpi.cartdim_get, doc='number of dimensions')
    topo = property(_mpi.cart_get, doc='Cartesian topology information')


class Graphcomm(Intracomm):

    def __init__(self, comm = None):
        Intracomm.__init__(self, comm)
        _mpi.comm_check_graph(self)



    def Dup(self):
        newcomm = _mpi.comm_dup(self)
        return Graphcomm(newcomm)



    def Get_dims(self):
        return _mpi.graphdims_get(self)



    def Get_topo(self):
        return _mpi.graph_get(self)



    def Get_neighbors_count(self, rank):
        return _mpi.graph_neigh_count(self, rank)



    def Get_neighbors(self, rank):
        return _mpi.graph_neigh(self, rank)



    def Map(self, index, edges):
        return _mpi.graph_map(self, index, edges)


    dims = property(_mpi.graphdims_get, doc='number of nodes and edges')
    topo = property(_mpi.graph_get, doc='graph topology information')


class Intercomm(Comm):

    def __init__(self, comm = None):
        Comm.__init__(self, comm)
        _mpi.comm_check_inter(self)



    def Get_remote_size(self):
        return _mpi.comm_remote_size(self)



    def Get_remote_group(self):
        group = _mpi.comm_remote_group(self)
        return Group(group)



    def Dup(self):
        newcomm = _mpi.comm_dup(self)
        return Intercomm(newcomm)



    def Create(self, group):
        newcomm = _mpi.comm_create(self, group)
        return Intercomm(newcomm)



    def Split(self, color = 0, key = 0):
        newcomm = _mpi.comm_split(self, color, key)
        return Intercomm(newcomm)



    def Merge(self, high = False):
        intracomm = _mpi.intercomm_merge(self, high)
        return Intracomm(intracomm)


    remote_size = property(_mpi.comm_remote_size, doc='size of remote group')


def Open_port(info = None):
    return _mpi.open_port(info)



def Close_port(port_name):
    return _mpi.close_port(port_name)



def Publish_name(service_name, info, port_name):
    return _mpi.publish_name(service_name, info, port_name)



def Unpublish_name(service_name, info, port_name):
    return _mpi.unpublish_name(service_name, info, port_name)



def Lookup_name(service_name, info = None):
    return _mpi.lookup_name(service_name, info)


MODE_NOCHECK = _mpi.MODE_NOCHECK
MODE_NOSTORE = _mpi.MODE_NOSTORE
MODE_NOPUT = _mpi.MODE_NOPUT
MODE_NOPRECEDE = _mpi.MODE_NOPRECEDE
MODE_NOSUCCEED = _mpi.MODE_NOSUCCEED
LOCK_EXCLUSIVE = _mpi.LOCK_EXCLUSIVE
LOCK_SHARED = _mpi.LOCK_SHARED

class Win(_mpi.Win):

    def __init__(self, win = None):
        _mpi.Win.__init__(self, win)



    def Create(cls, memory, disp, info, comm):
        win = _mpi.win_create(memory, disp, info, comm)
        return cls(win)


    Create = classmethod(Create)

    def Free(self):
        return _mpi.win_free(self)



    def Get_base(self):
        return _mpi.win_get_base(self)



    def Get_size(self):
        return _mpi.win_get_size(self)



    def Get_disp_unit(self):
        return _mpi.win_get_disp(self)



    def Get_group(self):
        group = _mpi.win_get_group(self)
        return Group(group)



    def Put(self, origin_buf, target_rank, target_disp = 0, target_count = -1, target_datatype = None):
        return _mpi.win_put(origin_buf, target_rank, target_disp, target_count, target_datatype, self)



    def Get(self, origin_buf, target_rank, target_disp = 0, target_count = -1, target_datatype = None):
        return _mpi.win_get(origin_buf, target_rank, target_disp, target_count, target_datatype, self)



    def Accumulate(self, origin_buf, target_rank, target_disp = 0, target_count = -1, target_datatype = None, op = SUM):
        return _mpi.win_accumulate(origin_buf, target_rank, target_disp, target_count, target_datatype, op, self)



    def Fence(self, assertion = 0):
        return _mpi.win_fence(assertion, self)



    def Start(self, group, assertion = 0):
        return _mpi.win_start(group, assertion, self)



    def Complete(self):
        return _mpi.win_complete(self)



    def Post(self, group, assertion = 0):
        return _mpi.win_post(group, assertion, self)



    def Wait(self):
        return _mpi.win_wait(self)



    def Test(self):
        return _mpi.win_test(self)



    def Lock(self, lock_type, rank, assertion = 0):
        return _mpi.win_lock(lock_type, rank, assertion, self)



    def Unlock(self, rank):
        return _mpi.win_unlock(rank, self)



    def Get_errhandler(self):
        eh = _mpi.win_get_errhandler(self)
        return Errhandler(eh)



    def Set_errhandler(self, errhandler):
        _mpi.win_set_errhandler(self, errhandler)



    def Get_name(self):
        return _mpi.win_get_name(self)



    def Set_name(self, name):
        return _mpi.win_set_name(self, name)


    base = property(_mpi.win_get_base, doc='window base address')
    size = property(_mpi.win_get_size, doc='window size, in bytes')
    disp_unit = property(_mpi.win_get_disp, doc='displacement unit')
    name = property(_mpi.win_get_name, _mpi.win_set_name, doc='window name')

WIN_NULL = Win(_mpi.WIN_NULL)
MODE_RDONLY = _mpi.MODE_RDONLY
MODE_RDWR = _mpi.MODE_RDWR
MODE_WRONLY = _mpi.MODE_WRONLY
MODE_CREATE = _mpi.MODE_CREATE
MODE_EXCL = _mpi.MODE_EXCL
MODE_DELETE_ON_CLOSE = _mpi.MODE_DELETE_ON_CLOSE
MODE_UNIQUE_OPEN = _mpi.MODE_UNIQUE_OPEN
MODE_SEQUENTIAL = _mpi.MODE_SEQUENTIAL
MODE_APPEND = _mpi.MODE_APPEND
SEEK_SET = _mpi.SEEK_SET
SEEK_CUR = _mpi.SEEK_CUR
SEEK_END = _mpi.SEEK_END
DISPLACEMENT_CURRENT = _mpi.DISPLACEMENT_CURRENT
DISP_CUR = _mpi.DISPLACEMENT_CURRENT

class File(_mpi.File):

    def __init__(self, file = None):
        _mpi.File.__init__(self, file)



    def Open(cls, comm, filename, amode = None, info = None):
        fh = _mpi.file_open(comm, filename, amode, info)
        return cls(fh)


    Open = classmethod(Open)

    def Close(self):
        _mpi.file_close(self)



    def Delete(filename, info = None):
        return _mpi.file_delete(filename, info)


    Delete = staticmethod(Delete)

    def Set_size(self, size):
        return _mpi.file_set_size(self, size)



    def Preallocate(self, size):
        return _mpi.file_preallocate(self, size)



    def Get_size(self):
        return _mpi.file_get_size(self)



    def Get_group(self):
        group = _mpi.file_get_group(self)
        return Group(group)



    def Get_amode(self):
        return _mpi.file_get_amode(self)



    def Set_info(self, info):
        return _mpi.file_set_info(self, info)



    def Get_info(self):
        info = _mpi.file_get_info(self)
        return Info(info)



    def Set_view(self, disp = 0, etype = None, filetype = None, datarep = 'native', info = None):
        if etype is None:
            etype = _mpi.BYTE
        if filetype is None:
            filetype = etype
        return _mpi.file_set_view(self, disp, etype, filetype, datarep, info)



    def Get_view(self):
        (disp, etype, ftype, datarep,) = _mpi.file_get_view(self)
        return (disp,
         Datatype(etype),
         Datatype(ftype),
         datarep)



    def Read_at(self, offset, buf, status = None):
        return _mpi.file_read(self, offset, buf, status, 0)



    def Read_at_all(self, offset, buf, status = None):
        return _mpi.file_read(self, offset, buf, status, 1)



    def Write_at(self, offset, buf, status = None):
        return _mpi.file_write(self, offset, buf, status, 0)



    def Write_at_all(self, offset, buf, status = None):
        return _mpi.file_write(self, offset, buf, status, 1)



    def Iread_at(self, offset, buf):
        request = _mpi.file_iread(self, offset, buf, 0)
        return Request(request)



    def Iwrite_at(self, offset, buf):
        request = _mpi.file_iwrite(self, offset, buf, 0)
        return Request(request)



    def Read(self, buf, status = None):
        return _mpi.file_read(self, buf, status, 0)



    def Read_all(self, buf, status = None):
        return _mpi.file_read(self, buf, status, 1)



    def Write(self, buf, status = None):
        return _mpi.file_write(self, buf, status, 0)



    def Write_all(self, buf, status = None):
        return _mpi.file_write(self, buf, status, 1)



    def Iread(self, buf):
        request = _mpi.file_iread(self, buf, 0)
        return Request(request)



    def Iwrite(self, buf):
        request = _mpi.file_iwrite(self, buf, 0)
        return Request(request)



    def Seek(self, offset, whence = None):
        return _mpi.file_seek(self, offset, whence, 0)



    def Get_position(self):
        return _mpi.file_get_position(self, 0)



    def Get_byte_offset(self, offset):
        return _mpi.file_get_byte_offset(self, offset)



    def Read_shared(self, buf, status = None):
        return _mpi.file_read(self, buf, status, 2)



    def Write_shared(self, buf, status = None):
        return _mpi.file_write(self, buf, status, 2)



    def Iread_shared(self, buf):
        request = _mpi.file_iread(self, buf, 2)
        return Request(request)



    def Iwrite_shared(self, buf):
        request = _mpi.file_iwrite(self, buf, 2)
        return Request(request)



    def Read_ordered(self, buf, status = None):
        return _mpi.file_read(self, buf, status, 3)



    def Write_ordered(self, buf, status = None):
        return _mpi.file_write(self, buf, status, 3)



    def Seek_shared(self, offset, whence = None):
        return _mpi.file_seek(self, offset, whence, 2)



    def Get_position_shared(self):
        return _mpi.file_get_position(self, 2)



    def Read_at_all_begin(self, offset, buf):
        return _mpi.file_read_split(self, offset, buf, None, 1, 0)



    def Read_at_all_end(self, buf, status = None):
        return _mpi.file_read_split(self, 0, buf, status, 1, 1)



    def Write_at_all_begin(self, offset, buf):
        return _mpi.file_write_split(self, offset, buf, None, 1, 0)



    def Write_at_all_end(self, buf, status = None):
        return _mpi.file_write_split(self, 0, buf, status, 1, 1)



    def Read_all_begin(self, buf):
        return _mpi.file_read_split(self, buf, None, 1, 0)



    def Read_all_end(self, buf, status = None):
        return _mpi.file_read_split(self, buf, status, 1, 1)



    def Write_all_begin(self, buf):
        return _mpi.file_write_split(self, buf, None, 1, 0)



    def Write_all_end(self, buf, status = None):
        return _mpi.file_write_split(self, buf, status, 1, 1)



    def Read_ordered_begin(self, buf):
        return _mpi.file_read_split(self, buf, None, 3, 0)



    def Read_ordered_end(self, buf, status = None):
        return _mpi.file_read_split(self, buf, status, 3, 1)



    def Write_ordered_begin(self, buf):
        return _mpi.file_write_split(self, buf, None, 3, 0)



    def Write_ordered_end(self, buf, status = None):
        return _mpi.file_write_split(self, buf, status, 3, 1)



    def Get_type_extent(self, datatype):
        return _mpi.file_get_type_extent(self, datatype)



    def Set_atomicity(self, flag):
        return _mpi.file_set_atomicity(self, flag)



    def Get_atomicity(self):
        return _mpi.file_get_atomicity(self)



    def Sync(self):
        return _mpi.file_sync(self)



    def Get_errhandler(self):
        eh = _mpi.file_get_errhandler(self)
        return Errhandler(eh)



    def Set_errhandler(self, errhandler):
        _mpi.file_set_errhandler(self, errhandler)


    size = property(_mpi.file_get_size, doc='file size, in bytes')
    amode = property(_mpi.file_get_amode, doc='file access mode')

FILE_NULL = File(_mpi.FILE_NULL)

def Init():
    if getattr(Init, '__called', False):
        _func = (Init.__module__, Init.__name__)
        raise RuntimeError('%s.%s() already called' % _func)
    else:
        _mpi.init()
        _mpi._set_exception(Exception)
        setattr(Init, '__called', True)



def Finalize():
    global COMM_WORLD
    global COMM_SELF
    if getattr(Finalize, '__called', False):
        _func = (Finalize.__module__, Finalize.__name__)
        raise RuntimeError('%s.%s() already called' % _func)
    else:
        COMM_SELF = COMM_WORLD = COMM_NULL
        _mpi.COMM_SELF = _mpi.COMM_WORLD = _mpi.COMM_NULL
        _mpi._set_exception(RuntimeError)
        _mpi.finalize()
        setattr(Finalize, '__called', True)



def Is_initialized():
    return _mpi.initialized()



def Is_finalized():
    return _mpi.finalized()


THREAD_SINGLE = _mpi.THREAD_SINGLE
THREAD_FUNNELED = _mpi.THREAD_FUNNELED
THREAD_SERIALIZED = _mpi.THREAD_SERIALIZED
THREAD_MULTIPLE = _mpi.THREAD_MULTIPLE

def Init_thread(required):
    if getattr(Init_thread, '__called', False):
        _func = (Init_thread.__module__, Init_thread.__name__)
        raise RuntimeError('%s.%s() already called' % _func)
    else:
        provided = _mpi.init_thread(required)
        _mpi._set_exception(Exception)
        setattr(Init_thread, '__called', True)
        return provided



def Query_thread():
    return _mpi.query_thread()



def Is_thread_main():
    return _mpi.is_thread_main()



def Get_version():
    return _mpi.get_version()


TAG_UB = _mpi.TAG_UB
HOST = _mpi.HOST
IO = _mpi.IO
WTIME_IS_GLOBAL = _mpi.WTIME_IS_GLOBAL

def Get_processor_name():
    return _mpi.get_processor_name()



def Wtime():
    return _mpi.wtime()



def Wtick():
    return _mpi.wtick()


MAX_PROCESSOR_NAME = _mpi.MAX_PROCESSOR_NAME
MAX_ERROR_STRING = _mpi.MAX_ERROR_STRING
MAX_PORT_NAME = _mpi.MAX_PORT_NAME
MAX_INFO_KEY = _mpi.MAX_INFO_KEY
MAX_INFO_VAL = _mpi.MAX_INFO_VAL
MAX_OBJECT_NAME = _mpi.MAX_OBJECT_NAME
MAX_DATAREP_STRING = _mpi.MAX_DATAREP_STRING

class Errhandler(_mpi.Errhandler):

    def __init__(self, errhandler = None):
        _mpi.Errhandler.__init__(self, errhandler)



    def Free(self):
        _mpi.errhandler_free(self)



ERRHANDLER_NULL = Errhandler(_mpi.ERRHANDLER_NULL)
ERRORS_ARE_FATAL = Errhandler(_mpi.ERRORS_ARE_FATAL)
ERRORS_RETURN = Errhandler(_mpi.ERRORS_RETURN)

class Exception(RuntimeError):

    def __init__(self, ierr, *args):
        self._Exception__ierr = _mpi.SUCCESS
        self._Exception__ierr = int(ierr)
        RuntimeError.__init__(self, int(self), *args)



    def __int__(self):
        return self._Exception__ierr



    def __str__(self):
        return _mpi.error_string(int(self))



    def __eq__(self, error):
        if isinstance(error, Exception):
            error = int(error)
        return int(self) == error



    def __ne__(self, error):
        if isinstance(error, Exception):
            error = int(error)
        return int(self) != error



    def Get_error_code(self):
        return int(self)



    def Get_error_class(self):
        return _mpi.error_class(int(self))



    def Get_error_string(self):
        return _mpi.error_string(int(self))



SUCCESS = _mpi.SUCCESS
ERR_BUFFER = _mpi.ERR_BUFFER
ERR_COUNT = _mpi.ERR_COUNT
ERR_TYPE = _mpi.ERR_TYPE
ERR_TAG = _mpi.ERR_TAG
ERR_COMM = _mpi.ERR_COMM
ERR_RANK = _mpi.ERR_RANK
ERR_ROOT = _mpi.ERR_ROOT
ERR_TRUNCATE = _mpi.ERR_TRUNCATE
ERR_IN_STATUS = _mpi.ERR_IN_STATUS
ERR_PENDING = _mpi.ERR_PENDING
ERR_GROUP = _mpi.ERR_GROUP
ERR_OP = _mpi.ERR_OP
ERR_REQUEST = _mpi.ERR_REQUEST
ERR_DIMS = _mpi.ERR_DIMS
ERR_TOPOLOGY = _mpi.ERR_TOPOLOGY
ERR_ARG = _mpi.ERR_ARG
ERR_INTERN = _mpi.ERR_INTERN
ERR_OTHER = _mpi.ERR_OTHER
ERR_UNKNOWN = _mpi.ERR_UNKNOWN
ERR_KEYVAL = _mpi.ERR_KEYVAL
ERR_NO_MEM = _mpi.ERR_NO_MEM
ERR_NAME = _mpi.ERR_NAME
ERR_PORT = _mpi.ERR_PORT
ERR_SERVICE = _mpi.ERR_SERVICE
ERR_SPAWN = _mpi.ERR_SPAWN
ERR_INFO = _mpi.ERR_INFO
ERR_INFO_KEY = _mpi.ERR_INFO_KEY
ERR_INFO_VALUE = _mpi.ERR_INFO_VALUE
ERR_INFO_NOKEY = _mpi.ERR_INFO_NOKEY
ERR_WIN = _mpi.ERR_WIN
ERR_BASE = _mpi.ERR_BASE
ERR_SIZE = _mpi.ERR_SIZE
ERR_DISP = _mpi.ERR_DISP
ERR_LOCKTYPE = _mpi.ERR_LOCKTYPE
ERR_ASSERT = _mpi.ERR_ASSERT
ERR_RMA_CONFLICT = _mpi.ERR_RMA_CONFLICT
ERR_RMA_SYNC = _mpi.ERR_RMA_SYNC
ERR_FILE = _mpi.ERR_FILE
ERR_NOT_SAME = _mpi.ERR_NOT_SAME
ERR_AMODE = _mpi.ERR_AMODE
ERR_UNSUPPORTED_DATAREP = _mpi.ERR_UNSUPPORTED_DATAREP
ERR_UNSUPPORTED_OPERATION = _mpi.ERR_UNSUPPORTED_OPERATION
ERR_NO_SUCH_FILE = _mpi.ERR_NO_SUCH_FILE
ERR_FILE_EXISTS = _mpi.ERR_FILE_EXISTS
ERR_BAD_FILE = _mpi.ERR_BAD_FILE
ERR_ACCESS = _mpi.ERR_ACCESS
ERR_NO_SPACE = _mpi.ERR_NO_SPACE
ERR_QUOTA = _mpi.ERR_QUOTA
ERR_READ_ONLY = _mpi.ERR_READ_ONLY
ERR_FILE_IN_USE = _mpi.ERR_FILE_IN_USE
ERR_DUP_DATAREP = _mpi.ERR_DUP_DATAREP
ERR_CONVERSION = _mpi.ERR_CONVERSION
ERR_IO = _mpi.ERR_IO
ERR_LASTCODE = _mpi.ERR_LASTCODE

def Get_error_class(errorcode):
    return _mpi.error_class(errorcode)



def Get_error_string(errorcode):
    return _mpi.error_string(errorcode)



def SWIG(cls):
    try:
        import mpi4py._mpi_swig as _swig
        _as = getattr(_swig, 'as_' + cls.__name__)
        _from = getattr(_swig, 'from_' + cls.__name__)

        def As_swig(self):
            return _as(self)



        def From_swig(cls, obj):
            return cls(_from(obj))


    except ImportError:
        _swig = None

        def As_swig(self):
            raise ImportError('SWIG support not available')



        def From_swig(cls, obj):
            raise ImportError('SWIG support not available')


    cls.As_swig = As_swig
    cls.From_swig = classmethod(From_swig)
    cls.this = property(As_swig, doc='SWIG handle')
    cls.thisown = property(lambda self: 0, doc='SWIG handle ownership')
    del _swig
    del As_swig
    del From_swig


for klass in (Datatype,
 Status,
 Request,
 Op,
 Info,
 Group,
 Comm,
 Win,
 File,
 Errhandler):
    SWIG(klass)

del SWIG
del klass
WORLD_SIZE = _mpi.WORLD_SIZE
WORLD_RANK = _mpi.WORLD_RANK
size = _mpi.WORLD_SIZE
rank = _mpi.WORLD_RANK
zero = WORLD_RANK == 0
last = WORLD_RANK == WORLD_SIZE - 1
even = WORLD_RANK % 2 != 1
odd = WORLD_RANK % 2 == 1

def _mpi_init():
    try:
        _mpi._set_exception(Exception)
    except StandardError:
        pass


_mpi_init()
del _mpi_init

def _mpi_fini():
    try:
        _mpi._del_exception()
    except StandardError:
        pass
    try:
        if not _mpi.initialized():
            return 
        if _mpi.finalized():
            return 
    except StandardError:
        return 


import atexit
atexit.register(_mpi_fini)
del atexit
del _mpi_fini

def distribute(N, B, i):
    return _mpi.distribute(N, B, i)



def pprint(message = None, comm = None, root = 0):
    if comm is None:
        comm = COMM_WORLD
    inbuf = comm.SERIALIZER.dump(message)
    result = _mpi.gather_string(inbuf, None, root, comm)
    if comm.Get_rank() == root:
        for i in result:
            msg = comm.SERIALIZER.load(i)
            print msg




def rprint(message = None, comm = None, root = 0):
    if comm is None:
        comm = COMM_WORLD
    if comm.Get_rank() == root:
        print message



