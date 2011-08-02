import service
import uix
import uiutil
import uiconst
import mathUtil
import uthread
import util
import log
import blue
import menu
import form
import _weakref
import trinity
import draw
import types
import base
import sys
from util import ResFile

class UICursorDeviceResource(object):

    def __init__(self, resName):
        self.resName = resName
        self.surface = None
        dev = trinity.GetDevice()
        dev.RegisterResource(self)
        self.OnCreate(dev)



    def OnInvalidate(self, level):
        self.surface = None



    def OnCreate(self, dev):
        self.surface = dev.CreateOffscreenPlainSurface(32, 32, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SCRATCH)
        self.surface.LoadSurfaceFromFile(ResFile(self.resName))




class UI(service.Service):
    __update_on_reload__ = 0
    __guid__ = 'svc.ui'
    __dependencies__ = ['font', 'settings']
    __notifyevents__ = ['OnContactLoggedOn', 'OnContactLoggedOff']

    def __init__(self):
        service.Service.__init__(self)



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.blinks = []
        self.showinguserson = []
        self.showingusersoff = []
        self.freezeOverview = 0
        self.stationsdata = None
        self.blinksA = {}
        self.blinksRGB = {}
        self.blink_running = False
        uicore.event.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self.CheckKeyDown)
        uicore.event.RegisterForTriuiEvents([uiconst.UI_KEYUP], self.CheckKeyUp)
        self.cursorSurfaces = {}



    def Stop(self, memStream = None):
        self.LogInfo('Stopping UI Service')
        self.blink_running = False
        self.cursorSurfaces.clear()



    def StopBlink(self, sprite):
        if not getattr(self, 'blink_running', False):
            return 
        if not hasattr(self, 'remPending'):
            self.remPending = []
        self.remPending.append(id(sprite))



    def BlinkSpriteA(self, sprite, a, time = 1000.0, maxCount = 10, passColor = 1, minA = 0.0):
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        key = id(sprite)
        self.blinksA[key] = (sprite,
         a,
         minA,
         time,
         maxCount,
         passColor)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread)



    def BlinkSpriteRGB(self, sprite, r, g, b, time = 1000.0, maxCount = 10, passColor = 1):
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        key = id(sprite)
        self.blinksRGB[key] = (sprite,
         r,
         g,
         b,
         time,
         maxCount,
         passColor)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread)



    def _BlinkThread(self):
        start = blue.os.GetTime()
        countsA = {}
        countsRGB = {}
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        try:
            while 1:
                if not self:
                    return 
                diff = blue.os.TimeDiffInMs(start)
                rem = []
                for (key, each,) in self.blinksA.iteritems():
                    (sprite, a, minA, time, maxCount, passColor,) = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.a = minA or a
                        continue
                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(a, minA, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(minA, a, ndt)
                    if key not in countsA:
                        countsA[key] = blue.os.GetTime()
                    if maxCount and blue.os.TimeDiffInMs(countsA[key]) / time > maxCount:
                        rem.append(key)
                        color.a = minA or a
                        if key in countsA:
                            del countsA[key]

                for each in rem:
                    if each in self.blinksA:
                        del self.blinksA[each]

                rem = []
                for (key, each,) in self.blinksRGB.iteritems():
                    (sprite, r, g, b, time, maxCount, passColor,) = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        continue
                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(r, 0.0, ndt)
                        color.g = mathUtil.Lerp(g, 0.0, ndt)
                        color.b = mathUtil.Lerp(b, 0.0, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(0.0, r, ndt)
                        color.g = mathUtil.Lerp(0.0, g, ndt)
                        color.b = mathUtil.Lerp(0.0, b, ndt)
                    if key not in countsRGB:
                        countsRGB[key] = blue.os.GetTime()
                    if maxCount and blue.os.TimeDiffInMs(countsRGB[key]) / time > maxCount:
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        if key in countsRGB:
                            del countsRGB[key]

                for each in rem:
                    if each in self.blinksRGB:
                        del self.blinksRGB[each]

                self.remPending = []
                if not len(self.blinksA) and not len(self.blinksRGB) or not self.blink_running:
                    self.blinksA = {}
                    self.blinksRGB = {}
                    self.blink_running = False
                    break
                blue.pyos.synchro.Yield()

        except Exception:
            self.blink_running = False
            log.LogException()
            sys.exc_clear()



    def Fade(self, fr, to, sprite, time = 500.0):
        ndt = 0.0
        start = blue.os.GetTime(1)
        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start) / time, 1.0)
            sprite.color.a = mathUtil.Lerp(fr, to, ndt)
            blue.pyos.synchro.Yield()




    def FadeRGB(self, fr, to, sprite, time = 500.0):
        ndt = 0.0
        start = blue.os.GetTime(1)
        while ndt != 1.0:
            ndt = min(float(blue.os.TimeDiffInMs(start)) / float(time), 1.0)
            sprite.color.r = mathUtil.Lerp(fr[0], to[0], ndt)
            sprite.color.g = mathUtil.Lerp(fr[1], to[1], ndt)
            sprite.color.b = mathUtil.Lerp(fr[2], to[2], ndt)
            blue.pyos.synchro.Yield()




    def Rotate(self, uitransform, time = 1.0, fromRot = 360.0, toRot = 0.0):
        uthread.new(self._Rotate, uitransform, time, fromRot, toRot)



    def _Rotate(self, uitransform, time, fromRot, toRot):
        time *= 1000
        i = 0
        while not uitransform.destroyed:
            (start, ndt,) = (blue.os.GetTime(), 0.0)
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start) / time, 1.0))
                deg = mathUtil.Lerp(fromRot, toRot, ndt)
                rad = mathUtil.DegToRad(deg)
                uitransform.SetRotation(rad)
                blue.pyos.synchro.Yield()





    def Browse(self, msgkey, dict):
        if msgkey == 'BrowseHtml':
            blue.os.ShellExecute(dict['url'])
        elif msgkey == 'BrowseIGB':
            browser = uicore.cmd.OpenBrowser(**dict)



    def ForceCursorUpdate(self):
        if uicore.uilib:
            uicore.UpdateCursor(uicore.uilib.mouseOver, 1)



    def SortGlobalLayer(self):
        order = ['mapbrowser',
         'neocom',
         'mapbutton',
         'locationInfo']
        order.reverse()
        glbl = uicore.layer.main
        for each in order:
            wnd = uiutil.FindChild(glbl, each)
            if wnd:
                uiutil.SetOrder(wnd, 0)




    def OnContactLoggedOn(self, charID, force = 0):
        if not force and not sm.GetService('addressbook').IsInAddressBook(charID, 'contact'):
            return 
        if not sm.GetService('addressbook').IsInWatchlist(charID):
            return 
        if force or charID not in self.showinguserson and charID != session.charid and settings.user.ui.Get('showwhencontactonline', 1):
            self.showinguserson.append(charID)
            icon = form.OnOfflineUserEntry(parent=uicore.desktop, idx=1)
            icon.Startup(charID, 1)



    def OnContactLoggedOff(self, charID):
        if not sm.GetService('addressbook').IsInAddressBook(charID, 'contact'):
            return 
        if not sm.GetService('addressbook').IsInWatchlist(charID):
            return 
        if charID not in self.showingusersoff and charID != session.charid and settings.user.ui.Get('showwhencontactoffline', 1):
            self.showingusersoff.append(charID)
            icon = form.OnOfflineUserEntry(parent=uicore.desktop, idx=1)
            icon.Startup(charID, 0)



    def CharacterDoneOff(self, charID):
        if charID in self.showingusersoff:
            self.showingusersoff.remove(charID)



    def CharacterDoneOn(self, charID):
        if charID in self.showinguserson:
            self.showinguserson.remove(charID)



    def CheckKeyUp(self, wnd, msgID, vkey_flag):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        (vkey, flag,) = vkey_flag
        if hasattr(wnd, 'KeyUp') and not wnd.destroyed:
            if wnd.KeyUp(vkey, flag):
                return 1
        if vkey == uiconst.VK_CONTROL:
            return self.CheckCtrlUp(wnd, msgID, vkey)
        return 1



    def CheckCtrlUp(self, wnd, msgID, ckey):
        sm.StartService('tactical').RemoveDelayedOverviewEntries()
        self.freezeOverview = 0
        if uix.GetInflightNav(0):
            uix.GetInflightNav(0).CloseZoomCursor()
        if eve.chooseWndMenu and not eve.chooseWndMenu.destroyed and eve.chooseWndMenu.state != uiconst.UI_HIDDEN:
            eve.chooseWndMenu.ChooseHilited()
        eve.chooseWndMenu = None
        return 1



    def CheckKeyDown(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if ctrl and alt and not shift and session.solarsystemid and not getattr(eve, 'chooseWndMenu', None) and uix.GetInflightNav(0):
            uix.GetInflightNav(0).ShowZoomCursor()
        elif not ctrl and alt and not shift and session.solarsystemid:
            sm.GetService('bracket').ShowAllHidden()
        return 1



    def GetStation(self, stationid, getall = 0):
        if self.stationsdata is None:
            data = sm.RemoteSvc('map').GetStationExtraInfo()
            self.stationsdata = data[0].Index('stationID')
            self.opservices = data[1]
            self.services = data[2]
        if getall:
            return (self.stationsdata.get(stationid, None), self.opservices, self.services)
        return self.stationsdata.get(stationid, None)



    def SetFreezeOverview(self, freeze = True):
        self.freezeOverview = freeze
        if not freeze:
            sm.GetService('tactical').RemoveDelayedOverviewEntries()



    def GetOverviewFreezeMode(self):
        return self.freezeOverview



