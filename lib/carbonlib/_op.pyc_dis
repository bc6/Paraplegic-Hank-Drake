#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\_op.py
__author__ = 'Lisandro Dalcin'
__credits__ = 'MPI Forum, MPICH Team, Open MPI Team.'
__date__ = '13 Oct 2006'
__version__ = '0.4.0'
__revision__ = '$Id: _op.py 16 2006-11-11 23:02:20Z dalcinl $'

def MAX(x, y):
    return max(x, y)


def MIN(x, y):
    return min(x, y)


def SUM(x, y):
    return x + y


def PROD(x, y):
    return x * y


def BAND(x, y):
    return x & y


def BOR(x, y):
    return x | y


def BXOR(x, y):
    return x ^ y


def LAND(x, y):
    return bool(x) & bool(y)


def LOR(x, y):
    return bool(x) | bool(y)


def LXOR(x, y):
    return bool(x) ^ bool(y)


def MAXLOC(x, y):
    u, i = x
    v, j = y
    w = max(u, v)
    if u == v:
        k = min(i, j)
    elif u < v:
        k = j
    else:
        k = i
    return (w, k)


def MINLOC(x, y):
    u, i = x
    v, j = y
    w = min(u, v)
    if u == v:
        k = min(i, j)
    elif u < v:
        k = i
    else:
        k = j
    return (w, k)


def REPLACE(x, y):
    return x