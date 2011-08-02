import blue
import sys
import os.path
import log

def ToolsPath(args):
    pyver = sys.version[:3]
    pyver = pyver[0] + pyver[-1]
    if pyver not in ('25', '27'):
        pyver = '27'
    if '/localdev' in args:
        up1 = os.path.split(blue.os.binpath)[0]
        up2 = os.path.split(up1)[0]
        up3 = os.path.split(up2)[0]
        toolsPerforcePath = 'games/' + os.path.split(up3)[1]
    else:
        toolsPerforcePath = 'games/shared_tools/libs'
    toolsPath = '../../carbon/tools'
    _coreToolsPath = '../../../../../shared_tools/libs'
    log.general.Log('Jessica.py: toolsPath:' + toolsPath + ' toolsPerforcePath:' + toolsPerforcePath, log.LGNOTICE)
    site_dir = blue.os.binpath + _coreToolsPath + '/lib' + pyver
    sys.path.append(site_dir)
    import _site
    _site.addsitedir(site_dir)
    if '32 bit' in sys.version:
        sys.path.append(blue.os.binpath + _coreToolsPath + '/lib' + pyver + '/bin/win32')
    else:
        sys.path.append(blue.os.binpath + _coreToolsPath + '/lib' + pyver + '/bin/x64')
    log.general.Log('sys.path normalised mappings for debugging ImportError:', log.LGNOTICE)
    for path in sys.path:
        path = os.path.normpath(path)
        level = log.LGNOTICE
        exists = True
        if not os.path.exists(path):
            level = log.LGERR
            exists = False
        log.general.Log('  %s [Exists: %s]' % (path, exists), level)

    return (blue.os.binpath + toolsPath, blue.os.binpath + _coreToolsPath)



def Jessica(args):
    (toolsPath, coreToolsPath,) = ToolsPath(args)
    jessicaPath = toolsPath + '/jessica'
    sharedmodules = coreToolsPath + '/sharedmodules'
    sys.path.append(sharedmodules)
    sys.path.append(toolsPath + '/lib')
    sys.path.append(toolsPath + '/pipeline/jessica')
    if os.path.exists(coreToolsPath + '/jessicaLite'):
        jessicaLiteSrc = coreToolsPath + '/jessicaLite/src'
        jessicaLiteLib = coreToolsPath + '/jessicaLite/lib'
        sys.path.append(jessicaLiteSrc)
        sys.path.append(jessicaLiteLib)
    useExtensions = '/noJessicaExtensions' not in args
    if useExtensions:
        jessica_ext_dir = blue.os.binpath + '../tools/jessicaExtensions'
        jessica_core_ext_dir = toolsPath + '/jessicaExtensions'
    APPDIR = jessicaPath
    RESDIR = jessicaPath + '/res'
    if useExtensions and os.path.exists(jessica_ext_dir + '/macros'):
        MACRODIR = jessica_ext_dir + '/macros'
    else:
        MACRODIR = jessicaPath + '/macros'
    sys.path.append(APPDIR)
    if useExtensions:
        if os.path.exists(jessica_ext_dir):
            sys.path.append(jessica_ext_dir)
        if os.path.exists(jessica_core_ext_dir):
            sys.path.append(jessica_core_ext_dir)
    if boot.role != 'minime':
        import nasty
        while not nasty.nastyInitialized:
            blue.os.Pump()

    if '/minime' in args:
        RunMinime(args)
    else:
        import app.App as App
        import app.Config as Config
        Config.RESDIR = RESDIR
        Config.MACRODIR = MACRODIR
        frameStr = 'MinFrame'
        for each in args:
            if '/frame' in each and '=' in each:
                frameStr = each.split('=')[1]
                break

        if boot.role == 'orchestratorMaster':
            frameStr = 'OrchestratorFrame'
        jessica = App.Object(frameStr)
        title = '[%s] %s %s %s.%s pid=%s' % (boot.region.upper(),
         boot.codename,
         boot.role,
         boot.version,
         boot.build,
         blue.os.pid)
        jessica.mainFrame.SetTitle(jessica.mainFrame.GetTitle() + ' (%s)' % title)
        import locale
        locale.setlocale(locale.LC_ALL, 'English')
        if '/simple_main_loop' in args:
            jessica.Simple_MainLoop()
        else:
            jessica.MainLoop()



def MakeDummySm():
    import __builtin__

    class DummySm:

        def __init__(self):
            pass



        def ScatterEvent(self, a, b):
            pass



        def SendEvent(self, eventid, *args, **keywords):
            pass



        def RegisterNotify(self, ob):
            pass



    __builtin__.sm = DummySm()



def Minime(args):
    if boot.role not in ('server', 'proxy'):
        MakeDummySm()
    ToolsPath(args)
    RunMinime(args)



def RunMinime(args):
    if '/nowindow' in args:
        try:
            for each in args:
                if each.startswith('/test_script'):
                    path = each.split('=')[1]
                    execfile(path, globals())

        except Exception as e:
            import log
            import traceback
            traceback.print_exc()
            log.LogException()
            sys.exc_clear()
    else:
        import minime
        minime.Main()


if not blue.pyos.packaged:
    args = blue.pyos.GetArg()[1:]
    app = ''
    try:
        if '/jessica' in args:
            app = 'Jessica'
            Jessica(args)
        elif '/minime' in args:
            app = 'Minime'
            Minime(args)
    except Exception as e:
        import log
        import traceback
        log.LogException()
        traceback.print_exc()
        sys.exc_clear()
        toolsPath = ToolsPath(args)
        if isinstance(e, ImportError) and not os.path.exists(toolsPath[1]):
            errStr = 'Please add the following line to your client spec.                    \n//depot/games/core_tools/MAIN/... //WORKSPACE/games/core_tools/MAIN/...'
        else:
            errStr = str(e)
        blue.win32.MessageBox(errStr, 'Failed to initialize %s!' % (app,), 272)

