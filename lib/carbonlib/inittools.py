import blue
if blue.pyos.packaged:
    try:
        import autoexec_tools
    except ImportError:
        import sys
        sys.exc_clear()
    except Exception:
        import traceback
        import log
        traceback.print_exc()
        log.LogException()
        raise 
else:
    args = blue.pyos.GetArg()[1:]
    tool = None
    for each in iter(args):
        split = each.split('=')
        if split[0].strip() == '/tools' and len(split) > 1:
            tool = split[1].strip()
            break

    if tool is not None:
        import sys
        import os
        pyver = sys.version[:3]
        pyver = pyver[0] + pyver[-1]
        if pyver not in ('25', '27'):
            pyver = '27'
        coreToolsPath = blue.os.binpath + '../../carbon/tools'
        localToolsPath = blue.os.binpath + '../tools'
        sharedToolsPath = '../../../../../shared_tools/libs'
        sys.path.append(os.path.join(coreToolsPath, 'lib'))
        libDir = blue.os.binpath + sharedToolsPath + '/lib' + pyver
        sys.path.append(libDir)
        import _site
        _site.addsitedir(libDir)
        if '32 bit' in sys.version:
            sys.path.append(libDir + '/bin/win32')
        else:
            sys.path.append(libDir + '/bin/x64')

        def execScript(path):
            try:
                blue.pyos.RunScript(path)
            except Exception as e:
                import traceback
                traceback.print_exc()
                blue.win32.MessageBox(str(e), 'Failed to initialize %s!' % (tool,), 272)
                blue.pyos.Quit(str(e))



        def execInitScript(toolsPath):
            if '/ziplib' in args and not blue.pyos.packaged:
                import shutil
                shutil.copyfile(toolsPath + '/startup/%s.py' % tool, toolsPath + '/startup/autoexec_tools.py')
                execScript(toolsPath + '/startup/%s.py' % tool)
            else:
                execScript(toolsPath + '/startup/%s.py' % tool)


        if os.path.exists(tool):
            execScript(tool)
        elif os.path.exists(localToolsPath + '/startup/%s.py' % tool):
            execInitScript(localToolsPath)
        elif os.path.exists(coreToolsPath + '/startup/%s.py' % tool):
            execInitScript(coreToolsPath)
        else:
            errStr = 'The following file was not found on your machine.\n/tools/startup/%s.py' % tool
            blue.win32.MessageBox(errStr, 'Failed to initialize %s' % tool, 272)
            blue.pyos.Quit(errStr)

