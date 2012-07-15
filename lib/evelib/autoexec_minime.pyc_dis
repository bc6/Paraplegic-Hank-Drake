#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\eve\common\lib\autoexec_minime.py
import blue
import eveLog

def Startup():
    import nasty
    nasty.Startup()
    import service
    srvMng = service.ServiceManager()
    srvMng.Run([])


t = blue.pyos.CreateTasklet(Startup, (), {})
t.context = '^boot::autoexec_minime'
import Jessica