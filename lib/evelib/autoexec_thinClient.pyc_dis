#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\eve\common\lib\autoexec_thinClient.py
import autoexec_thinClient_core
import eveLog
servicesToRun = ('counter', 'dataconfig', 'machoNet', 'objectCaching', 'alert', 'connectClient', 'godma')
startInline = ['config',
 'machoNet',
 'objectCaching',
 'dataconfig',
 'dogmaIM',
 'device']

def setupBuiltinSession():
    import eve
    import __builtin__
    evetmp = eve.eve
    evetmp.session = __builtin__.session
    del eve
    __builtin__.eve = evetmp
    wwwroot = 'script:/wwwroot/;script:/../../../../carbon/common/script/wwwroot/;script:/../../../common/script/wwwroot/;script:/../../../client/script/wwwroot/'
    prefs.SetValue('wwwroot', wwwroot)


autoexec_thinClient_core.StartClient(servicesToRun, setupBuiltinSession, startInline)