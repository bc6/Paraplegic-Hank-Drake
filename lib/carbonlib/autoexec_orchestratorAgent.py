import autoexec_common
import __builtin__

def Startup(servicesToRun, startInline = []):
    import blue
    blue.pyos.logMemory = 1
    blue.os.SetAppTitle('Juuuust a moment...')
    autoexec_common.LogStarting('Orchestrator Agent')
    scriptDirs = ['bin:/../../carbon/backend/script/',
     'bin:/../backend/script/',
     'bin:/../../carbon/tools/orchestrator/agent/script/',
     'bin:/../../carbon/tools/orchestrator/slave/script/',
     'bin:/../tools/orchestrator/slave/script/']
    import nasty
    nasty.Startup(scriptDirs)
    autoexec_common.LogStarted('Orchestrator Agent')
    use64 = False
    for i in blue.pyos.GetArg()[1:]:
        if i[0] != '-' and i[0] != '/':
            print 'Executing',
            print i
            blue.pyos.ExecFile(i, globals())
        elif i.startswith('/use64'):
            parts = i.split(':')
            if len(parts) == 1:
                use64 = True
            elif 'True' == parts[1]:
                use64 = True

    __builtin__.USE64 = use64
    import service
    srvMng = service.ServiceManager(startInline=['machoNet'] + startInline)
    srvMng.Run(servicesToRun)
    macho = sm.services['machoNet']
    blue.os.SetAppTitle('[%s %s.%s] %s %s %s.%s pid=%s' % (macho.GetNodeID(),
     '?',
     boot.region.upper(),
     boot.codename,
     boot.role,
     boot.version,
     boot.build,
     blue.os.pid))
    import Jessica



def StartOrchestrator(servicesToRun, startInline = []):
    import blue
    blue.pyos.CreateTasklet(Startup, (servicesToRun, startInline), {})
    import Jessica


StartOrchestrator(('counter', 'http', 'machoNet', 'objectCaching', 'debug', 'alert', 'orchestratorAgent'))

