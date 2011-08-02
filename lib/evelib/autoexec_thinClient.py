import autoexec_thinClient_core
import eveLog
servicesToRun = ('dataconfig', 'machoNet', 'objectCaching', 'alert', 'connectClient', 'devToolsClient')
startInline = ['config',
 'DB',
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

