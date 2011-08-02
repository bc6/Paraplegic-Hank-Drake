import logging
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import cherrypy
from cherrypy._cperror import format_exc, bare_error
from cherrypy.lib import httputil
from cherrypy import wsgiserver

class NativeGateway(wsgiserver.Gateway):
    recursive = False

    def respond(self):
        req = self.req
        try:
            local = req.server.bind_addr
            local = httputil.Host(local[0], local[1], '')
            remote = (req.conn.remote_addr, req.conn.remote_port)
            remote = httputil.Host(remote[0], remote[1], '')
            scheme = req.scheme
            sn = cherrypy.tree.script_name(req.uri or '/')
            if sn is None:
                self.send_response('404 Not Found', [], [''])
            else:
                app = cherrypy.tree.apps[sn]
                method = req.method
                path = req.path
                qs = req.qs or ''
                headers = req.inheaders.items()
                rfile = req.rfile
                prev = None
                try:
                    redirections = []
                    while True:
                        (request, response,) = app.get_serving(local, remote, scheme, 'HTTP/1.1')
                        request.multithread = True
                        request.multiprocess = False
                        request.app = app
                        request.prev = prev
                        try:
                            request.run(method, path, qs, req.request_protocol, headers, rfile)
                            break
                        except cherrypy.InternalRedirect as ir:
                            app.release_serving()
                            prev = request
                            if not self.recursive:
                                if ir.path in redirections:
                                    raise RuntimeError('InternalRedirector visited the same URL twice: %r' % ir.path)
                                elif qs:
                                    qs = '?' + qs
                                redirections.append(sn + path + qs)
                            method = 'GET'
                            path = ir.path
                            qs = ir.query_string
                            rfile = StringIO()

                    self.send_response(response.output_status, response.header_list, response.body)

                finally:
                    app.release_serving()

        except:
            tb = format_exc()
            cherrypy.log(tb, 'NATIVE_ADAPTER', severity=logging.ERROR)
            (s, h, b,) = bare_error()
            self.send_response(s, h, b)



    def send_response(self, status, headers, body):
        req = self.req
        req.status = str(status or '500 Server Error')
        for (header, value,) in headers:
            req.outheaders.append((header, value))

        if req.ready and not req.sent_headers:
            req.sent_headers = True
            req.send_headers()
        for seg in body:
            req.write(seg)





class CPHTTPServer(wsgiserver.HTTPServer):

    def __init__(self, server_adapter = cherrypy.server):
        self.server_adapter = server_adapter
        server_name = self.server_adapter.socket_host or self.server_adapter.socket_file or None
        wsgiserver.HTTPServer.__init__(self, server_adapter.bind_addr, NativeGateway, minthreads=server_adapter.thread_pool, maxthreads=server_adapter.thread_pool_max, server_name=server_name)
        self.max_request_header_size = self.server_adapter.max_request_header_size or 0
        self.max_request_body_size = self.server_adapter.max_request_body_size or 0
        self.request_queue_size = self.server_adapter.socket_queue_size
        self.timeout = self.server_adapter.socket_timeout
        self.shutdown_timeout = self.server_adapter.shutdown_timeout
        self.protocol = self.server_adapter.protocol_version
        self.nodelay = self.server_adapter.nodelay
        ssl_module = self.server_adapter.ssl_module or 'pyopenssl'
        if self.server_adapter.ssl_context:
            adapter_class = wsgiserver.get_ssl_adapter_class(ssl_module)
            self.ssl_adapter = adapter_class(self.server_adapter.ssl_certificate, self.server_adapter.ssl_private_key, self.server_adapter.ssl_certificate_chain)
            self.ssl_adapter.context = self.server_adapter.ssl_context
        elif self.server_adapter.ssl_certificate:
            adapter_class = wsgiserver.get_ssl_adapter_class(ssl_module)
            self.ssl_adapter = adapter_class(self.server_adapter.ssl_certificate, self.server_adapter.ssl_private_key, self.server_adapter.ssl_certificate_chain)




