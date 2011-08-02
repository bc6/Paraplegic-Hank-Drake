from timerstuff import ClockThis
import uthread
import blue
import debug
import sys
import traceback
import log
import const

class SafeThread(object):
    __guid__ = 'safeThread.SafeThread'
    KILL_ME = 145686248
    MAX_REPAIR_ATTEMPTS = 10

    def init(self, uniqueIDstring):
        args = blue.pyos.GetArg()[1:]
        if ('/debug' in args or '/jessica' in args) and not prefs.GetValue('neverDebug', False):
            self._SafeThread__debugging = False
            self.MAX_REPAIR_ATTEMPTS = 1000
        else:
            self._SafeThread__debugging = False
        self.uniqueIDstring = uniqueIDstring
        self._SafeThread__killLoop = True
        self._SafeThread__thread = None
        self._SafeThread__active = False
        self.rep = True
        self.repairCount = 0
        self._SafeThread__sleepTime = None



    def __MainLoop(self):
        blue.pyos.synchro.Yield()
        try:
            while self._SafeThread__killLoop == False:
                now = blue.os.GetTime()
                if self._SafeThread__debugging:
                    try:
                        if ClockThis(self.uniqueIDstring + '::SafeThreadLoop', self.SafeThreadLoop, now) == self.KILL_ME:
                            self._SafeThread__killLoop = True
                    except SystemExit:
                        raise 
                    except TaskletExit:
                        self._SafeThread__killLoop = True
                    except Exception as inst:
                        self._SafeThread__killLoop = True
                        print 'SafeThread.__MainLoop - Unhandled Exception: ' + self.uniqueIDstring
                        print 'Repair attempts remaining:',
                        print self.MAX_REPAIR_ATTEMPTS - self.repairCount - 1,
                        print '\n'
                        log.LogException()
                        print traceback.print_tb(sys.exc_info()[2])
                        print inst
                        print inst.__doc__
                        debug.startDebugging()
                        uthread.new(self._SafeThread__RestoreSafeThreadLoop)
                else:
                    try:
                        if ClockThis(self.uniqueIDstring + '::SafeThreadLoop', self.SafeThreadLoop, now) == self.KILL_ME:
                            self._SafeThread__killLoop = True
                    except SystemExit:
                        raise 
                    except TaskletExit:
                        self._SafeThread__killLoop = True
                    except Exception as e:
                        self._SafeThread__killLoop = True
                        print 'SafeThread.__MainLoop - Unhandled Exception: ' + self.uniqueIDstring,
                        print '\n    Debug mode is off, skipping straight to repair'
                        print 'Repair attempts remaining:',
                        print self.MAX_REPAIR_ATTEMPTS - self.repairCount - 1,
                        print '\n'
                        print traceback.print_tb(sys.exc_info()[2])
                        log.LogException()
                        uthread.new(self._SafeThread__RestoreSafeThreadLoop)
                        self._SafeThread__thread = None
                        self._SafeThread__active = False
                        self._SafeThread__killLoop = True
                        raise e
                blue.pyos.synchro.Sleep(self._SafeThread__sleepTime)

            self._SafeThread__thread = None
            self._SafeThread__active = False
        except AttributeError:
            sys.exc_clear()



    def SafeThreadLoop(self, now):
        print 'ERROR: Please implement the virtual SafeThreadLoop function'
        return self.KILL_ME



    def KillLoop(self):
        self._SafeThread__killLoop = True



    def Disabledebugging(self):
        self._SafeThread__debugging = False



    def Enabledebugging(self):
        self._SafeThread__debugging = True



    def LaunchSafeThreadLoop_MS(self, sleepTime = 16):
        if self._SafeThread__active == False:
            self._SafeThread__sleepTime = sleepTime
            self._SafeThread__active = True
            self._SafeThread__killLoop = False
            self._SafeThread__thread = uthread.new(self._SafeThread__MainLoop)
            self._SafeThread__thread.context = self.uniqueIDstring
        else:
            log.LogError('ERROR: This class is already looping SafeThreadLoop function', self)



    def LaunchSafeThreadLoop_BlueTime(self, sleepTime = const.ONE_TICK):
        self.LaunchSafeThreadLoop_MS(sleepTime / const.MSEC)



    def __RestoreSafeThreadLoop(self):
        if self.repairCount < self.MAX_REPAIR_ATTEMPTS:
            self.repairCount += 1
            self._SafeThread__WaitForRestart()
            if self.rep:
                self.RepairMe()
            self.LaunchSafeThreadLoop_MS(self._SafeThread__sleepTime)



    def __WaitForRestart(self):
        while self._SafeThread__active == True or self._SafeThread__killLoop == False or self._SafeThread__thread is not None:
            blue.pyos.synchro.SleepUntil(blue.os.GetTime(1) + 100 * const.MSEC)




    def RepairMe(self):
        pass




def SleepAndCallAtTime(launchTime, function, *args, **kwargs):
    if blue.os.GetTime(1) < launchTime:
        blue.pyos.synchro.SleepUntil(launchTime)
    else:
        blue.pyos.synchro.Yield()
    function(*args, **kwargs)



def DoMethodLater(waitDuration, launchFunction, *args, **kwargs):
    launchTime = blue.os.GetTime() + waitDuration
    uthread.worker(('doMethodLater-' + launchFunction.__name__), SleepAndCallAtTime, launchTime, launchFunction, *args, **kwargs)


import util
exports = util.AutoExports('safeThread', globals())

