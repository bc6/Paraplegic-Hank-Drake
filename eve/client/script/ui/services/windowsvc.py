import service
import uix
import uiutil
import mathUtil
import blue
import uthread
import xtriui
import form
import trinity
import util
import draw
import sys
import types
import uicls
import uiconst
BTNLEFT = 140

class WindowMgr(service.Service):
    __guid__ = 'svc.window'
    __servicename__ = 'window'
    __displayname__ = 'Window Service'
    __dependencies__ = ['form']
    __exportedcalls__ = {'Reset': [],
     'RegisterStack': [],
     'UnregisterStack': [],
     'GetStack': [],
     'ResetToDefaults': [],
     'LoadUIColors': [],
     'RegisterWindow': [],
     'UnregisterWindow': [],
     'RegisterGroup': [],
     'UnregisterGroup': [],
     'MinimizeWindow': [],
     'MaximizeWindow': [],
     'NotMinimized': [],
     'GetWindows': [],
     'GetWindow': [],
     'GetActiveWnd': [],
     'OpenCorpHangar': [],
     'OpenCargo': [],
     'OpenDrones': [],
     'OpenContainer': [],
     'CloseContainer': [],
     'StartCEOTradeSession': [],
     'BlinkWindow': [],
     'OpenWindows': []}
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnCapacityChange',
     'ProcessRookieStateChange',
     'OnEndChangeDevice',
     'ProcessDeviceChange']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Window Service')
        self.LoadUIColors()
        self.initingWindows = False
        self.groups = []
        self.stacks = {}
        self.windowbtns = []



    def Stop(self, memStream = None):
        self.LogInfo('Stopping Window Service')
        service.Service.Stop(self)



    def ProcessRookieStateChange(self, state):
        if sm.GetService('connection').IsConnected():
            self.OpenWindows()



    def ProcessDeviceChange(self):
        pass



    def OnEndChangeDevice(self, change, *args):
        if 'BackBufferHeight' in change or 'BackBufferWidth' in change:
            self.UpdateWindowPositions(change)



    def UpdateWindowPositions(self, deviceChange):
        if trinity.app is None:
            return 
        d = uicore.desktop
        (oldBBW, newBBW,) = deviceChange.get('BackBufferWidth', (d.width, d.width))
        (oldBBH, newBBH,) = deviceChange.get('BackBufferHeight', (d.height, d.height))
        wDiff = newBBW - oldBBW
        hDiff = newBBH - oldBBH
        all = self.GetValidWindows(getModals=True, floatingOnly=True, getHidden=True)
        (neoleft, neoright,) = sm.GetService('neocom').GetSideOffset()
        done = []
        for wnd in all:
            if wnd.sr.stack is not None:
                continue
            if wnd in done:
                continue
            if getattr(wnd, 'isImplanted', None):
                continue
            cornerAlignment = self.GetWndCornerAlignment(wnd)
            if cornerAlignment:
                (corner, wndChainImIn,) = cornerAlignment
                if 'right' in corner:
                    wnd.left += wDiff
                if 'bottom' in corner:
                    wnd.top += hDiff
                continue
            wndGroup = wnd.FindConnectingWindows(wnd)
            (l, t, r, b,) = self.GetBoundries(wndGroup, oldBBW, oldBBH)
            if t in (0, 16):
                pass
            elif b in (0, 16):
                for gwnd in wndGroup:
                    gwnd.top += hDiff

            else:
                oldCenterY = (oldBBH - (b - t)) / 2
                yPortion = oldCenterY / float(oldBBH)
                newCenterY = int(yPortion * newBBH)
                cyDiff = newCenterY - oldCenterY
                for gwnd in wndGroup:
                    gwnd.top += cyDiff

            if l in (0, neoleft, neoleft + 16):
                pass
            elif r in (0, neoright, neoright + 16):
                for gwnd in wndGroup:
                    gwnd.left += wDiff

            else:
                oldCenterX = (oldBBW - (r - l)) / 2
                xPortion = oldCenterX / float(oldBBW)
                newCenterX = int(xPortion * newBBW)
                cxDiff = newCenterX - oldCenterX
                for gwnd in wndGroup:
                    gwnd.left += cxDiff

            done += wndGroup

        self.ValidateWindows()



    def TryAlignToCornerGroup(self, wnd):
        cornerAlignment = self.GetWndCornerAlignment(wnd)
        if cornerAlignment:
            windowGroups = self.GetWindowGroups(checking=1, cornerCheck=1)
            (corner, wndChainImIn,) = cornerAlignment
            wndChainImIn = list(wndChainImIn)
            if corner in windowGroups:
                if wnd.name in wndChainImIn:
                    myIdxInChain = wndChainImIn.index(wnd.name)
                else:
                    myIdxInChain = max(0, len(wndChainImIn) - 1)
                wndsInCorner = list(windowGroups[corner])
                if corner in ('topright', 'topleft'):
                    side = 'bottom'
                    cside = 'top'
                else:
                    side = 'top'
                    cside = 'bottom'
                    wndsInCorner.reverse()
                prevWndName = wndsInCorner[max(0, min(len(wndsInCorner) - 1, myIdxInChain - 1))]
                prevWnd = self.GetWindow(prevWndName)
                if prevWnd and prevWnd != wnd and prevWnd.name in wndChainImIn:
                    prevWndIdxInChain = wndChainImIn.index(prevWnd.name)
                    if prevWndIdxInChain >= myIdxInChain:
                        side = cside
                    prevWnd.AttachWindow(wnd, side, 0)
                    return True
                maxRange = len(wndChainImIn)
                rnge = [ i for i in xrange(myIdxInChain, maxRange) ]
                if myIdxInChain > 0:
                    rnge += [ abs(i - myIdxInChain) - 1 for i in xrange(0, myIdxInChain) ]
                for idx in rnge:
                    checkWnd = self.GetWindow(wndChainImIn[idx])
                    if checkWnd and checkWnd != wnd:
                        checkWnd.AttachWindow(wnd, side, 0)
                        return True

            elif 'top' in corner:
                wnd.top = 16
            elif 'bottom' in corner:
                wnd.top = uicore.desktop.height - wnd.height - 16
            (neoleft, neoright,) = sm.GetService('neocom').GetSideOffset()
            if 'left' in corner:
                wnd.left = neoleft + 16
            elif 'right' in corner:
                wnd.left = uicore.desktop.width - wnd.width - 16 - neoright
        return False



    def CheckCorners(self):
        blue.pyos.synchro.Yield()
        windowGroups = self.GetWindowGroups(checking=1, cornerCheck=1)
        current = self._GetCurrentCornerAlignment()
        for cornerKey in windowGroups:
            wndNames = list(windowGroups[cornerKey])
            if 'bottom' in cornerKey:
                wndNames.reverse()
            i = 0
            if cornerKey in current and wndNames[0] in current[cornerKey]:
                i = current[cornerKey].index(wndNames[0])
            for wndName in wndNames:
                for currentCornerKey in current:
                    if cornerKey == currentCornerKey:
                        continue
                    inCurrentCorner = current[currentCornerKey]
                    if wndName in inCurrentCorner:
                        inCurrentCorner.remove(wndName)

                if cornerKey not in ('topright', 'topleft', 'bottomright', 'bottomleft'):
                    continue
                if cornerKey not in current:
                    current[cornerKey] = []
                if wndName not in current[cornerKey]:
                    current[cornerKey].insert(i, wndName)
                i += 1


        settings.user.windows.Set('windowCornerGroups_1', current)



    def _GetCurrentCornerAlignment(self):
        current = settings.user.windows.Get('windowCornerGroups_1', 'notset')
        if current == 'notset':
            current = {'topright': ['selecteditemview',
                          'overview',
                          'droneview',
                          'lobby'],
             'bottomleft': ['stack1']}
        return current



    def GetWndCornerAlignment(self, wnd):
        (wndname, prefsID,) = self.GetNameAndDefaultPrefsID(wnd)
        current = self._GetCurrentCornerAlignment()
        for cornerKey in current:
            if cornerKey and wndname in current[cornerKey]:
                return (cornerKey, current[cornerKey])




    def GetWindowGroups(self, refresh = 0, checking = 0, cornerCheck = 0):
        d = uicore.desktop
        all = self.GetValidWindows(1, floatingOnly=True)
        (neoleft, neoright,) = sm.GetService('neocom').GetSideOffset()
        knownGroups = {}
        for wnd in all:
            if wnd.sr.stack is not None:
                continue
            if cornerCheck:
                wndGroup = wnd.FindConnectingWindows(wnd, 'top', fullSideOnly=True)[1:] + wnd.FindConnectingWindows(wnd, 'bottom', fullSideOnly=True)
            else:
                wndGroup = wnd.FindConnectingWindows(wnd)
            (l, t, r, b,) = self.GetBoundries(wndGroup)
            sorted = uiutil.SortListOfTuples([ ((_wnd.top, _wnd.left), _wnd) for _wnd in wndGroup ])
            groupNames = tuple([ _wnd.name for _wnd in sorted if getattr(_wnd, 'registerCornerAlignment', 1) ])
            if t in (0, 16):
                side = 'top'
            elif b in (0, 16):
                side = 'bottom'
            else:
                side = ''
            if l in (0, neoleft, neoleft + 16):
                side += 'left'
            elif r in (0, neoright, neoright + 16):
                side += 'right'
            if checking:
                if side in knownGroups:
                    if groupNames != knownGroups[side]:
                        knownGroups[side] += groupNames
                else:
                    knownGroups[side] = groupNames
            elif side:
                knownGroups[(groupNames, side)] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)
            else:
                knownGroups[(groupNames, 'left')] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)
                knownGroups[(groupNames, 'top')] = (l,
                 t,
                 r,
                 b,
                 d.width,
                 d.height)

        return knownGroups



    def ValidateWindows(self):
        d = uicore.desktop
        all = self.GetValidWindows(1, floatingOnly=True)
        for wnd in all:
            if wnd.align != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))




    def GetBoundries(self, wnds, dw = None, dh = None):
        d = uicore.desktop
        dw = dw or d.width
        dh = dh or d.height
        (l, t, r, b,) = self.GetGroupRect(wnds)
        return (l,
         t,
         dw - r,
         dh - b)



    def GetGroupRect(self, group, getAbsolute = 0):
        if not len(group):
            return (0, 0, 0, 0)
        (l, t, w, h,) = group[0].GetAbsolute()
        r = l + w
        b = t + h
        for wnd in group[1:]:
            (wl, wt, ww, wh,) = wnd.GetAbsolute()
            l = min(l, wl)
            t = min(t, wt)
            r = max(r, wl + ww)
            b = max(b, wt + wh)

        if getAbsolute:
            return (l,
             t,
             r - l,
             b - t)
        return (l,
         t,
         r,
         b)



    def GetGroupAbsolute(self, group):
        return self.GetGroupRect(group, 1)



    def DoSessionChanging(self, isRemote, session, change):
        if not eve.session.charid:
            for layer in (uicore.layer.tabs, uicore.layer.map):
                for each in layer.children:
                    each.Close()





    def OnSessionChanged(self, isRemote, session, change):
        if sm.GetService('connection').IsConnected() and 'locationid' in change:
            self.OpenWindows()



    def BlinkWindow(self, wnd):
        stack = getattr(wnd.sr, 'stack', None)
        if wnd.state == uiconst.UI_HIDDEN and wnd.sr.tab and hasattr(wnd.sr.tab, 'Blink'):
            wnd.sr.tab.Blink(1)
        if wnd.state == uiconst.UI_HIDDEN and wnd.sr.btn and hasattr(wnd.sr.btn, 'SetBlink'):
            wnd.sr.btn.SetBlink(1)
        elif stack is not None and (stack.state != uiconst.UI_NORMAL or wnd.state != uiconst.UI_NORMAL):
            if stack.sr.btn and hasattr(stack.sr.btn, 'SetBlink'):
                stack.sr.btn.SetBlink(1)



    def GetDefaults(self, windowname):
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        defaults = {'generic': [(dw - 256) / 2,
                     (dh - 128) / 2,
                     256,
                     128,
                     0,
                     0,
                     None,
                     0],
         'monitor': [dw - 300 - rightpush,
                     (dh - 164) / 2,
                     300,
                     164,
                     0,
                     0,
                     None,
                     0],
         'modal': [(dw - 340) / 2,
                   (dh - 210) / 2,
                   340,
                   210,
                   0,
                   1,
                   None,
                   0],
         'notepad': [(dw - 400) / 2,
                     (dh - 300) / 2,
                     400,
                     300,
                     0,
                     0,
                     None,
                     0],
         'progresswindow': [0,
                            0,
                            340,
                            96,
                            0,
                            1,
                            None,
                            0],
         'browser': [dw - 300 - rightpush,
                     0,
                     300,
                     dh - 200,
                     0,
                     0,
                     None,
                     0],
         'virtualbrowser': [(dw - 400) / 2,
                            (dh - 340) / 2,
                            400,
                            300,
                            0,
                            0,
                            None,
                            0],
         'charactersheet': [100,
                            32,
                            256,
                            610,
                            0,
                            0,
                            None,
                            0],
         'aura9': [dw - 360 - rightpush,
                   dh - 270,
                   350,
                   240,
                   0,
                   0,
                   None,
                   0],
         'help': [(dw - 300) / 2,
                  (dh - 458) / 2,
                  300,
                  458,
                  0,
                  0,
                  None,
                  0],
         'chatchannel': [leftpush,
                         dh - 200,
                         317,
                         200,
                         0,
                         1,
                         'stack1',
                         0],
         'corpchannel': [leftpush,
                         dh - 200,
                         317,
                         200,
                         0,
                         1,
                         'stack1',
                         0],
         'localchannel': [leftpush,
                          dh - 200,
                          317,
                          200,
                          0,
                          1,
                          'stack1',
                          0],
         'stack1': [leftpush,
                    dh - 200,
                    317,
                    200,
                    0,
                    1,
                    None,
                    0],
         'container': [leftpush + 317,
                       dh - 200,
                       317,
                       200,
                       0,
                       0,
                       '126831469216044537',
                       0],
         '126831469216044537': [leftpush + 317,
                                dh - 200,
                                317,
                                200,
                                0,
                                0,
                                None,
                                0],
         'market': [leftpush,
                    0,
                    dw - 264 - leftpush,
                    uicore.desktop.height - 180,
                    0,
                    0,
                    None,
                    0],
         'calculator': [leftpush,
                        0,
                        150,
                        150,
                        0,
                        0,
                        None,
                        0],
         'transmission': [(dw - 360) / 2,
                          (dh - 240) / 2 + 32,
                          360,
                          240,
                          0,
                          0,
                          None,
                          0],
         'mapspalette': [leftpush,
                         128,
                         320,
                         320,
                         0,
                         0,
                         None,
                         0],
         'manufacturing': [(dw - 440) / 2,
                           (dh - 300) / 2,
                           440,
                           300,
                           0,
                           0,
                           None,
                           0],
         'contracts': [(dw - 630) / 2,
                       (dh - 500) / 2,
                       630,
                       500,
                       0,
                       0,
                       None,
                       0],
         'fitting': [(dw - 680) / 2,
                     (dh - 500) / 2,
                     680,
                     500,
                     0,
                     0,
                     None,
                     0],
         'militia': [(dw - 710) / 2,
                     (dh - 540) / 2,
                     710,
                     540,
                     0,
                     0,
                     None,
                     0],
         'corporation': [(dw - 550) / 2,
                         (dh - 590) / 2,
                         550,
                         590,
                         0,
                         0,
                         None,
                         0],
         'wallet': [(dw - 560) / 2,
                    (dh - 256) / 2,
                    560,
                    256,
                    0,
                    0,
                    None,
                    0],
         'market': [leftpush,
                    0,
                    dw - 264 - leftpush,
                    dh - 180,
                    0,
                    0,
                    None,
                    0],
         'selecteditemview': [dw - 256 - 16 - rightpush,
                              16,
                              256,
                              92,
                              0,
                              1,
                              None,
                              1],
         'overview': [dw - 256 - 16 - rightpush,
                      108,
                      256,
                      160,
                      0,
                      1,
                      None,
                      1],
         'droneview': [dw - 256 - 16 - rightpush,
                       268,
                       256,
                       160,
                       0,
                       1,
                       None,
                       1],
         'jukebox': [(dw - 600) / 2,
                     (dh - 450) / 2,
                     600,
                     450,
                     0,
                     0,
                     None,
                     0],
         'jukeboxMinimized': [(dw - 250) / 2,
                              (dh - 40) / 2,
                              250,
                              40,
                              0,
                              0,
                              None,
                              0],
         'lobby': [dw - 266 - rightpush,
                   0,
                   266,
                   dh,
                   0,
                   1,
                   None,
                   0],
         'newmessage': [(dw - 300) / 2,
                        (dh - 350) / 2,
                        300,
                        350,
                        0,
                        0,
                        None,
                        0],
         'mail': [(dw - 600) / 2,
                  (dh - 450) / 2,
                  600,
                  450,
                  0,
                  0,
                  None,
                  0],
         'fleetwindow': [(dw - 400) / 2,
                         (dh - 300) / 2,
                         400,
                         300,
                         0,
                         0,
                         None,
                         0],
         'infrastructhubsettings': [(dw - 230) / 2,
                                    (dh - 70) / 2,
                                    230,
                                    70,
                                    0,
                                    0,
                                    None,
                                    0],
         'reprocessing': [(dw - 405) / 2,
                          (dh - 270) / 2,
                          405,
                          270,
                          0,
                          0,
                          None,
                          0]}
        if eve.session.role & service.ROLEMASK_ELEVATEDPLAYER:
            defaults['insider'] = [leftpush + 200,
             0,
             0,
             0,
             0,
             1,
             None,
             0]
        if defaults.has_key(windowname):
            return defaults[windowname]
        if windowname is not None and windowname.startswith('infowindow'):
            (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
            return [leftpush,
             0,
             256,
             340,
             0,
             0,
             None,
             0]
        if windowname is not None and windowname.startswith('agentinteraction'):
            agentInteractWidth = 835
            agentInteractHeight = 545
            return [(dw - agentInteractWidth) / 2,
             (dh - agentInteractHeight) / 2,
             agentInteractWidth,
             agentInteractHeight,
             0,
             0,
             None,
             0]
        return defaults['generic']



    def ResetToggleState(self):
        self.toggleState = None



    def ToggleWindows(self):
        prestate = getattr(self, 'toggleState', None)
        if prestate:
            for wndname in prestate:
                wnd = self.GetWindow(wndname)
                if wnd and wnd.IsCollapsed():
                    wnd.Expand()

            self.toggleState = None
            return 1
        state = []
        wnds = self.GetValidWindows(floatingOnly=True)
        for wnd in wnds:
            if not wnd.IsCollapsed():
                wnd.Collapse()
                state.append(wnd.name)

        if not state:
            for wnd in wnds:
                if wnd.IsCollapsed():
                    wnd.Expand()

        self.toggleState = state
        if state:
            return 1



    def ResetAll(self):
        settings.user.windows.Delete('windowSizesAndPositions_1')
        settings.user.windows.Delete('stacksWindows')
        settings.user.windows.Delete('windowCornerGroups_1')
        settings.user.ui.Delete('targetOrigin')
        for statename in ['pinned',
         'open',
         'minimized',
         'collapsed',
         'locked']:
            settings.user.windows.Set('%sWindows' % statename, {})

        uthread.new(self.RealignWindows)



    def RealignWindows(self):
        wnds = self.GetValidWindows(getHidden=1)
        for each in wnds:
            if each.sr.stack is None and not getattr(each, 'isImplanted', None):
                each.InitializeSize()

        for each in wnds:
            if each.sr.stack is None and not getattr(each, 'isImplanted', None):
                skipState = bool(each.state == uiconst.UI_HIDDEN)
                each.InitializeStatesAndPosition(skipWelcomePage=True, skipState=skipState)

        sm.GetService('target').ArrangeTargets()



    def ResetToDefaults(self, wndname):
        for each in ('windowSizesAndPositions_1', 'stacksWindows', 'windowCornerGroups_1pinnedWindows', 'openWindows', 'minimizedWindows', 'collapsedWindows', 'lockedWindows'):
            prefs = settings.user.windows.Get(each, {})
            if wndname in prefs:
                del prefs[wndname]
                settings.user.windows.Set(each, prefs)




    def GetNameAndDefaultPrefsID(self, wnd):
        if type(wnd) in types.StringTypes:
            return (wnd, None)
        else:
            return (wnd.name, wnd.defaultPrefsID)



    def GetWndState(self, wnd, statename):
        (wndname, prefsID,) = self.GetNameAndDefaultPrefsID(wnd)
        all = settings.user.windows.Get('%sWindows' % statename, {})
        if wndname in all:
            return all[wndname]
        (left, top, width, height, minimized, open, stackname, pinned,) = self.GetDefaults(prefsID or wndname)
        stateIdx = ['pinned',
         'open',
         'minimized',
         'collapsed',
         'locked'].index(statename)
        return all.get(wndname, [pinned,
         open,
         minimized,
         0,
         0][stateIdx])



    def GetWndStack(self, wnd):
        (wndname, prefsID,) = self.GetNameAndDefaultPrefsID(wnd)
        all = settings.user.windows.Get('stacksWindows', {})
        if wndname in all:
            return all[wndname]
        (left, top, width, height, minimized, open, stackname, pinned,) = self.GetDefaults(prefsID or wndname)
        return all.get(wndname, stackname)



    def GetWndPositionAndSize(self, wnd):
        (wndname, prefsID,) = self.GetNameAndDefaultPrefsID(wnd)
        all = settings.user.windows.Get('windowSizesAndPositions_1', {})
        if wndname in all:
            (left, top, width, height, cdw, cdh,) = all[wndname]
        else:
            (left, top, width, height, minimized, open, stackname, pinned,) = self.GetDefaults(prefsID or wndname)
            (left, top, width, height, cdw, cdh,) = all.get(wndname, (left,
             top,
             width,
             height,
             uicore.desktop.width,
             uicore.desktop.height))
        (dw, dh,) = (uicore.desktop.width, uicore.desktop.height)
        if cdw != dw:
            wDiff = dw - cdw
            (neoleft, neoright,) = sm.GetService('neocom').GetSideOffset()
            if left + width in (cdw, cdw - neoright, cdw - neoright - 16):
                left += wDiff
            elif left not in (0, neoleft, neoleft + 16):
                oldCenterX = (cdw - width) / 2
                xPortion = oldCenterX / float(cdw)
                newCenterX = int(xPortion * dw)
                cxDiff = newCenterX - oldCenterX
                left += cxDiff
        if cdh != dh:
            hDiff = dh - cdh
            if top in (0, 16):
                pass
            elif top + height in (cdh, cdh - 16):
                top += hDiff
            oldCenterY = (cdh - height) / 2
            yPortion = oldCenterY / float(cdh)
            newCenterY = int(yPortion * dh)
            cyDiff = newCenterY - oldCenterY
            top += cyDiff
        return (left,
         top,
         width,
         height,
         dw,
         dh)



    def Reset(self):
        self.groups = []
        self.stacks = {}
        self.windowbtns = []
        uicore.registry.Release()



    def OpenWindows(self):
        if eve.rookieState and eve.rookieState < 10:
            return 
        self.initingWindows = True
        instation = []
        if eve.session.stationid:
            office = sm.GetService('corp').GetOffice()
            if office is not None:
                instation += [['corpHangar_%s' % office.itemID, self.OpenCorpHangar]]
        instation += [['corpMarketHangar', uicore.cmd.OpenCorpDeliveries]]
        if eve.rookieState is not None or not settings.user.windows.Get('dockshipsanditems', 0):
            instation += [['hangarFloor', uicore.cmd.OpenHangarFloor], ['shipHangar', uicore.cmd.OpenShipHangar], ['drones_%s' % eve.session.shipid, uicore.cmd.OpenDroneBayOfActiveShip]]
        anywhere = [['mail', uicore.cmd.OpenMail],
         ['wallet', uicore.cmd.OpenWallet],
         ['corporation', uicore.cmd.OpenCorporationPanel],
         ['assets', uicore.cmd.OpenAssets],
         ['channels', uicore.cmd.OpenChannels],
         ['journal', uicore.cmd.OpenJournal],
         ['jukebox', uicore.cmd.OpenJukebox],
         ['logger', uicore.cmd.OpenLog],
         ['charactersheet', uicore.cmd.OpenCharactersheet],
         ['addressbook', uicore.cmd.OpenPeopleAndPlaces],
         ['logger', uicore.cmd.OpenLog],
         ['market', uicore.cmd.OpenMarket],
         ['notepad', uicore.cmd.OpenNotepad],
         ['shipCargo_%s' % eve.session.shipid, uicore.cmd.OpenCargoHoldOfActiveShip]]
        if eve.session.stationid:
            sm.GetService('gameui').ScopeCheck(['station', 'station_inflight'])
            anywhere += instation
        elif eve.session.solarsystemid and eve.session.shipid:
            sm.GetService('gameui').ScopeCheck(['inflight', 'station_inflight'])
            anywhere += [['scanner', uicore.cmd.OpenScanner]]
        else:
            sm.GetService('gameui').ScopeCheck()
        for each in anywhere:
            (windowname, func,) = each
            if (self.GetWndState(windowname, 'open') and self.GetWndStack(windowname) or not self.GetWndState(windowname, 'minimized')) and self.GetWindow(windowname) is None:
                apply(func)

        self.initingWindows = False



    def SetWindowColor(self, r, g, b, a, what = 'color'):
        settings.user.windows.Set('wnd%s' % what.capitalize(), (r,
         g,
         b,
         a))
        sm.ScatterEvent('OnUIColorsChanged')



    def GetWindowColors(self):
        return (settings.user.windows.Get('wndColor', eve.themeColor),
         settings.user.windows.Get('wndBackgroundcolor', eve.themeBgColor),
         settings.user.windows.Get('wndComponent', eve.themeCompColor),
         settings.user.windows.Get('wndComponentsub', eve.themeCompSubColor))



    def ResetWindowColors(self, *args):
        self.LoadUIColors(reset=True)



    def LoadUIColors(self, reset = 0):
        reset = reset or eve.session.userid is None
        if reset:
            self.SetWindowColor(what='Color', *eve.themeColor)
            self.SetWindowColor(what='Background', *eve.themeBgColor)
            self.SetWindowColor(what='Component', *eve.themeCompColor)
            self.SetWindowColor(what='Componentsub', *eve.themeCompSubColor)
        sm.ScatterEvent('OnUIColorsChanged')



    def RegisterWindow(self, wnd):
        uicore.registry.RegisterWindow(wnd)



    def UnregisterWindow(self, wnd):
        uicore.registry.UnregisterWindow(wnd)
        for window in uicore.registry.GetWindows():
            if window is None or window.destroyed:
                uicore.registry.UnregisterWindow(window)




    def RegisterGroup(self, group):
        self.groups.append(group)



    def UnregisterGroup(self, group):
        if group in self.groups:
            self.groups.remove(group)



    def GetWindows(self):
        return uicore.registry.GetWindows()



    def GetValidWindows(self, getModals = 0, floatingOnly = False, getHidden = 0):
        return uicore.registry.GetValidWindows(getModals, floatingOnly, getHidden)



    def GetActiveWnd(self):
        all = uicore.registry.GetWindows()
        active = uicore.registry.GetActive()
        for each in all:
            if each == active:
                return each
            if uiutil.IsUnder(active, each):
                return each




    def GetWindow(self, windowname, create = 0, maximize = 0, decoClass = None, ignoreCurrent = 0, forceNoStack = 0, expandIfCollapsed = None, skipCornerAligmentCheck = False, **kw):
        windowClass = decoClass
        wnd = None
        if not ignoreCurrent:
            w = uicore.registry.GetWindow(windowname)
            if w and not w.destroyed and w.parent:
                wnd = w
        if not wnd and create:
            if windowClass is None:
                formClass = getattr(form, windowname, None)
                if formClass:
                    windowClass = formClass
                else:
                    import uicls
                windowClass = uicls.Window
            try:
                wnd = windowClass(parent=uicore.layer.main, name=windowname, **kw)
            except:
                wnd = uiutil.FindChild(uicore.layer.main, windowname)
                if wnd in uicore.layer.main.children:
                    uicore.layer.main.children.remove(wnd)
                    wnd.Close()
                raise 
            self.RegisterWindow(wnd)
            sm.ScatterEvent('OnWindowOpened', wnd)
            notifyevents = getattr(windowClass, '__notifyevents__', None)
            if notifyevents:
                sm.RegisterNotify(wnd)
            if expandIfCollapsed is None:
                expandIfCollapsed = bool(not self.initingWindows)
        if wnd and maximize:
            wnd.Maximize()
        return wnd



    def CheckControlAppearance(self, control):
        wnd = uiutil.GetWindowAbove(control)
        if wnd:
            self.ChangeControlAppearance(wnd, control)



    def ChangeControlAppearance(self, wnd, control = None):
        haveLiteFunction = [ w for w in (control or wnd).Find('trinity.Tr2Sprite2dContainer') if hasattr(w, 'LiteMode') ]
        haveLiteFunction += [ w for w in (control or wnd).Find('trinity.Tr2Sprite2dFrame') if hasattr(w, 'LiteMode') ]
        for obj in haveLiteFunction:
            obj.LiteMode(wnd.IsPinned())

        wnds = [ w for w in (control or wnd).Find('trinity.Tr2Sprite2dContainer') if w.name == '_underlay' if w not in haveLiteFunction ]
        wnd = getattr(wnd.sr, 'stack', None) or wnd
        for w in wnds:
            uiutil.Flush(w)
            if wnd.IsPinned():
                uicls.Frame(parent=w, color=(1.0, 1.0, 1.0, 0.2), padding=(-1, -1, -1, -1))
                uicls.Fill(parent=w, color=(0.0, 0.0, 0.0, 0.3))
            else:
                uicls.BumpedUnderlay(parent=w)

        frames = [ w for w in (control or wnd).Find('trinity.Tr2Sprite2dFrame') if w.name == '__underlay' if w not in haveLiteFunction ]
        for f in frames:
            self.CheckFrames(f, wnd)




    def CheckFrames(self, underlay, wnd):
        underlayParent = getattr(underlay, 'parent', None)
        if underlayParent is None:
            return 
        noBackground = getattr(underlayParent, 'noBackground', 0)
        if noBackground:
            return 
        underlayFrame = underlayParent.FindChild('underlayFrame')
        underlayFill = underlayParent.FindChild('underlayFill')
        if wnd.IsPinned():
            underlay.state = uiconst.UI_HIDDEN
            if not underlayFill:
                underlayFill = uicls.Frame(name='underlayFill', color=(0.0, 0.0, 0.0, 0.3), frameConst=uiconst.FRAME_FILLED_CORNER0, parent=underlayParent)
            else:
                underlayFill.state = uiconst.UI_DISABLED
            if not underlayFrame:
                underlayFrame = uicls.Frame(name='underlayFrame', color=(1.0, 1.0, 1.0, 0.2), frameConst=uiconst.FRAME_BORDER1_CORNER0, parent=underlayParent, pos=(-1, -1, -1, -1))
            else:
                underlayFrame.state = uiconst.UI_DISABLED
        elif not noBackground:
            underlay.state = uiconst.UI_DISABLED
        if underlayFrame:
            underlayFrame.state = uiconst.UI_HIDDEN
        if underlayFill:
            underlayFill.state = uiconst.UI_HIDDEN



    def ToggleLiteWindowAppearance(self, wnd, forceLiteState = None):
        if forceLiteState is not None:
            wnd._SetPinned(forceLiteState)
        state = uiconst.UI_DISABLED
        for each in wnd.children[:]:
            if each.name.startswith('_lite'):
                each.Close()

        if wnd.IsPinned():
            for align in (uiconst.TOLEFT,
             uiconst.TOTOP,
             uiconst.TORIGHT,
             uiconst.TOBOTTOM):
                uicls.Line(parent=wnd, align=align, color=(0.0, 0.0, 0.0, 0.3), idx=0, name='_liteline')

            uicls.Frame(parent=wnd, color=(1.0, 1.0, 1.0, 0.2), name='_liteframe')
            uicls.Fill(parent=wnd, color=(0.0, 0.0, 0.0, 0.3), name='_litefill')
            state = uiconst.UI_HIDDEN
        for each in wnd.children:
            for _each in wnd.sr.underlay.background:
                if _each.name in ('base', 'color', 'shadow', 'solidBackground'):
                    _each.state = state


        m = wnd.sr.maincontainer
        if state == uiconst.UI_DISABLED:
            m.left = m.top = m.width = m.height = 1
        else:
            m.left = m.top = m.width = m.height = 0
        self.ChangeControlAppearance(wnd)



    def DestroyWindows(self):
        globalL = uicore.layer.main
        for each in globalL.children[:]:
            if getattr(each, 'isDockWnd', 0):
                each.Close()




    def MinimizeWindow(self, wnd, animate = True):
        if not wnd or wnd.destroyed or wnd.IsMinimized() or getattr(wnd.sr, 'btn', None):
            return 
        wnd.OnStartMinimize_()
        wnd.changing = 1
        uicore.registry.CheckMoveActiveState(wnd)
        btn = uicls.WindowButton(parent=uicore.layer.tabs, name='windowButton_%s' % wnd.name, align=uiconst.BOTTOMLEFT, pos=(0, 0, 0, 16), wnd=wnd)
        wnd.sr.btn = wnd.sr.minimizedBtn = btn
        self.windowbtns.append(btn)
        self.RefreshWindowBtns()
        if animate:
            (l, t, w, h,) = wnd.GetAbsolute()
            frame = uicls.Frame(parent=wnd.parent, align=uiconst.TOPLEFT, left=l, top=t, width=w, height=h)
            uthread.new(self.MoveWnd, frame, btn)
        btn.state = uiconst.UI_NORMAL
        wnd._SetMinimized(True)
        wnd.state = uiconst.UI_HIDDEN
        wnd.OnEndMinimize_()
        wnd.changing = 0
        sm.ScatterEvent('OnWindowMinimized', wnd)



    def MaximizeWindow(self, wnd, silent = 0, expandIfCollapsed = True):
        if wnd is None or wnd.destroyed or not wnd.sr:
            return 
        wnd.changing = 1
        if wnd.sr.btn:
            self.NotMinimized(wnd.sr.btn)
            wnd.sr.btn = None
            wnd.sr.minimizedBtn = None
        if getattr(wnd.sr, 'stack', None) is not None:
            wnd._SetMinimized(False)
            wnd.sr.stack.ShowWnd(wnd)
            wnd.sr.stack.Maximize()
            wnd.changing = 0
            return 
        wnd.OnStartMaximize_()
        if expandIfCollapsed and wnd.IsCollapsed():
            wnd.Expand(0)
        uiutil.SetOrder(wnd, 0)
        wnd._SetMinimized(False)
        wnd.state = uiconst.UI_NORMAL
        kick = [ w for w in wnd.Find('trinity.Tr2Sprite2dContainer') + wnd.Find('trinity.Tr2Sprite2d') if hasattr(w, '_OnResize') ]
        for each in kick:
            if hasattr(each, '_OnResize'):
                each._OnResize()

        uicore.registry.SetFocus(wnd)
        wnd.OnEndMaximize_()
        wnd.changing = 0
        sm.ScatterEvent('OnWindowMaximized', wnd)



    def ToggleWindowFocus(self, wnd):
        if wnd.sr.stack:
            if wnd.sr.stack.IsMinimized():
                wnd.sr.stack.Maximize()
            if wnd != wnd.sr.stack.GetActiveWindow():
                wnd.sr.stack.ShowWnd(wnd)
            uicore.registry.SetFocus(wnd)
        elif wnd.IsMinimized():
            wnd.Maximize()
        else:
            isOnTop = wnd.parent.children.index(wnd) == 0
            if isOnTop:
                wnd.Minimize()
            else:
                uicore.registry.SetFocus(wnd)



    def MoveWnd(self, frame, button):
        (fl, ft, fw, fh,) = frame.GetAbsolute()
        (tl, tt, tw, th,) = button.GetAbsolute()
        fromVec = trinity.TriVector(float(fl), float(ft), 0.0)
        toVec = trinity.TriVector(float(tl), float(tt), 0.0)
        dist = (fromVec - toVec).Length()
        try:
            start = blue.os.GetTime()
            time = max(50, min(100.0, dist * 0.33))
            ndt = 0.0
            while ndt != 1.0:
                ndt = min(blue.os.TimeDiffInMs(start) / time, 1.0)
                frame.top = int(mathUtil.Lerp(ft, tt, ndt))
                frame.left = int(mathUtil.Lerp(fl, tl, ndt))
                frame.width = int(mathUtil.Lerp(fw, tw, ndt))
                portion = frame.width / float(fw)
                frame.height = int(fh * portion)
                blue.pyos.synchro.Yield()


        finally:
            if frame is not None and not frame.destroyed:
                frame.Close()




    def NotMinimized(self, btn):
        if btn in self.windowbtns:
            self.windowbtns.remove(btn)
            if btn is not None and not btn.destroyed:
                btn.Close()
        self.RefreshWindowBtns()



    def RefreshWindowBtns(self):
        if not uicore.uilib:
            return 
        left = BTNLEFT
        for btn in self.windowbtns:
            if btn is None or btn.destroyed:
                self.windowbtns.remove(btn)
                continue
            if btn.wnd_wr and btn.wnd_wr():
                wnd = btn.wnd_wr()
                if wnd is None or wnd.destroyed:
                    self.windowbtns.remove(btn)
                    continue
            btn.left = left
            left += btn.width




    def RegisterStack(self, stack):
        self.stacks[stack.name] = stack



    def UnregisterStack(self, stackname):
        if stackname in self.stacks:
            del self.stacks[stackname]



    def GetStack(self, stackname = None, onatop = 0):
        if stackname is not None and stackname in self.stacks:
            stack = self.stacks[stackname]
            if stack is not None and not stack.destroyed and getattr(stack, 'sr', None) is not None:
                return stack
            del self.stacks[stackname]
        return self.GetWindow(stackname or str(blue.os.GetTime()), create=1, decoClass=uicls.WindowStack)



    def OpenCorpHangar(self, officeID = None, officeFolderID = None, info = 0):
        if officeID is None or officeFolderID is None:
            if eve.session.stationid:
                if officeID is None:
                    office = sm.GetService('corp').GetOffice()
                    if office is not None:
                        officeID = office.itemID
                        officeFolderID = office.officeFolderID
                else:
                    officeFolderID = sm.GetService('corp').GetOfficeFolderIDForOfficeID(officeID)
            else:
                eve.Message('OpenCorpHangarNotAtStation', {})
                return 
        if officeID is None or officeFolderID is None:
            if info:
                if not eve.session.stationid:
                    eve.Message('OpenCorpHangarNotAtStation', {})
                else:
                    corpStationMgr = sm.GetService('corp').GetCorpStationManager()
                    if corpStationMgr:
                        if corpStationMgr.DoesPlayersCorpHaveJunkAtStation():
                            if eve.session.corprole & const.corpRoleDirector != const.corpRoleDirector:
                                raise UserError('CrpJunkOnlyAvailableToDirector')
                            cost = corpStationMgr.GetQuoteForGettingCorpJunkBack()
                            if eve.Message('CrpJunkAcceptCost', {'cost': cost}, uiconst.YESNO) != uiconst.ID_YES:
                                return 
                            corpStationMgr.PayForReturnOfCorpJunk(cost)
                            return 
                    eve.Message('OpenCorpHangarNoHangar', {})
            return 
        container = eve.GetInventoryFromId(officeFolderID)
        container.List()
        wnd = self.GetWindow('corpHangar_%s' % officeID, create=1, maximize=1, decoClass=form.CorpHangar, windowPrefsID='corpHangarContainer', officeID=officeID)



    def OpenCorpHangarArray(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot'):
        wnd = self.GetWindow(nameLabel + '_%s' % id_, create=1, maximize=1, decoClass=form.CorpHangarArray, windowPrefsID='corpHangarArrayContainer', officeID=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag)
        wnd.displayName = name if name != None else cfg.invgroups.Get(const.groupCorporateHangarArray).name



    def OpenShipCorpHangars(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot'):
        wnd = self.GetWindow(nameLabel + '_%s' % id_, create=1, maximize=1, decoClass=form.ShipCorpHangars, windowPrefsID='shipCorpHangarContainer', officeID=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag)
        shipName = cfg.evelocations.GetIfExists(id_) or ''
        if shipName:
            shipName = shipName.name
        wnd.displayName = '%s - %s' % (mls.UI_GENERIC_CORPHANGAR, shipName)



    def OpenCargo(self, item, name, displayname = None, typeid = None):
        if session.stationid2:
            if item.groupID == const.groupCapsule:
                if eve.Message('AskActivateShip', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    sm.GetService('station').SelectShipDlg()
                return 
            decoClass = form.DockedCargoView
        elif eve.session.solarsystemid:
            decoClass = form.InflightCargoView
        else:
            self.LogError('Not inflight or docked???')
            return 
        itemID = item.itemID
        self.LogInfo('OpenCargo', itemID, name, displayname)
        wnd = self.GetWindow('shipCargoe%s' % itemID, create=1, maximize=1, decoClass=decoClass, _id=itemID, displayName=name)
        if wnd and itemID == eve.session.shipid:
            wnd.scope = 'station_inflight'



    def OpenDrones(self, id_, name, displayname = None, typeid = None):
        wnd = self.GetWindow('drones_%s' % id_, create=1, maximize=1, decoClass=form.DroneBay, _id=id_, displayName=name)
        if wnd and id_ == eve.session.shipid:
            wnd.scope = 'station_inflight'



    def OpenPlanetCargoLink(self, id_, name, displayname = None):
        wnd = self.GetWindow('planetcargo_%s' % id_, create=1, maximize=1, decoClass=form.PlanetInventory, _id=id_, displayName=name)



    def OpenContainer(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot', isWreck = False, windowPrefsID = None):
        wnd = self.GetWindow(nameLabel + '_%s' % id_, create=1, maximize=1, decoClass=form.LootCargoView, windowPrefsID=windowPrefsID, _id=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag, isWreck=isWreck)



    def CloseContainer(self, id_):
        wnd = self.GetWindow('loot_%s' % id_)
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()



    def OpenSpecialCargoBay(self, id_, name, locationFlag, nameLabel = 'specialBay'):
        wnd = self.GetWindow(nameLabel + '%s_%s' % (id_, locationFlag), create=1, maximize=1, decoClass=form.SpecialCargoBay, _id=id_, displayName=name, locationFlag=locationFlag)
        if wnd and id_ == eve.session.shipid:
            wnd.scope = 'station_inflight'



    def StartCEOTradeSession(self, declaredByID, againstID, warID):
        try:
            otherDude = declaredByID
            if declaredByID in (eve.session.corpid, eve.session.allianceid):
                otherDude = againstID
            if util.IsAlliance(otherDude):
                otherDude = sm.GetService('alliance').GetAlliance(otherDude).executorCorpID
            if otherDude is None:
                raise UserError('CanNotSurrenderToAllianceInTurmoil')
            corporation = sm.GetService('corp').GetCorporation(otherDude, 1)
            sm.GetService('pvptrade').StartCEOTradeSession(corporation.ceoID, warID)
        except UserError as e:
            if e.msg == 'OtherCharNotAtStation':
                if eve.Message('CantSurrenderCEONotAtStationPageInstead', {'name': e.args[1]['name']}, uiconst.YESNO) == uiconst.ID_YES:
                    sm.GetService('LSC').Invite(corporation.ceoID)
            else:
                raise 
            sys.exc_clear()



    def OnCapacityChange(self, moduleID):
        for window in uicore.registry.GetWindows():
            if window.destroyed:
                continue
            if window.__guid__ in ('form.DockedCargoView', 'form.InflightCargoView') and window.itemID == moduleID:
                window.RefreshCapacity()
            elif window.__guid__ == 'form.LootCargoView' and window.itemID == moduleID and window.hasCapacity:
                window.RefreshCapacity()




    def GetCameraLeftOffset(self, width, align = None, left = 0, *args):
        if not settings.user.ui.Get('offsetUIwithCamera', False):
            return 0
        offset = int(settings.user.ui.Get('cameraOffset', 0))
        if not offset:
            return 0
        if align in [uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM]:
            camerapush = int(offset / 100.0 * uicore.desktop.width / 3.0)
            allowedOffset = int((uicore.desktop.width - width) / 2) - 10
            if camerapush < 0:
                return max(camerapush, -allowedOffset - left)
            if camerapush > 0:
                return min(camerapush, allowedOffset + left)
        return 0




