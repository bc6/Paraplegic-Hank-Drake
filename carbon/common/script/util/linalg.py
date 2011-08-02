import math
import types
import sys
TINY = 0.0

class VectorOP(object):

    def __Coarce(self, o):
        if hasattr(o, '__len__') or hasattr(o, '__iter__'):
            return o
        return [ o for i in xrange(len(self)) ]



    def Set(self, other):
        self[:] = other



    def __iadd__(self, other):
        other = self._VectorOP__Coarce(other)
        for i in xrange(len(self)):
            self[i] += other[i]

        return self



    def __isub__(self, other):
        other = self._VectorOP__Coarce(other)
        for i in xrange(len(self)):
            self[i] -= other[i]

        return self



    def __imul__(self, other):
        other = self._VectorOP__Coarce(other)
        for i in xrange(len(self)):
            self[i] *= other[i]

        return self



    def __idiv__(self, other):
        other = self._VectorOP__Coarce(other)
        for i in xrange(len(self)):
            self[i] /= other[i]

        return self



    def Negate(self):
        for i in xrange(len(self)):
            self[i] = -self[i]




    def Dot(self, other):
        r = self[0] * other[0]
        for i in range(1, len(self)):
            r += self[i] * other[i]

        return r



    def Len2(self):
        return self.Dot(self)



    def Len(self):
        return math.sqrt(self.Len2())



    def __abs__(self):
        return self.Len()



    def Normalize(self):
        self /= self.Len()




def Mixin(current, cls):
    current.update(cls.__dict__)



class Vector(list):
    Mixin(locals(), VectorOP)

    def __init__(self, a = None, b = 0):
        try:
            list.__init__(self, [ b for i in range(a) ])
        except TypeError:
            list.__init__(self, a)
            sys.exc_clear()



    def Ones(length, item = 1.0):
        return Vector(length, item)


    Ones = staticmethod(Ones)

    def Copy(self):
        return Vector(self)



    def LMatrix(self):
        return Matrix((1, len(self)), self)



    def CMatrix(self):
        return Matrix((len(self), 1), self)



    def __MatchSize(self, other):
        if len(self) != len(other):
            raise TypeError, 'operands have mismatching sizes'



    def __Vectorize(self, obj):
        if not isinstance(obj, Vector):
            return Vector(len(self), obj)
        return obj



    def __add__(self, op):
        r = Vector(self)
        r += op
        return r



    def __radd__(self, op):
        return self + op



    def __sub__(self, op):
        r = Vector(self)
        r -= op
        return r



    def __rsub__(self, op):
        return self._Vector__Vectorize(op) - self



    def __mul__(self, op):
        r = Vector(self)
        r *= op
        return r



    def __rmul__(self, op):
        return self._Vector__Vectorize(op) * self



    def __div__(self, op):
        r = Vector(self)
        r /= op
        return r



    def __rdiv__(self, other):
        return self._Vector__Vectorize(other) / self



    def __neg__(self):
        return Vector([ -each for each in self ])



    def Cross(self, other):
        return Vector([self[1] * other[2] - other[1] * self[2], -(self[0] * other[2] - other[0] * self[2]), self[0] * other[1] - other[0] * self[1]])



    def Normal(self):
        return self / abs(self)




class Matrix(Vector):
    __slots__ = 'dim'

    def __init__(self, a, b = None):
        if isinstance(a, Matrix) and b is None:
            super(Matrix, self).__init__(a)
            self.dim = a.dim
            return 
        self.dim = a
        l = a[0] * a[1]
        if b is None:
            super(Matrix, self).__init__(l)
        elif len(b) != l:
            raise ValueError, 'operand has incorrect length'
        super(Matrix, self).__init__(b)



    def __getitem__(self, idx):
        if isinstance(idx, types.TupleType):
            return super(Matrix, self).__getitem__(idx[0] * self.dim[1] + idx[1])
        return super(Matrix, self).__getitem__(idx)



    def __setitem__(self, idx, val):
        if isinstance(idx, types.TupleType):
            super(Matrix, self).__setitem__(idx[0] * self.dim[1] + idx[1], val)
        else:
            super(Matrix, self).__setitem__(idx, val)



    def Ones(dim, item = 1.0):
        return Matrix(dim, [item] * dim[0] * dim[1])


    Ones = staticmethod(Ones)

    def I(n, item = 1.0):
        tmp = [item] + ([0.0] * n + [item]) * (n - 1)
        return Matrix((n, n), tmp)


    I = staticmethod(I)

    def FromLines(lines):
        l = len(lines)
        c = len(lines[0])
        v = []
        for line in lines:
            v.extend(line)

        return Matrix((l, c), v)


    FromLines = staticmethod(FromLines)

    def FromCols(cols):
        c = len(cols)
        l = len(cols[0])
        v = []
        for i in range(l):
            v.extend([ cols[j][i] for j in range(c) ])

        return Matrix((l, c), v)


    FromCols = staticmethod(FromCols)

    def __repr__(self):
        return '{Matrix %s %s}' % (self.dim, super(Matrix, self).__repr__())



    def __str__(self):
        return '\n'.join([ str(self.Line(l)) for l in range(self.dim[0]) ])



    def Copy(self):
        return Matrix(self)



    def Set(self, other):
        self[:] = other
        self.dim = other.dim



    def Dim(self):
        return self.dim



    def __Matrixize(self, other):
        if isinstance(other, Matrix):
            return other
        if isinstance(other, Vector):
            return other.LMatrix()
        return self.Ones(self.dim, other)



    def __add__(self, other):
        r = self.Copy()
        r += other
        return r



    def __radd__(self, other):
        return self._Matrix__Matrixize(other) + self



    def __sub__(self, other):
        r = self.Copy()
        r -= other
        return r



    def __rsub__(self, other):
        return self._Matrix__Matrixize(other) - self



    def __neg__(self):
        r = self.Copy()
        r.Negate()
        return r



    def __mul__(self, other):
        if not isinstance(other, Matrix):
            if not isinstance(other, Vector):
                return Matrix(self.dim, super(Matrix, self).__mul__(other))
            other = other.CMatrix()
        d = self.dim[1]
        if d != other.dim[0]:
            raise ValueError, 'invalid operand (dim%s * dim%s)' % (self.dim, other.dim)
        (nl, nc,) = (self.dim[0], other.dim[1])
        dim = (self.dim[0], other.dim[1])
        r = Matrix((nl, nc))
        nc = range(nc)
        d = range(1, d)
        for l in xrange(nl):
            for c in nc:
                v = self[(l, 0)] * other[(0, c)]
                for i in d:
                    v += self[(l, i)] * other[(i, c)]

                r[(l, c)] = v


        return r
        for l in xrange(nl):
            line = Line(self, l)
            for c in xrange(nc):
                r[(l, c)] = line.Dot(Column(other, c))





    def __imul__(self, other):
        self.Set(self * other)
        return self



    def __rmul__(self, other):
        return self._Matrix__Matrixize(other) * self



    def __div__(self, other):
        if isinstance(other, Matrix):
            if other.dim[0] < 3:
                return self * other.Inv()
            return other.Trans().Solve(self.Trans()).Trans()
        super(Matrix, self).__div__(other)



    def __idiv__(self, other):
        self.Set(self / other)
        return self



    def __rdiv__(self, other):
        return self._Matrix__Matrixize(other) / self



    def Line(self, l):
        return Vector(self[(l * self.dim[1]):((l + 1) * self.dim[1])])



    def Lines(self):
        return [ self.Line(l) for l in range(self.dim[0]) ]



    def Col(self, c):
        v = [ self[i] for i in range(c, len(self), self.dim[1]) ]
        return Vector(v)



    def Cols(self):
        return [ self.Col(c) for c in range(self.dim[1]) ]



    def Sub(self, start, size):
        end = (start[0] + size[0], start[1] + size[1])
        v = []
        for l in range(start[0], end[0]):
            v.extend(self.Line(l)[start[1]:end[1]])

        return Matrix(size, v)



    def JoinH(self, other):
        r = []
        for l in range(self.dim[0]):
            a = self.Line(l)
            a.extend(other.Line(l))
            r.extend(a)

        return Matrix((self.dim[0], self.dim[1] + other.dim[1]), r)



    def JoinV(self, other):
        a = self.Copy()
        a.extend(other)
        a.dim[0] += other.dim[0]
        return a



    def Det(self):
        dim = self.dim
        if dim[0] == 1:
            return self[(0, 0)]
        f = 1
        s = 0
        for c in range(self.dim[1]):
            a = self.Sub((1, 0), (dim[0] - 1, c))
            b = self.Sub((1, c + 1), (dim[0] - 1, dim[1] - c - 1))
            subm = a.JoinH(b)
            s += f * self[(0, c)] * subm.Det()
            f *= -1

        return s



    def Det2(self):
        a = self.Copy()
        (idx, even,) = a.LUDecompose()
        d = 1.0
        for i in range(a.dim[0]):
            d *= a[(i, i)]

        if not even:
            d *= -1.0
        return d



    def Transpose(self):
        (l, c,) = (self.dim[1], self.dim[0])
        if l < 2 or c < 2:
            return Matrix((l, c), self)
        r = Matrix((l, c))
        for i in range(l * c):
            r[i % l * c + i / l] = self[i]

        return r


    Trans = Transpose

    def Solve(self, other):
        dc = self.Copy()
        (index, even,) = dc.LUDecompose()
        if isinstance(other, Matrix):
            cols = other.Cols()
            for col in cols:
                dc.LUBacksubstitute(index, col)

            return self.FromCols(cols)
        else:
            v = Vector(other)
            dc.LUBacksubstitute(index, v)
            return v



    def Inverse(self):
        if self.dim == (1, 1):
            det = self[(0, 0)]
            if not det:
                raise ValueError, 'singular matrix (%s)' % self
            return Matrix((1, 1), [1.0 / self[(0, 0)]])
        if self.dim == (2, 2):
            det = self[(0, 0)] * self[(1, 1)] - self[(1, 0)] * self[(0, 1)]
            if not det:
                raise ValueError, 'singular matrix (%s)' % self
            return Matrix((2, 2), [self[(1, 1)] / det,
             -self[(0, 1)] / det,
             -self[(1, 0)] / det,
             self[(0, 0)] / det])
        return self.Solve(self.I(self.dim[0]))


    Inv = Inverse

    def Invert(self):
        self.Set(self.Inverse())



    def LUDecompose(self):
        n = self.dim[0]
        if n != self.dim[1]:
            raise ValueError, 'Matrix must be square'
        vv = []
        even = True
        for i in range(n):
            big = 0.0
            for j in range(n):
                temp = abs(self[(i, j)])
                if temp > big:
                    big = temp

            if not big:
                raise ValueError, 'singular matrix (%s)' % self
            vv.append(1.0 / big)

        indx = []
        for j in range(n):
            for i in range(j):
                sum = self[(i, j)]
                for k in range(i):
                    sum -= self[(i, k)] * self[(k, j)]

                self[(i, j)] = sum

            big = 0.0
            for i in range(j, n):
                sum = self[(i, j)]
                for k in range(j):
                    sum -= self[(i, k)] * self[(k, j)]

                self[(i, j)] = sum
                dum = vv[i] * abs(sum)
                if dum >= big:
                    big = dum
                    imax = i

            if j != imax:
                for k in range(n):
                    (self[(imax, k)], self[(j, k)],) = (self[(j, k)], self[(imax, k)])

                even = not even
                vv[imax] = vv[j]
            indx.append(imax)
            if not self[(j, j)]:
                raise ValueError, 'singular matrix'
                self[(j, j)] = TINY
            if j != n:
                dum = 1.0 / self[(j, j)]
                for i in range(j + 1, n):
                    self[(i, j)] *= dum


        return (indx, even)



    def LUBacksubstitute(self, indx, b):
        ii = None
        n = self.dim[0]
        for i in range(n):
            ip = indx[i]
            (sum, b[ip],) = (b[ip], b[i])
            if ii is not None:
                for j in range(ii, i):
                    sum -= self[(i, j)] * b[j]

            elif sum:
                ii = i
            b[i] = sum

        for i in range(n - 1, -1, -1):
            sum = b[i]
            for j in range(i + 1, n):
                sum -= self[(i, j)] * b[j]

            b[i] = float(sum) / self[(i, i)]





class Column(VectorOP):
    __slots__ = ['m', 'c']

    def __init__(self, m, c):
        (self.m, self.c,) = (m, c)



    def __getitem__(self, i):
        return self.m[(i, self.c)]



    def __setitem__(self, i, v):
        self.m[(i, self.c)] = v



    def __len__(self):
        return self.m.dim[0]




class Line(VectorOP):
    __slots__ = ['m', 'l']

    def __init__(self, m, l):
        (self.m, self.l,) = (m, l)



    def __getitem__(self, i):
        return self.m[(self.l, i)]



    def __setitem__(self, i, v):
        self.m[(self.l, i)] = v



    def __len__(self):
        return self.m.dim[1]



exports = {'linalg.Vector': Vector,
 'linalg.Matrix': Matrix}

