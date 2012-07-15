#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/util/safeThread.py
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
            self.__debugging = False
            self.MAX_REPAIR_ATTEMPTS = 1000
        else:
            self.__debugging = False
        self.uniqueIDstring = uniqueIDstring
        self.__killLoop = True
        self.__thread = None
        self.__active = False
        self.rep = True
        self.repairCount = 0
        self.__sleepTime = None

    def __MainLoop(self):
        blue.pyos.synchro.Yield()
        try:
            while self.__killLoop == False:
                now = blue.os.GetWallclockTime()
                if self.__debugging:
                    try:
                        if ClockThis(self.uniqueIDstring + '::SafeThreadLoop', self.SafeThreadLoop, now) == self.KILL_ME:
                            self.__killLoop = True
                    except SystemExit:
                        raise 
                    except TaskletExit:
                        self.__killLoop = True
                    except Exception as inst:
                        self.__killLoop = True
                        print 'SafeThread.__MainLoop - Unhandled Exception: ' + self.uniqueIDstring
                        print 'Repair attempts remaining:', self.MAX_REPAIR_ATTEMPTS - self.repairCount - 1, '\n'
                        log.LogException()
                        print traceback.print_tb(sys.exc_info()[2])
                        print inst
                        print inst.__doc__
                        debug.startDebugging()
                        uthread.new(self.__RestoreSafeThreadLoop)

                else:
                    try:
                        if ClockThis(self.uniqueIDstring + '::SafeThreadLoop', self.SafeThreadLoop, now) == self.KILL_ME:
                            self.__killLoop = True
                    except SystemExit:
                        raise 
                    except TaskletExit:
                        self.__killLoop = True
                    except Exception as e:
                        self.__killLoop = True
                        print 'SafeThread.__MainLoop - Unhandled Exception: ' + self.uniqueIDstring, '\n    Debug mode is off, skipping straight to repair'
                        print 'Repair attempts remaining:', self.MAX_REPAIR_ATTEMPTS - self.repairCount - 1, '\n'
                        print traceback.print_tb(sys.exc_info()[2])
                        log.LogException()
                        uthread.new(self.__RestoreSafeThreadLoop)
                        self.__thread = None
                        self.__active = False
                        self.__killLoop = True
                        raise e

                blue.pyos.synchro.SleepWallclock(self.__sleepTime)

            self.__thread = None
            self.__active = False
        except AttributeError:
            sys.exc_clear()

    def SafeThreadLoop(self, now):
        print 'ERROR: Please implement the virtual SafeThreadLoop function'
        return self.KILL_ME

    def KillLoop(self):
        self.__killLoop = True

    def Disabledebugging(self):
        self.__debugging = False

    def Enabledebugging(self):
        self.__debugging = True

    def LaunchSafeThreadLoop_MS(self, sleepTime = 16):
        if self.__active == False:
            self.__sleepTime = sleepTime
            self.__active = True
            self.__killLoop = False
            self.__thread = uthread.new(self.__MainLoop)
            self.__thread.context = self.uniqueIDstring
        else:
            log.LogError('ERROR: This class is already looping SafeThreadLoop function', self)

    def LaunchSafeThreadLoop_BlueTime(self, sleepTime = const.ONE_TICK):
        self.LaunchSafeThreadLoop_MS(sleepTime / const.MSEC)

    def __RestoreSafeThreadLoop(self):
        if self.repairCount < self.MAX_REPAIR_ATTEMPTS:
            self.repairCount += 1
            self.__WaitForRestart()
            if self.rep:
                self.RepairMe()
            self.LaunchSafeThreadLoop_MS(self.__sleepTime)

    def __WaitForRestart(self):
        while self.__active == True or self.__killLoop == False or self.__thread is not None:
            blue.pyos.synchro.SleepUntilWallclock(blue.os.GetWallclockTimeNow() + 100 * const.MSEC)

    def RepairMe(self):
        pass


def SleepAndCallAtTime(launchTime, function, *args, **kwargs):
    if blue.os.GetWallclockTimeNow() < launchTime:
        blue.pyos.synchro.SleepUntilWallclock(launchTime)
    else:
        blue.pyos.synchro.Yield()
    function(*args, **kwargs)


def DoMethodLater(waitDuration, launchFunction, *args, **kwargs):
    launchTime = blue.os.GetWallclockTime() + waitDuration
    uthread.worker(('doMethodLater-' + launchFunction.__name__), SleepAndCallAtTime, launchTime, launchFunction, *args, **kwargs)


import util
exports = util.AutoExports('safeThread', globals())