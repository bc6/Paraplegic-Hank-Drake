from __future__ import with_statement
import SocketServer
import uthread

class UThreadingMixIn:
    __guid__ = 'StacklessSocketServer.UThreadingMixIn'

    def process_request_tasklet(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)



    def process_request(self, request, client_address):
        t = uthread.new(self.process_request_tasklet, request, client_address)
        t.run()




class UThreadingTCPServer(UThreadingMixIn, SocketServer.TCPServer):
    __guid__ = 'StacklessSocketServer.UThreadingTCPServer'


