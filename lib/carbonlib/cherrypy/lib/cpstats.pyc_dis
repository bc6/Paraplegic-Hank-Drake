#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\cherrypy\lib\cpstats.py
import logging
if not hasattr(logging, 'statistics'):
    logging.statistics = {}

def extrapolate_statistics(scope):
    c = {}
    for k, v in list(scope.items()):
        if isinstance(v, dict):
            v = extrapolate_statistics(v)
        elif isinstance(v, (list, tuple)):
            v = [ extrapolate_statistics(record) for record in v ]
        elif hasattr(v, '__call__'):
            v = v(scope)
        c[k] = v

    return c


import threading
import time
import cherrypy
appstats = logging.statistics.setdefault('CherryPy Applications', {})
appstats.update({'Enabled': True,
 'Bytes Read/Request': lambda s: s['Total Requests'] and s['Total Bytes Read'] / float(s['Total Requests']) or 0.0,
 'Bytes Read/Second': lambda s: s['Total Bytes Read'] / s['Uptime'](s),
 'Bytes Written/Request': lambda s: s['Total Requests'] and s['Total Bytes Written'] / float(s['Total Requests']) or 0.0,
 'Bytes Written/Second': lambda s: s['Total Bytes Written'] / s['Uptime'](s),
 'Current Time': lambda s: time.time(),
 'Current Requests': 0,
 'Requests/Second': lambda s: float(s['Total Requests']) / s['Uptime'](s),
 'Server Version': cherrypy.__version__,
 'Start Time': time.time(),
 'Total Bytes Read': 0,
 'Total Bytes Written': 0,
 'Total Requests': 0,
 'Total Time': 0,
 'Uptime': lambda s: time.time() - s['Start Time'],
 'Requests': {}})
proc_time = lambda s: time.time() - s['Start Time']

class ByteCountWrapper(object):

    def __init__(self, rfile):
        self.rfile = rfile
        self.bytes_read = 0

    def read(self, size = -1):
        data = self.rfile.read(size)
        self.bytes_read += len(data)
        return data

    def readline(self, size = -1):
        data = self.rfile.readline(size)
        self.bytes_read += len(data)
        return data

    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()

        return lines

    def close(self):
        self.rfile.close()

    def __iter__(self):
        return self

    def next(self):
        data = self.rfile.next()
        self.bytes_read += len(data)
        return data


average_uriset_time = lambda s: s['Count'] and s['Sum'] / s['Count'] or 0

class StatsTool(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_end_request', self.record_stop)

    def _setup(self):
        if appstats.get('Enabled', False):
            cherrypy.Tool._setup(self)
            self.record_start()

    def record_start(self):
        request = cherrypy.serving.request
        if not hasattr(request.rfile, 'bytes_read'):
            request.rfile = ByteCountWrapper(request.rfile)
            request.body.fp = request.rfile
        r = request.remote
        appstats['Current Requests'] += 1
        appstats['Total Requests'] += 1
        appstats['Requests'][threading._get_ident()] = {'Bytes Read': None,
         'Bytes Written': None,
         'Client': lambda s: '%s:%s' % (r.ip, r.port),
         'End Time': None,
         'Processing Time': proc_time,
         'Request-Line': request.request_line,
         'Response Status': None,
         'Start Time': time.time()}

    def record_stop(self, uriset = None, slow_queries = 1.0, slow_queries_count = 100, debug = False, **kwargs):
        w = appstats['Requests'][threading._get_ident()]
        r = cherrypy.request.rfile.bytes_read
        w['Bytes Read'] = r
        appstats['Total Bytes Read'] += r
        if cherrypy.response.stream:
            w['Bytes Written'] = 'chunked'
        else:
            cl = int(cherrypy.response.headers.get('Content-Length', 0))
            w['Bytes Written'] = cl
            appstats['Total Bytes Written'] += cl
        w['Response Status'] = cherrypy.response.status
        w['End Time'] = time.time()
        p = w['End Time'] - w['Start Time']
        w['Processing Time'] = p
        appstats['Total Time'] += p
        appstats['Current Requests'] -= 1
        if debug:
            cherrypy.log('Stats recorded: %s' % repr(w), 'TOOLS.CPSTATS')
        if uriset:
            rs = appstats.setdefault('URI Set Tracking', {})
            r = rs.setdefault(uriset, {'Min': None,
             'Max': None,
             'Count': 0,
             'Sum': 0,
             'Avg': average_uriset_time})
            if r['Min'] is None or p < r['Min']:
                r['Min'] = p
            if r['Max'] is None or p > r['Max']:
                r['Max'] = p
            r['Count'] += 1
            r['Sum'] += p
        if slow_queries and p > slow_queries:
            sq = appstats.setdefault('Slow Queries', [])
            sq.append(w.copy())
            if len(sq) > slow_queries_count:
                sq.pop(0)


import cherrypy
cherrypy.tools.cpstats = StatsTool()
import os
thisdir = os.path.abspath(os.path.dirname(__file__))
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None

missing = object()
locale_date = lambda v: time.strftime('%c', time.gmtime(v))
iso_format = lambda v: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(v))

def pause_resume(ns):

    def _pause_resume(enabled):
        pause_disabled = ''
        resume_disabled = ''
        if enabled:
            resume_disabled = 'disabled="disabled" '
        else:
            pause_disabled = 'disabled="disabled" '
        return '\n            <form action="pause" method="POST" style="display:inline">\n            <input type="hidden" name="namespace" value="%s" />\n            <input type="submit" value="Pause" %s/>\n            </form>\n            <form action="resume" method="POST" style="display:inline">\n            <input type="hidden" name="namespace" value="%s" />\n            <input type="submit" value="Resume" %s/>\n            </form>\n            ' % (ns,
         pause_disabled,
         ns,
         resume_disabled)

    return _pause_resume


class StatsPage(object):
    formatting = {'CherryPy Applications': {'Enabled': pause_resume('CherryPy Applications'),
                               'Bytes Read/Request': '%.3f',
                               'Bytes Read/Second': '%.3f',
                               'Bytes Written/Request': '%.3f',
                               'Bytes Written/Second': '%.3f',
                               'Current Time': iso_format,
                               'Requests/Second': '%.3f',
                               'Start Time': iso_format,
                               'Total Time': '%.3f',
                               'Uptime': '%.3f',
                               'Slow Queries': {'End Time': None,
                                                'Processing Time': '%.3f',
                                                'Start Time': iso_format},
                               'URI Set Tracking': {'Avg': '%.3f',
                                                    'Max': '%.3f',
                                                    'Min': '%.3f',
                                                    'Sum': '%.3f'},
                               'Requests': {'Bytes Read': '%s',
                                            'Bytes Written': '%s',
                                            'End Time': None,
                                            'Processing Time': '%.3f',
                                            'Start Time': None}},
     'CherryPy WSGIServer': {'Enabled': pause_resume('CherryPy WSGIServer'),
                             'Connections/second': '%.3f',
                             'Start time': iso_format}}

    def index(self):
        yield '\n<html>\n<head>\n    <title>Statistics</title>\n<style>\n\nth, td {\n    padding: 0.25em 0.5em;\n    border: 1px solid #666699;\n}\n\ntable {\n    border-collapse: collapse;\n}\n\ntable.stats1 {\n    width: 100%;\n}\n\ntable.stats1 th {\n    font-weight: bold;\n    text-align: right;\n    background-color: #CCD5DD;\n}\n\ntable.stats2, h2 {\n    margin-left: 50px;\n}\n\ntable.stats2 th {\n    font-weight: bold;\n    text-align: center;\n    background-color: #CCD5DD;\n}\n\n</style>\n</head>\n<body>\n'
        for title, scalars, collections in self.get_namespaces():
            yield "\n<h1>%s</h1>\n\n<table class='stats1'>\n    <tbody>\n" % title
            for i, (key, value) in enumerate(scalars):
                colnum = i % 3
                if colnum == 0:
                    yield '\n        <tr>'
                yield "\n            <th>%(key)s</th><td id='%(title)s-%(key)s'>%(value)s</td>" % vars()
                if colnum == 2:
                    yield '\n        </tr>'

            if colnum == 0:
                yield '\n            <th></th><td></td>\n            <th></th><td></td>\n        </tr>'
            elif colnum == 1:
                yield '\n            <th></th><td></td>\n        </tr>'
            yield '\n    </tbody>\n</table>'
            for subtitle, headers, subrows in collections:
                yield "\n<h2>%s</h2>\n<table class='stats2'>\n    <thead>\n        <tr>" % subtitle
                for key in headers:
                    yield '\n            <th>%s</th>' % key

                yield '\n        </tr>\n    </thead>\n    <tbody>'
                for subrow in subrows:
                    yield '\n        <tr>'
                    for value in subrow:
                        yield '\n            <td>%s</td>' % value

                    yield '\n        </tr>'

                yield '\n    </tbody>\n</table>'

        yield '\n</body>\n</html>\n'

    index.exposed = True

    def get_namespaces(self):
        s = extrapolate_statistics(logging.statistics)
        for title, ns in sorted(s.items()):
            scalars = []
            collections = []
            ns_fmt = self.formatting.get(title, {})
            for k, v in sorted(ns.items()):
                fmt = ns_fmt.get(k, {})
                if isinstance(v, dict):
                    headers, subrows = self.get_dict_collection(v, fmt)
                    collections.append((k, ['ID'] + headers, subrows))
                elif isinstance(v, (list, tuple)):
                    headers, subrows = self.get_list_collection(v, fmt)
                    collections.append((k, headers, subrows))
                else:
                    format = ns_fmt.get(k, missing)
                    if format is None:
                        continue
                    if hasattr(format, '__call__'):
                        v = format(v)
                    elif format is not missing:
                        v = format % v
                    scalars.append((k, v))

            yield (title, scalars, collections)

    def get_dict_collection(self, v, formatting):
        headers = []
        for record in v.itervalues():
            for k3 in record:
                format = formatting.get(k3, missing)
                if format is None:
                    continue
                if k3 not in headers:
                    headers.append(k3)

        headers.sort()
        subrows = []
        for k2, record in sorted(v.items()):
            subrow = [k2]
            for k3 in headers:
                v3 = record.get(k3, '')
                format = formatting.get(k3, missing)
                if format is None:
                    continue
                if hasattr(format, '__call__'):
                    v3 = format(v3)
                elif format is not missing:
                    v3 = format % v3
                subrow.append(v3)

            subrows.append(subrow)

        return (headers, subrows)

    def get_list_collection(self, v, formatting):
        headers = []
        for record in v:
            for k3 in record:
                format = formatting.get(k3, missing)
                if format is None:
                    continue
                if k3 not in headers:
                    headers.append(k3)

        headers.sort()
        subrows = []
        for record in v:
            subrow = []
            for k3 in headers:
                v3 = record.get(k3, '')
                format = formatting.get(k3, missing)
                if format is None:
                    continue
                if hasattr(format, '__call__'):
                    v3 = format(v3)
                elif format is not missing:
                    v3 = format % v3
                subrow.append(v3)

            subrows.append(subrow)

        return (headers, subrows)

    if json is not None:

        def data(self):
            s = extrapolate_statistics(logging.statistics)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return json.dumps(s, sort_keys=True, indent=4)

        data.exposed = True

    def pause(self, namespace):
        logging.statistics.get(namespace, {})['Enabled'] = False
        raise cherrypy.HTTPRedirect('./')

    pause.exposed = True
    pause.cp_config = {'tools.allow.on': True,
     'tools.allow.methods': ['POST']}

    def resume(self, namespace):
        logging.statistics.get(namespace, {})['Enabled'] = True
        raise cherrypy.HTTPRedirect('./')

    resume.exposed = True
    resume.cp_config = {'tools.allow.on': True,
     'tools.allow.methods': ['POST']}