import blue
import lg

def Reboot(reason = ''):
    lg.Info('appUtils.Reboot', 'About to reboot the client because:' + reason)
    prefs.SetValue('rebootReason', reason)
    prefs.SetValue('rebootTime', blue.os.GetTime())
    allargs = blue.pyos.GetArg()
    cmd = allargs[0]
    args = []
    for arg in allargs[1:]:
        arg = arg.strip()
        if arg.find(' ') >= 0 or arg.find('\t') >= 0:
            arg = '"""' + arg + '"""'
        args.append(arg)

    args = ' '.join(args)
    lg.Info('appUtils.Reboot', 'About to reboot the client with:' + str((0,
     None,
     cmd,
     args)))
    try:
        blue.win32.ShellExecute(0, None, cmd, args)
    except Exception as e:
        lg.Error('appUtils.Reboot', 'Failed with: ' + str(e))
        raise 
    blue.pyos.Quit(reason)


exports = {'appUtils.Reboot': Reboot}

