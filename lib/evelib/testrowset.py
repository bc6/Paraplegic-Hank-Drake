import sys
import stackless
stackless.enable_softswitch(0)
from sake import stacklesssocket
stacklesssocket.install()

def DummyMgr():
    pass


stacklesssocket.stacklesssocket_manager(DummyMgr)
from sake.app import InitializeApp
from sake.process import Process
from sake.const import PLATFORM_PS3
from dust.app import DustApp
title = 'test rowset'
app = InitializeApp(DustApp, title)

class RowsetTestService(Process):
    serviceName = 'rowsettest'
    serviceIncludes = []

    def StartProcess(self):
        global desktop
        if sys.platform == PLATFORM_PS3:
            s = open('/app_home/bin/thehost.txt').read()
            address = s.rsplit(' ', 1)[1].strip()
        else:
            address = '127.0.0.1'
        connection = app.GetService('remoteConnection')
        connection.ConnectToWorldManager(address)
        self.ep = connection.GetEndpoint()
        print 'Have now connection',
        print self.ep
        ret = self.ep.Call('backend.Authenticate', 'dsp', 'dsp')
        print 'got auth ret',
        print ret
        import starMap
        desktop.OpenView('starMap.debug', ('starMap.default',), CaptureInput.ALL)



import sake.network
import dust.remote
services = [sake.network.ConnectionService, dust.remote.RemoteConnection, RowsetTestService]
app.InitServices(services)
if True:
    app.pumpWindowsMessages = False
    import deelite
    from viewmgr import ViewMgr, DeeViewerApp, CaptureInput
    desktop = ViewMgr('deeviewer', False)
    deelite._deeliteMgr.viewManagers.append(desktop)
    desktop.Refresh()
    DeeViewerApp.MainLoop()
else:
    app.Run()

