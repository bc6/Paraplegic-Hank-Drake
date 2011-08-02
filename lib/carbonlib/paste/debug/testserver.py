import time
from paste.httpserver import *

class WSGIRegressionServer(WSGIServer):
    defaulttimeout = 10

    def __init__(self, *args, **kwargs):
        WSGIServer.__init__(self, *args, **kwargs)
        self.stopping = []
        self.pending = []
        self.timeout = self.defaulttimeout
        self.socket.settimeout(2)



    def serve_forever(self):
        from threading import Thread
        thread = Thread(target=self.serve_pending)
        thread.start()



    def reset_expires(self):
        if self.timeout:
            self.expires = time.time() + self.timeout



    def close_request(self, *args, **kwargs):
        WSGIServer.close_request(self, *args, **kwargs)
        self.pending.pop()
        self.reset_expires()



    def serve_pending(self):
        self.reset_expires()
        while not self.stopping or self.pending:
            now = time.time()
            if now > self.expires and self.timeout:
                print '\nWARNING: WSGIRegressionServer timeout exceeded\n'
                break
            if self.pending:
                self.handle_request()
            time.sleep(0.1)




    def stop(self):
        self.stopping.append(True)



    def accept(self, count = 1):
        [ self.pending.append(True) for x in range(count) ]




def serve(application, host = None, port = None, handler = None):
    server = WSGIRegressionServer(application, host, port, handler)
    print 'serving on %s:%s' % server.server_address
    server.serve_forever()
    return server


if __name__ == '__main__':
    import urllib
    from paste.wsgilib import dump_environ
    server = serve(dump_environ)
    baseuri = 'http://%s:%s' % server.server_address

    def fetch(path):
        server.accept(1)
        import socket
        socket.setdefaulttimeout(5)
        return urllib.urlopen(baseuri + path).read()


    server.accept(1)
    server.stop()
    urllib.urlopen(baseuri)

