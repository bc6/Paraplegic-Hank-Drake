#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/util/autoLogin.py
import blue
import loginEventHandler
import blue.synchro.Sleep as Sleep
import log

class AutoLoginHandler:

    def __init__(self):
        self.eventHandler = loginEventHandler.LoginEventHandler()

    def ParseCommandLineAndLogin(self):
        AUTOLOGIN_ARG = '/autologin'
        DELIMITER = ':'
        args = blue.pyos.GetArg()[1:]
        if AUTOLOGIN_ARG not in args:
            return
        argsRef = None
        for i in range(len(args)):
            if args[i] == AUTOLOGIN_ARG:
                argsRef = i + 1
                break

        if argsRef is not None and argsRef < len(args):
            myArgs = args[argsRef]
        else:
            return
        atomicArgs = myArgs.split(DELIMITER)
        if len(atomicArgs) == 2:
            user, password = atomicArgs
            self.LoginUser(user=user, password=password)

    def LoginUser(self, user = 'esp', password = 'esp'):
        self.eventHandler.WaitForEula()
        loginForm = uicore.layer.login
        if user:
            loginForm.usernameEditCtrl.SetValue(user)
        if password:
            loginForm.passwordEditCtrl.SetValue(password)

        def amIReadyToRock():
            Sleep(1000)
            return ': OK' in loginForm.serverStatusTextControl.GetText()

        if not amIReadyToRock():
            raise Exception
        loginForm.Connect()
        self.eventHandler.WaitForCharsel()
        charSelForm = uicore.layer.charsel
        Sleep(5000)
        charSelForm.Confirm()


import util
exports = util.AutoExports('autoLogin', locals())