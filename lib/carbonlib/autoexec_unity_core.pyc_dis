#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\autoexec_unity_core.py
Done = False
import blue
import sys
import os
import log
import autoexec_common

def SimpleNasty():
    scriptDirs = ['/../../common/script/',
     '/',
     '/../../../carbon/common/script/',
     '/../../client/script/',
     '/../../server/script/']
    coreScript = '/../../../carbon/%s/script/' % str(boot.role)
    coreToolsJessica = '/../../../../../../core_tools/MAIN/Jessica'
    scriptDirs.append(coreScript)
    scriptDirs.append(coreToolsJessica)
    log.general.Log('==========================================================')
    log.general.Log('Adding the directories to sys.path')
    missingpath = set()
    for scriptDir in scriptDirs:
        scriptDir = blue.paths.ResolvePath(u'script:/') + scriptDir
        for root, dirs, files in os.walk(scriptDir):
            root = root.replace('\\', '/')
            if root[-1] == '/':
                root = root[:-1]
            missingpath.add(os.path.normpath(root))

    for path in missingpath:
        log.general.Log('sys.path: %s' % path)
        sys.path.append(path)

    log.general.Log('==========================================================')


def Startup(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline = []):
    global Done
    autoexec_common.LogStarting('Unity')
    SimpleNasty()
    mydocs = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL)
    paths = [blue.paths.ResolvePath(u'cache:/')]
    for dir in appCacheDirs:
        paths.append(blue.paths.ResolvePath(u'cache:/') + dir)

    for dir in userCacheDirs:
        paths.append(mydocs + dir)

    for path in paths:
        try:
            os.makedirs(path)
        except OSError as e:
            sys.exc_clear()

    builtinSetupHook()
    autoexec_common.LogStarted('Unity')
    import bluepy, numerical
    bluepy.frameClock = numerical.FrameClock()
    blue.os.frameClock = bluepy.frameClock
    title = '[%s] %s %s %s.%s pid=%s' % (boot.region.upper(),
     boot.codename,
     boot.role,
     boot.version,
     boot.build,
     blue.os.pid)
    blue.os.SetAppTitle(title)
    Done = True


def StartClient(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline = []):
    if '/tasklet' not in blue.pyos.GetArg()[1:]:
        import stackless
        stackless.tasklet = None
    Startup(appCacheDirs, userCacheDirs, builtinSetupHook, servicesToRun, preUIStartArgProcessHook, StartupUIServiceName, startInline)
    unityCorePath = blue.paths.ResolvePath(u'root:/../carbon/unity/script')
    sys.path.append(unityCorePath)
    import unity_core