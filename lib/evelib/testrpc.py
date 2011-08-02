import sys
from sake import stacklesssocket
stacklesssocket.install()

def DummyMgr():
    pass


stacklesssocket.stacklesssocket_manager(DummyMgr)
isServer = sys.platform == 'win32' and 'client' not in sys.argv
from sake.app import InitializeApp
from dust.app import DustApp
title = 'test rpc ' + ('server' if isServer else 'client')
app = InitializeApp(DustApp, title)
import sake.login
import sake.telnetServer
import sake.pasteServer
import sake.network
import dust.testserver
services = [sake.telnetServer.TelnetServer,
 sake.pasteServer.PasteServer,
 sake.network.ConnectionService,
 dust.testserver.TestServerService]
app.InitServices(services)
import sake.web
app.process.New(sake.web.Run)

def Bingo():
    from paste import httpserver
    from paste.wsgilib import dump_environ
    s = httpserver.serve(dump_environ, server_version='Wombles/1.0', protocol_version='HTTP/1.1', host='0.0.0.0', port='8888', use_threadpool=False, start_loop=False)
    print 'serving on 8888'
    while app.running:
        s.handle_request()




def SocketPump():
    import asyncore
    while app.running:
        if len(asyncore.socket_map):
            app.process.New(asyncore.poll)
        app.Sleep(300)

    print 'app r uningni no longe??!?!?',
    print app.running


app.process.New(Bingo)
import httplib

def Bingo2():
    import httplib
    print 'conn is pyhon org'
    conn = httplib.HTTPConnection('bamboo')
    print 'Getting'
    conn.request('GET', '/')
    print 'resonsingP'
    r1 = conn.getresponse()
    print 'the status:',
    print r1.status,
    print r1.reason
    data1 = r1.read()
    print 'the data:',
    print data1[:50]
    conn.request('GET', '/parrot.spam')
    r2 = conn.getresponse()
    print r2.status,
    print r2.reason
    data2 = r2.read()
    conn.close()



def ConnTest():
    print 'doing conntest'
    connection = app.GetService('connection')
    if sys.platform == 'win32' and 'client' not in sys.argv:
        connection.StartAccepting(sake.network.PORT_ROOT)
        connection.StartAccepting(sake.network.PORT_USER)
    else:
        print 'about to connect to server'
        if sys.platform == 'PS3':
            s = open('/app_home/bin/thehost.txt').read()
            address = s.rsplit(' ', 1)[1].strip()
        else:
            address = '127.0.0.1'
        print 'About to try to connect to',
        print address
        ep = connection.Connect(address, sake.network.PORT_ROOT)
        print 'Have now connection',
        print ep
        while app.running:
            print 'Pinging.'
            try:
                ret = ep.Ping()
                print 'got ping info',
                print ret
            except Exception as e:
                print 'Rats!',
                print e
                break



app.process.New(ConnTest)
app.Run()

