import os
import sys
import blue
import log
try:
    import marshalstrings
except ImportError:
    pass

def ReturnFalse():
    return False



def LogStarting(mode):
    startedat = '%s %s version %s build %s starting %s %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     blue.os.FormatUTC()[0],
     blue.os.FormatUTC()[2])
    print startedat
    log.general.Log(startedat, log.LGNOTICE)
    log.general.Log('Python version: ' + sys.version, log.LGNOTICE)
    if blue.win32.IsTransgaming():
        log.general.Log('Transgaming? yes')
        try:
            blue.win32.TGGetOS()
            blue.win32.TGGetSystemInfo()
        except NotImplementedError:
            log.general.Log('TG OS & TG SI: not implemented, pretending not to be TG')
            blue.win32.IsTransgaming = ReturnFalse
    else:
        log.general.Log('Transgaming? no')
    if blue.win32.IsTransgaming():
        log.general.Log('TG OS: ' + blue.win32.TGGetOS(), log.LGNOTICE)
        log.general.Log('TG SI: ' + repr(blue.win32.TGGetSystemInfo()), log.LGNOTICE)
    log.general.Log('Process bits: ' + repr(blue.win32.GetProcessBits()), log.LGNOTICE)
    log.general.Log('Wow64 process? ' + ('yes' if blue.win32.IsWow64Process() else 'no'), log.LGNOTICE)
    log.general.FLog('System info: ' + repr(blue.win32.GetSystemInfo()), log.LGNOTICE)
    if blue.win32.IsWow64Process():
        log.general.FLog('Native system info: ' + repr(blue.win32.GetNativeSystemInfo()), log.LGNOTICE)



def LogStarted(mode):
    startedat = '%s %s version %s build %s started %s %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     blue.os.FormatUTC()[0],
     blue.os.FormatUTC()[2])
    print strx(startedat)
    log.general.Log(startedat, log.LGINFO)
    log.general.Log(startedat, log.LGNOTICE)
    log.general.Log(startedat, log.LGWARN)
    log.general.Log(startedat, log.LGERR)



