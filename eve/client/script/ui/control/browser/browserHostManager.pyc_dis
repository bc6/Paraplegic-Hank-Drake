#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/browser/browserHostManager.py
import blue
import service
import ccpBrowserHost
import browserutil
import corebrowserutil
import os
import errno
import log
import shutil
import sys
import svc

class BrowserHostManager(svc.browserHostManager):
    __guid__ = 'svc.eveBrowserHostManager'
    __replaceservice__ = 'browserHostManager'
    __startupdependencies__ = ['settings']

    def AppRun(self, *args):
        pass

    def AppGetBrowserCachePath(self):
        return settings.public.generic.Get('BrowserCache', corebrowserutil.DefaultCachePath())