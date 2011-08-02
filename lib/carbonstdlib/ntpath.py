import os
import sys
import stat
import genericpath
import warnings
from genericpath import *
__all__ = ['normcase',
 'isabs',
 'join',
 'splitdrive',
 'split',
 'splitext',
 'basename',
 'dirname',
 'commonprefix',
 'getsize',
 'getmtime',
 'getatime',
 'getctime',
 'islink',
 'exists',
 'lexists',
 'isdir',
 'isfile',
 'ismount',
 'walk',
 'expanduser',
 'expandvars',
 'normpath',
 'abspath',
 'splitunc',
 'curdir',
 'pardir',
 'sep',
 'pathsep',
 'defpath',
 'altsep',
 'extsep',
 'devnull',
 'realpath',
 'supports_unicode_filenames',
 'relpath']
curdir = '.'
pardir = '..'
extsep = '.'
sep = '\\'
pathsep = ';'
altsep = '/'
defpath = '.;C:\\bin'
if 'ce' in sys.builtin_module_names:
    defpath = '\\Windows'
elif 'os2' in sys.builtin_module_names:
    altsep = '/'
devnull = 'nul'

def normcase(s):
    return s.replace('/', '\\').lower()



def isabs(s):
    s = splitdrive(s)[1]
    return s != '' and s[:1] in '/\\'



def join(a, *p):
    path = a
    for b in p:
        b_wins = 0
        if path == '':
            b_wins = 1
        elif isabs(b):
            if path[1:2] != ':' or b[1:2] == ':':
                b_wins = 1
            elif len(path) > 3 or len(path) == 3 and path[-1] not in '/\\':
                b_wins = 1
        if b_wins:
            path = b
        elif path[-1] in '/\\':
            if b and b[0] in '/\\':
                path += b[1:]
            else:
                path += b
        elif path[-1] == ':':
            path += b
        elif b:
            if b[0] in '/\\':
                path += b
            else:
                path += '\\' + b
        else:
            path += '\\'

    return path



def splitdrive(p):
    if p[1:2] == ':':
        return (p[0:2], p[2:])
    return ('', p)



def splitunc(p):
    if p[1:2] == ':':
        return ('', p)
    firstTwo = p[0:2]
    if firstTwo == '//' or firstTwo == '\\\\':
        normp = normcase(p)
        index = normp.find('\\', 2)
        if index == -1:
            return ('', p)
        index = normp.find('\\', index + 1)
        if index == -1:
            index = len(p)
        return (p[:index], p[index:])
    return ('', p)



def split(p):
    (d, p,) = splitdrive(p)
    i = len(p)
    while i and p[(i - 1)] not in '/\\':
        i = i - 1

    (head, tail,) = (p[:i], p[i:])
    head2 = head
    while head2 and head2[-1] in '/\\':
        head2 = head2[:-1]

    head = head2 or head
    return (d + head, tail)



def splitext(p):
    return genericpath._splitext(p, sep, altsep, extsep)


splitext.__doc__ = genericpath._splitext.__doc__

def basename(p):
    return split(p)[1]



def dirname(p):
    return split(p)[0]



def islink(path):
    return False


lexists = exists

def ismount(path):
    (unc, rest,) = splitunc(path)
    if unc:
        return rest in ('', '/', '\\')
    p = splitdrive(path)[1]
    return len(p) == 1 and p[0] in '/\\'



def walk(top, func, arg):
    warnings.warnpy3k('In 3.x, os.path.walk is removed in favor of os.walk.', stacklevel=2)
    try:
        names = os.listdir(top)
    except os.error:
        return 
    func(arg, top, names)
    for name in names:
        name = join(top, name)
        if isdir(name):
            walk(name, func, arg)




def expanduser(path):
    if path[:1] != '~':
        return path
    (i, n,) = (1, len(path))
    while i < n and path[i] not in '/\\':
        i = i + 1

    if 'HOME' in os.environ:
        userhome = os.environ['HOME']
    elif 'USERPROFILE' in os.environ:
        userhome = os.environ['USERPROFILE']
    elif 'HOMEPATH' not in os.environ:
        return path
    try:
        drive = os.environ['HOMEDRIVE']
    except KeyError:
        drive = ''
    userhome = join(drive, os.environ['HOMEPATH'])
    if i != 1:
        userhome = join(dirname(userhome), path[1:i])
    return userhome + path[i:]



def expandvars(path):
    if '$' not in path and '%' not in path:
        return path
    import string
    varchars = string.ascii_letters + string.digits + '_-'
    res = ''
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index]
        if c == "'":
            path = path[(index + 1):]
            pathlen = len(path)
            try:
                index = path.index("'")
                res = res + "'" + path[:(index + 1)]
            except ValueError:
                res = res + path
                index = pathlen - 1
        elif c == '%':
            if path[(index + 1):(index + 2)] == '%':
                res = res + c
                index = index + 1
            else:
                path = path[(index + 1):]
                pathlen = len(path)
            try:
                index = path.index('%')
            except ValueError:
                res = res + '%' + path
                index = pathlen - 1
            else:
                var = path[:index]
                if var in os.environ:
                    res = res + os.environ[var]
                else:
                    res = res + '%' + var + '%'
        elif c == '$':
            if path[(index + 1):(index + 2)] == '$':
                res = res + c
                index = index + 1
            elif path[(index + 1):(index + 2)] == '{':
                path = path[(index + 2):]
                pathlen = len(path)
                try:
                    index = path.index('}')
                    var = path[:index]
                    if var in os.environ:
                        res = res + os.environ[var]
                    else:
                        res = res + '${' + var + '}'
                except ValueError:
                    res = res + '${' + path
                    index = pathlen - 1
            else:
                var = ''
                index = index + 1
                c = path[index:(index + 1)]
                while c != '' and c in varchars:
                    var = var + c
                    index = index + 1
                    c = path[index:(index + 1)]

                if var in os.environ:
                    res = res + os.environ[var]
                else:
                    res = res + '$' + var
                if c != '':
                    index = index - 1
        else:
            res = res + c
        index = index + 1

    return res



def normpath(path):
    (backslash, dot,) = (u'\\', u'.') if isinstance(path, unicode) else ('\\', '.')
    if path.startswith(('\\\\.\\', '\\\\?\\')):
        return path
    path = path.replace('/', '\\')
    (prefix, path,) = splitdrive(path)
    if prefix == '':
        while path[:1] == '\\':
            prefix = prefix + backslash
            path = path[1:]

    elif path.startswith('\\'):
        prefix = prefix + backslash
        path = path.lstrip('\\')
    comps = path.split('\\')
    i = 0
    while i < len(comps):
        if comps[i] in ('.', ''):
            del comps[i]
        elif comps[i] == '..':
            if i > 0 and comps[(i - 1)] != '..':
                del comps[i - 1:i + 1]
                i -= 1
            else:
                if i == 0 and prefix.endswith('\\'):
                    del comps[i]
                else:
                    i += 1
        else:
            i += 1

    if not prefix and not comps:
        comps.append(dot)
    return prefix + backslash.join(comps)


try:
    from nt import _getfullpathname
except ImportError:

    def abspath(path):
        if not isabs(path):
            if isinstance(path, unicode):
                cwd = os.getcwdu()
            else:
                cwd = os.getcwd()
            path = join(cwd, path)
        return normpath(path)


else:

    def abspath(path):
        if path:
            try:
                path = _getfullpathname(path)
            except WindowsError:
                pass
        elif isinstance(path, unicode):
            path = os.getcwdu()
        else:
            path = os.getcwd()
        return normpath(path)


realpath = abspath
supports_unicode_filenames = hasattr(sys, 'getwindowsversion') and sys.getwindowsversion()[3] >= 2

def _abspath_split(path):
    abs = abspath(normpath(path))
    (prefix, rest,) = splitunc(abs)
    is_unc = bool(prefix)
    if not is_unc:
        (prefix, rest,) = splitdrive(abs)
    return (is_unc, prefix, [ x for x in rest.split(sep) if x ])



def relpath(path, start = curdir):
    if not path:
        raise ValueError('no path specified')
    (start_is_unc, start_prefix, start_list,) = _abspath_split(start)
    (path_is_unc, path_prefix, path_list,) = _abspath_split(path)
    if path_is_unc ^ start_is_unc:
        raise ValueError('Cannot mix UNC and non-UNC paths (%s and %s)' % (path, start))
    if path_prefix.lower() != start_prefix.lower():
        if path_is_unc:
            raise ValueError('path is on UNC root %s, start on UNC root %s' % (path_prefix, start_prefix))
        else:
            raise ValueError('path is on drive %s, start on drive %s' % (path_prefix, start_prefix))
    i = 0
    for (e1, e2,) in zip(start_list, path_list):
        if e1.lower() != e2.lower():
            break
        i += 1

    rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)



