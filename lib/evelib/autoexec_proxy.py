import autoexec_proxy_core
import blue
import eveLog
servicesToRun = ['counter',
 'tcpRawProxyService',
 'http',
 'http2',
 'machoNet',
 'objectCaching',
 'debug',
 'ramProxy',
 'clientStatLogger',
 'alert',
 'processHealth']
if prefs.GetValue('enableDust', 0):
    dustServices = []
    servicesToRun += dustServices
arguments = blue.pyos.GetArg()[1:]
for argument in arguments:
    if argument.startswith('-startOrchestrator'):
        servicesToRun += ('orchestratorSlave',)

servicesToBlock = ['DB', 'DB2']
autoexec_proxy_core.StartProxy(servicesToRun, servicesToBlock=servicesToBlock, serviceManagerClass='EveServiceManager')

