import log

def Info(channel, *etc):
    Log(channel, log.LGINFO, *etc)



def Notice(channel, *etc):
    Log(channel, log.LGNOTICE, *etc)



def Warn(channel, *etc):
    Log(channel, log.LGWARN, *etc)



def Error(channel, *etc):
    Log(channel, log.LGERR, *etc)



def Log(channel, flag, *blah):
    sm.GetService('log').Log(channel, flag, *blah)



def _Test():
    Info('lgtest', 'this is info')
    Notice('lgtest', 'this is notice')
    Warn('lgtest', 'this is warn')
    Error('lgtest', 'this is error')


exports = {'lg.Info': Info,
 'lg.Warn': Warn,
 'lg.Error': Error,
 'lg._Test': _Test}

