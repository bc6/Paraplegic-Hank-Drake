#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\traceback2.py
import linecache
from traceback import format_exception_only
import sys
import pprint
FORMAT_NORMAL = 0
FORMAT_LOGSRV = 1
FORMAT_SINGLE = 2

def print_exc(limit = None, file = None, show_locals = 0, format = FORMAT_NORMAL):
    _getfile(file).write(format_exc(limit, show_locals, format))


def format_exc(limit = None, show_locals = 0, format = FORMAT_NORMAL):
    etype, value, tb = sys.exc_info()
    try:
        return ''.join(format_exception(etype, value, tb, limit, show_locals, format))
    finally:
        del etype
        del value
        del tb


def print_exception(etype, value, tb, limit = None, file = None, show_locals = 0, format = FORMAT_NORMAL):
    _getfile(file).write(''.join(format_exception(etype, value, tb, limit, show_locals, format)))


def format_exception(etype, value, tb, limit = None, show_locals = 0, format = FORMAT_NORMAL):
    if tb:
        list = ['Traceback (most recent call last):\n']
        list = list + format_tb(tb, limit, show_locals, format)
    else:
        list = []
    return list + format_exception_only(etype, value)


def print_stack(f = None, limit = None, up = 0, show_locals = 0, format = FORMAT_NORMAL, file = None):
    if f is None:
        up += 1
    _getfile(file).write(''.join(format_stack(f, limit, up, show_locals, format)))


def format_stack(f = None, limit = None, up = 0, show_locals = 0, format = FORMAT_NORMAL):
    if f is None:
        up += 1
    return format_list(extract_stack(f, limit, up, show_locals), show_locals, format)


def print_tb(tb, limit = None, file = None, show_locals = 0, format = FORMAT_NORMAL):
    _getfile(file).write(''.join(format_tb(tb, limit, show_locals)))


def format_tb(tb, limit = None, show_locals = 0, format = FORMAT_NORMAL):
    return format_list(extract_tb(tb, limit, show_locals), show_locals, format)


def format_list(extracted_list, show_locals = 0, format = FORMAT_NORMAL):
    if show_locals < 0:
        start_locals = 0
    else:
        start_locals = len(extracted_list) - show_locals
    data = []
    for i, (filename, lineno, name, line, f_locals) in enumerate(extracted_list):
        if format & FORMAT_NORMAL == FORMAT_NORMAL:
            item = '  File "%s", line %d, in %s\n' % (filename, lineno, name)
            if line:
                item += '    %s\n' % line.strip()
        if format & FORMAT_LOGSRV:
            item = '%s(%s) %s' % (filename, lineno, name)
        else:
            item = '  File "%s", line %d, in %s' % (filename, lineno, name)
        if line:
            if format & FORMAT_SINGLE:
                item += ' : %s\n' % (line.strip(),)
            else:
                item += '\n    %s\n' % (line.strip(),)
        else:
            item += '\n'
        if i >= start_locals:
            item += ''.join(_format_locals(f_locals, format))
        data.append(item)

    return data


def _format_locals(f_locals, format):
    lines = []
    if f_locals is None:
        return lines
    for key, value in f_locals.iteritems():
        if format & FORMAT_LOGSRV:
            extra = '        %s = ' % (key,)
        else:
            extra = '%20s = ' % (key,)
        try:
            width = 253 - len(extra)
            val = pprint.pformat(value, depth=1, width=width)
            if len(val) > 1024:
                val = val[:1024] + '...'
            vlines = val.splitlines()
            if len(vlines) > 4:
                vlines[4:] = ['...']
            for i in xrange(1, len(vlines)):
                vlines[i] = ' ' * 23 + vlines[i]

            extra += '\n'.join(vlines) + '\n'
        except Exception as e:
            try:
                extra += '<error printing value: %r>' % (e,)
            except Exception:
                extra += '<error printing value>'

        lines.append(extra)

    return lines


def extract_tb(tb, limit = None, extract_locals = 0):
    frames = []
    n = 1
    while tb is not None and (limit is None or n < limit):
        frames.append((tb.tb_frame, tb.tb_lineno))
        tb = tb.tb_next
        n += 1

    return _extract_frames(frames, extract_locals)


def extract_stack(f = None, limit = None, up = 0, extract_locals = 0):
    if f is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            f = sys.exc_info()[2].tb_frame.f_back

    frames = []
    n = 0
    while f is not None and (limit is None or n < limit + up):
        frames.append((f, f.f_lineno))
        f = f.f_back
        n = n + 1

    frames.reverse()
    if up > 0:
        del frames[-up:]
    return _extract_frames(frames, extract_locals)


def _extract_frames(frames, extract_locals = 0):
    result = []
    if extract_locals >= 0:
        j = len(frames) - extract_locals
    else:
        j = 0
    for i, (f, lineno) in enumerate(frames):
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None
        locals = f.f_locals if i >= j else None
        result.append((filename,
         lineno,
         name,
         line,
         locals))

    return result


def _getfile(file):
    if file is None:
        file = sys.stderr
    return file