import stackless
import blue
import sys
import os
import log
import autoexec_common
Done = False

def Startup(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline = [], serviceManagerClass = 'ServiceManager'):
    global Done
    blue.pyos.logMemory = 1
    args = blue.pyos.GetArg()[1:]
    autoexec_common.LogStarting('Client')
    additionalScriptDirs = []
    for argument in args:
        if argument.startswith('-startOrchestrator'):
            additionalScriptDirs.extend(['bin:/../../carbon/tools/orchestrator/slave/script/', 'bin:/../tools/orchestrator/slave/script/'])
            servicesToRun += ('orchestratorSlave',)
        elif argument.startswith('/telemetryServer='):
            tmServer = str(argument[17:])
            blue.statistics.StartTelemetry(tmServer)

    if '/jessica' in args and '/localizationMonitor' in args:
        servicesToRun += ('localizationMonitor',)
    if not blue.pyos.packaged and '/jessica' in args:
        if '/carbon' in blue.os.binpath:
            jessicaToolPath = '../tools/'
        else:
            jessicaToolPath = '../../carbon/tools/'
        additionalScriptDirs.extend(['script:/../' + jessicaToolPath + '/jessica/script/', 'script:/../../../carbon/backend/script/', 'script:/../../backend/script/'])
        useExtensions = '/noJessicaExtensions' not in args
        if useExtensions:
            additionalScriptDirs.extend(['script:/../' + jessicaToolPath + 'jessicaExtensions/script/', 'script:/../../tools/jessicaExtensions/script/'])
        servicesToRun += ('catma',)
    import nasty
    nasty.Startup(additionalScriptDirs)
    errorMsg = {'resetsettings': [mls.UI_GENERIC_CANTCLEARSETTINGS, mls.UI_GENERIC_CANTCLEARSETTINGSHDR, 'Cannot clear settings'],
     'clearcache': [mls.UI_GENERIC_CANTCLEARCACHE, mls.UI_GENERIC_CANTCLEARCACHEHDR, 'Cannot clear cache']}
    for (clearType, clearPath,) in [('resetsettings', blue.os.settingspath), ('clearcache', blue.os.cachepath)]:
        if getattr(prefs, clearType, 0):
            if clearType == 'resetsettings':
                prefs.DeleteValue(clearType)
            if os.path.exists(clearPath):
                i = 0
                while 1:
                    newDir = clearPath[:-1] + '_backup%s' % i
                    if not os.path.isdir(newDir):
                        try:
                            os.makedirs(newDir)
                        except:
                            blue.win32.MessageBox(errorMsg[clearType][0], errorMsg[clearType][1], 272)
                            blue.pyos.Quit(errorMsg[clearType][2])
                            return False
                        break
                    i += 1

                for filename in os.listdir(clearPath):
                    if filename != 'Settings':
                        try:
                            os.rename(clearPath + filename, '%s_backup%s/%s' % (clearPath[:-1], i, filename))
                        except:
                            blue.win32.MessageBox(errorMsg[clearType][0], errorMsg[clearType][1], 272)
                            blue.pyos.Quit(errorMsg[clearType][2])
                            return False

                prefs.DeleteValue(clearType)

    mydocs = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL)
    paths = [blue.os.cachepath]
    for dir in appCacheDirs:
        paths.append(blue.os.cachepath + dir)

    for dir in userCacheDirs:
        paths.append(mydocs + dir)

    for path in paths:
        try:
            os.makedirs(path)
        except OSError as e:
            sys.exc_clear()

    import __builtin__
    import base
    session = base.CreateUserSession()
    __builtin__.session = session
    __builtin__.charsession = session
    base.EnableCallTimers(1)
    builtinSetupHook()
    autoexec_common.LogStarted('Client')
    import bluepy
    import numerical
    bluepy.frameClock = numerical.FrameClock()
    blue.os.frameClock = bluepy.frameClock
    import service
    smClass = getattr(service, serviceManagerClass)
    srvMng = smClass(startInline=['DB2', 'machoNet'] + startInline)
    if hasattr(prefs, 'http') and prefs.http:
        log.general.Log('Running http', log.LGINFO)
        srvMng.Run(('http',))
    srvMng.Run(servicesToRun)
    title = '[%s] %s %s %s.%s pid=%s' % (boot.region.upper(),
     boot.codename,
     boot.role,
     boot.version,
     boot.build,
     blue.os.pid)
    blue.os.SetAppTitle(title)
    Done = True
    bmRuns = prefs.GetValue('bmnextrun', 0)
    if '/benchmark' in args or bmRuns >= 1:
        import benchmark1
        prefs.SetValue('bmnextrun', bmRuns - 1)
        benchmark1.Run()
    if preUIStartArgProcessHook is not None:
        preUIStartArgProcessHook(args)
    if '/skiprun' not in args:
        if '/webtools' in args:
            ix = args.index('/webtools') + 1
            pr = args[ix]
            pr = pr.split(',')
            srvMng.StartService('webtools').SetVars(pr)
        srvMng.GetService(StartupUIServiceName).StartupUI(0)



def StartClient(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline = [], serviceManagerClass = 'ServiceManager'):
    t = blue.pyos.CreateTasklet(Startup, (appCacheDirs,
     userCacheDirs,
     builtinSetupHook,
     servicesToRun,
     preUIStartArgProcessHook,
     StartupUIServiceName,
     startInline,
     serviceManagerClass), {})
    t.context = '^boot::autoexec_client'
    import Jessica



