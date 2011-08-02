import os
import sys
try:
    from functools import wraps
except ImportError:
    import unittest2.compatibility

    def wraps(_):

        def _wraps(func):
            return func


        return _wraps


if not hasattr(os, 'relpath'):
    if os.path is sys.modules.get('ntpath'):

        def relpath(path, start = os.path.curdir):
            if not path:
                raise ValueError('no path specified')
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
            if start_list[0].lower() != path_list[0].lower():
                (unc_path, rest,) = os.path.splitunc(path)
                (unc_start, rest,) = os.path.splitunc(start)
                if bool(unc_path) ^ bool(unc_start):
                    raise ValueError('Cannot mix UNC and non-UNC paths (%s and %s)' % (path, start))
                else:
                    raise ValueError('path is on drive %s, start on drive %s' % (path_list[0], start_list[0]))
            for i in range(min(len(start_list), len(path_list))):
                if start_list[i].lower() != path_list[i].lower():
                    break
            else:
                i += 1

            rel_list = [os.path.pardir] * (len(start_list) - i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)


    else:

        def relpath(path, start = os.path.curdir):
            if not path:
                raise ValueError('no path specified')
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
            i = len(os.path.commonprefix([start_list, path_list]))
            rel_list = [os.path.pardir] * (len(start_list) - i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)


    os.path.relpath = relpath

