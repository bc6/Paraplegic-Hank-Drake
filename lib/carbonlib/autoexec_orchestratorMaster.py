import autoexec_common
import __builtin__

def Startup(servicesToRun, startInline = []):
    import blue
    blue.pyos.logMemory = 1
    blue.os.SetAppTitle('Juuuust a moment...')
    import sys
    import os
    sys.path.append(os.path.abspath(blue.os.binpath + '../../carbon/'))
    sys.path.append(os.path.abspath(blue.os.binpath + '../../carbon/tools/'))
    sys.path.append(os.path.abspath(blue.os.binpath + '../../carbon/tools/cluster/'))
    import tools
    autoexec_common.LogStarting('Orchestrator Master')
    import nasty
    args = blue.pyos.GetArg()[1:]
    for myArg in args:
        if myArg.startswith('/autotest'):
            parts = myArg.split(':')
            testList = parts[1:]
            if len(testList) == 1 and (testList[0].find('.txt') > 0 or testList[0].find('ALL') == 0):
                testList = testList[0]
            __builtin__.AUTOTESTLISTFILE = testList
        elif myArg.startswith('/resultmail'):
            parts = myArg.split(':')
            mailList = parts[1:]
            __builtin__.RESULTMAILLIST = mailList
        elif myArg.startswith('/revision'):
            parts = myArg.split(':')
            revision = str(parts[1])
            __builtin__.CURRENTTESTINGREVISION = revision
        elif myArg.startswith('/changelistsDataFile'):
            parts = myArg.split(':', 1)
            fileName = str(parts[1])
            __builtin__.CHANGELISTSDATAFILE = fileName
        elif myArg.startswith('/onlyEmailResultMailList'):
            __builtin__.ONLYEMAILRESULTMAILLIST = True
        elif myArg.startswith('/saveEmailToFile'):
            __builtin__.SAVEEMAILTOFILE = True
        elif myArg.startswith('/saveBenchmarkData'):
            __builtin__.SAVEBENCHMARKDATA = True

    if '/buildServer' in args:
        servicesToRun = servicesToRun + ('builderMaster',)
    additionalScriptDirs = ['bin:/../../carbon/backend/script/',
     'bin:/../backend/script/',
     'bin:/../../carbon/tools/orchestrator/master/script/',
     'bin:/../../carbon/tools/orchestrator/slave/script/',
     'bin:/../tools/orchestrator/slave/script/']
    if '/jessica' in args:
        additionalScriptDirs.extend(['bin:/../../carbon/tools/jessica/script/'])
        useExtensions = '/noJessicaExtensions' not in args
        if useExtensions:
            additionalScriptDirs.extend(['script:/../../../../../carbon/tools/jessicaExtensions/script/', 'script:/../../../../tools/jessicaExtensions/script/'])
    nasty.Startup(additionalScriptDirs)
    autoexec_common.LogStarted('Orchestrator Master')
    for i in blue.pyos.GetArg()[1:]:
        if i[0] != '-' and i[0] != '/':
            print 'Executing',
            print i
            blue.pyos.ExecFile(i, globals())

    import service
    srvMng = service.ServiceManager(startInline=['DB2', 'machoNet'] + startInline)
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


StartOrchestrator(('counter', 'http', 'machoNet', 'objectCaching', 'debug', 'alert', 'orchestratorMaster'))

