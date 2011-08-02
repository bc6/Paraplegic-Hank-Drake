import sys
import cgi
import time
import traceback
from cStringIO import StringIO
from thread import get_ident
from paste import httpexceptions
from paste.request import construct_url, parse_formvars
from paste.util.template import HTMLTemplate, bunch
page_template = HTMLTemplate('\n<html>\n <head>\n  <style type="text/css">\n   body {\n     font-family: sans-serif;\n   }\n   table.environ tr td {\n     border-bottom: #bbb 1px solid;\n   }\n   table.environ tr td.bottom {\n     border-bottom: none;\n   }\n   table.thread {\n     border: 1px solid #000;\n     margin-bottom: 1em;\n   }\n   table.thread tr td {\n     border-bottom: #999 1px solid;\n     padding-right: 1em;\n   }\n   table.thread tr td.bottom {\n     border-bottom: none;\n   }\n   table.thread tr.this_thread td {\n     background-color: #006;\n     color: #fff;\n   }\n   a.button {\n     background-color: #ddd;\n     border: #aaa outset 2px;\n     text-decoration: none;\n     margin-top: 10px;\n     font-size: 80%;\n     color: #000;\n   }\n   a.button:hover {\n     background-color: #eee;\n     border: #bbb outset 2px;\n   }\n   a.button:active {\n     border: #bbb inset 2px;\n   }\n  </style>\n  <title>{{title}}</title>\n </head>\n <body>\n  <h1>{{title}}</h1>\n  {{if kill_thread_id}}\n  <div style="background-color: #060; color: #fff;\n              border: 2px solid #000;">\n  Thread {{kill_thread_id}} killed\n  </div>\n  {{endif}}\n  <div>Pool size: {{nworkers}}\n       {{if actual_workers > nworkers}}\n         + {{actual_workers-nworkers}} extra\n       {{endif}}\n       ({{nworkers_used}} used including current request)<br>\n       idle: {{len(track_threads["idle"])}},\n       busy: {{len(track_threads["busy"])}},\n       hung: {{len(track_threads["hung"])}},\n       dying: {{len(track_threads["dying"])}},\n       zombie: {{len(track_threads["zombie"])}}</div>\n\n{{for thread in threads}}\n\n<table class="thread">\n <tr {{if thread.thread_id == this_thread_id}}class="this_thread"{{endif}}>\n  <td>\n   <b>Thread</b>\n   {{if thread.thread_id == this_thread_id}}\n   (<i>this</i> request)\n   {{endif}}</td>\n  <td>\n   <b>{{thread.thread_id}}\n    {{if allow_kill}}\n    <form action="{{script_name}}/kill" method="POST"\n          style="display: inline">\n      <input type="hidden" name="thread_id" value="{{thread.thread_id}}">\n      <input type="submit" value="kill">\n    </form>\n    {{endif}}\n   </b>\n  </td>\n </tr>\n <tr>\n  <td>Time processing request</td>\n  <td>{{thread.time_html|html}}</td>\n </tr>\n <tr>\n  <td>URI</td>\n  <td>{{if thread.uri == \'unknown\'}}\n      unknown\n      {{else}}<a href="{{thread.uri}}">{{thread.uri_short}}</a>\n      {{endif}}\n  </td>\n <tr>\n  <td colspan="2" class="bottom">\n   <a href="#" class="button" style="width: 9em; display: block"\n      onclick="\n        var el = document.getElementById(\'environ-{{thread.thread_id}}\');\n        if (el.style.display) {\n            el.style.display = \'\';\n            this.innerHTML = \'&#9662; Hide environ\';\n        } else {\n            el.style.display = \'none\';\n            this.innerHTML = \'&#9656; Show environ\';\n        }\n        return false\n      ">&#9656; Show environ</a>\n   \n   <div id="environ-{{thread.thread_id}}" style="display: none">\n    {{if thread.environ:}}\n    <table class="environ">\n     {{for loop, item in looper(sorted(thread.environ.items()))}}\n     {{py:key, value=item}}\n     <tr>\n      <td {{if loop.last}}class="bottom"{{endif}}>{{key}}</td>\n      <td {{if loop.last}}class="bottom"{{endif}}>{{value}}</td>\n     </tr>\n     {{endfor}}\n    </table>\n    {{else}}\n    Thread is in process of starting\n    {{endif}}\n   </div>\n\n   {{if thread.traceback}}\n   <a href="#" class="button" style="width: 9em; display: block"\n      onclick="\n        var el = document.getElementById(\'traceback-{{thread.thread_id}}\');\n        if (el.style.display) {\n            el.style.display = \'\';\n            this.innerHTML = \'&#9662; Hide traceback\';\n        } else {\n            el.style.display = \'none\';\n            this.innerHTML = \'&#9656; Show traceback\';\n        }\n        return false\n      ">&#9656; Show traceback</a>\n\n    <div id="traceback-{{thread.thread_id}}" style="display: none">\n      <pre class="traceback">{{thread.traceback}}</pre>\n    </div>\n    {{endif}}\n\n  </td>\n </tr>\n</table>\n\n{{endfor}}\n\n </body>\n</html>\n', name='watchthreads.page_template')

class WatchThreads(object):

    def __init__(self, allow_kill = False):
        self.allow_kill = allow_kill



    def __call__(self, environ, start_response):
        if 'paste.httpserver.thread_pool' not in environ:
            start_response('403 Forbidden', [('Content-type', 'text/plain')])
            return ['You must use the threaded Paste HTTP server to use this application']
        else:
            if environ.get('PATH_INFO') == '/kill':
                return self.kill(environ, start_response)
            return self.show(environ, start_response)



    def show(self, environ, start_response):
        start_response('200 OK', [('Content-type', 'text/html')])
        form = parse_formvars(environ)
        if form.get('kill'):
            kill_thread_id = form['kill']
        else:
            kill_thread_id = None
        thread_pool = environ['paste.httpserver.thread_pool']
        nworkers = thread_pool.nworkers
        now = time.time()
        workers = thread_pool.worker_tracker.items()
        workers.sort(key=lambda v: v[1][0])
        threads = []
        for (thread_id, (time_started, worker_environ,),) in workers:
            thread = bunch()
            threads.append(thread)
            if worker_environ:
                thread.uri = construct_url(worker_environ)
            else:
                thread.uri = 'unknown'
            thread.thread_id = thread_id
            thread.time_html = format_time(now - time_started)
            thread.uri_short = shorten(thread.uri)
            thread.environ = worker_environ
            thread.traceback = traceback_thread(thread_id)

        page = page_template.substitute(title='Thread Pool Worker Tracker', nworkers=nworkers, actual_workers=len(thread_pool.workers), nworkers_used=len(workers), script_name=environ['SCRIPT_NAME'], kill_thread_id=kill_thread_id, allow_kill=self.allow_kill, threads=threads, this_thread_id=get_ident(), track_threads=thread_pool.track_threads())
        return [page]



    def kill(self, environ, start_response):
        if not self.allow_kill:
            exc = httpexceptions.HTTPForbidden('Killing threads has not been enabled.  Shame on you for trying!')
            return exc(environ, start_response)
        vars = parse_formvars(environ)
        thread_id = int(vars['thread_id'])
        thread_pool = environ['paste.httpserver.thread_pool']
        if thread_id not in thread_pool.worker_tracker:
            exc = httpexceptions.PreconditionFailed('You tried to kill thread %s, but it is not working on any requests' % thread_id)
            return exc(environ, start_response)
        thread_pool.kill_worker(thread_id)
        script_name = environ['SCRIPT_NAME'] or '/'
        exc = httpexceptions.HTTPFound(headers=[('Location', script_name + '?kill=%s' % thread_id)])
        return exc(environ, start_response)




def traceback_thread(thread_id):
    if not hasattr(sys, '_current_frames'):
        return None
    frames = sys._current_frames()
    if thread_id not in frames:
        return None
    frame = frames[thread_id]
    out = StringIO()
    traceback.print_stack(frame, file=out)
    return out.getvalue()


hide_keys = ['paste.httpserver.thread_pool']

def format_environ(environ):
    if environ is None:
        return environ_template.substitute(key='---', value='No environment registered for this thread yet')
    environ_rows = []
    for (key, value,) in sorted(environ.items()):
        if key in hide_keys:
            continue
        try:
            if key.upper() != key:
                value = repr(value)
            environ_rows.append(environ_template.substitute(key=cgi.escape(str(key)), value=cgi.escape(str(value))))
        except Exception as e:
            environ_rows.append(environ_template.substitute(key=cgi.escape(str(key)), value='Error in <code>repr()</code>: %s' % e))

    return ''.join(environ_rows)



def format_time(time_length):
    if time_length >= 3600:
        time_string = '%i:%02i:%02i' % (int(time_length / 60 / 60), int(time_length / 60) % 60, time_length % 60)
    elif time_length >= 120:
        time_string = '%i:%02i' % (int(time_length / 60), time_length % 60)
    elif time_length > 60:
        time_string = '%i sec' % time_length
    elif time_length > 1:
        time_string = '%0.1f sec' % time_length
    else:
        time_string = '%0.2f sec' % time_length
    if time_length < 5:
        return time_string
    else:
        if time_length < 120:
            return '<span style="color: #900">%s</span>' % time_string
        return '<span style="background-color: #600; color: #fff">%s</span>' % time_string



def shorten(s):
    if len(s) > 60:
        return s[:40] + '...' + s[-10:]
    else:
        return s



def make_watch_threads(global_conf, allow_kill = False):
    from paste.deploy.converters import asbool
    return WatchThreads(allow_kill=asbool(allow_kill))


make_watch_threads.__doc__ = WatchThreads.__doc__

def make_bad_app(global_conf, pause = 0):
    pause = int(pause)

    def bad_app(environ, start_response):
        import thread
        if pause:
            time.sleep(pause)
        else:
            count = 0
            while 1:
                print "I'm alive %s (%s)" % (count, thread.get_ident())
                time.sleep(10)
                count += 1

        start_response('200 OK', [('content-type', 'text/plain')])
        return ['OK, paused %s seconds' % pause]


    return bad_app



