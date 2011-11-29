import service
import uiutil
import localization
import uthread
import form
import trinity
import util
import sys
import types
import uicls
import uiconst

class WindowMgr(service.Service):
    __guid__ = 'svc.window'
    __servicename__ = 'window'
    __displayname__ = 'Window Service'
    __dependencies__ = ['form']
    __exportedcalls__ = {'LoadUIColors': [],
     'OpenCorpHangar': [],
     'OpenCargo': [],
     'OpenDrones': [],
     'OpenContainer': [],
     'CloseContainer': [],
     'StartCEOTradeSession': [],
     'OpenWindows': []}
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnCapacityChange',
     'ProcessRookieStateChange',
     'OnEndChangeDevice',
     'OnUIScalingChange',
     'ProcessDeviceChange']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Window Service')
        self.LoadUIColors()



    def Stop(self, memStream = None):
        self.LogInfo('Stopping Window Service')
        service.Service.Stop(self)



    def ProcessRookieStateChange(self, state):
        if sm.GetService('connection').IsConnected():
            self.OpenWindows()



    def ProcessDeviceChange(self, *args):
        pass



    def OnEndChangeDevice(self, change, *args):
        if 'BackBufferHeight' in change or 'BackBufferWidth' in change:
            self.RealignWindows()
            sm.GetService('device').SetupUIScaling()



    def OnUIScalingChange(self, change, *args):
        self.RealignWindows()



    def ValidateWindows(self):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(1, floatingOnly=True)
        for wnd in all:
            if wnd.align != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))




    def DoSessionChanging(self, isRemote, session, change):
        if not eve.session.charid:
            for layer in (uicore.layer.starmap,):
                for each in layer.children:
                    each.Close()





    def OnSessionChanged(self, isRemote, session, change):
        if sm.GetService('connection').IsConnected() and 'locationid' in change:
            self.OpenWindows()



    def ResetWindowSettings(self):
        self.RealignWindows(flushSettings=True)



    def RealignWindows(self, flushSettings = False):
        wnds = uicore.registry.GetValidWindows(getHidden=1, floatingOnly=True)
        wasInStack = []
        closeStacks = []
        triggerUpdate = []
        for each in wnds:
            if isinstance(each, uicls.WindowStackCore):
                for wnd in each.GetWindows()[:]:
                    uiutil.Transplant(wnd, each.parent)
                    wnd.state = uiconst.UI_HIDDEN
                    wnd.sr.stack = None
                    triggerUpdate.append(wnd)
                    wasInStack.append((each.windowID, wnd))

                closeStacks.append(each)
            else:
                each.state = uiconst.UI_HIDDEN
                triggerUpdate.append(each)

        for each in closeStacks:
            each.Close()

        if flushSettings:
            uicls.Window.ResetAllWindowSettings()
        for each in triggerUpdate:
            each.state = uiconst.UI_HIDDEN

        for each in triggerUpdate:
            each.InitializeSize()
            each.InitializeStatesAndPosition()

        for (prevStackID, wnd,) in wasInStack:
            if not wnd.InStack():
                self.LogWarn('RealignWindows: Wnd with windowID', wnd.windowID, 'didnt find its stack (', prevStackID, ') while reinitializing')
                wnd.align = uiconst.TOPLEFT
                wnd.ShowHeader()
                wnd.ShowBackground()
                wnd.InitializeSize()
                wnd.InitializeStatesAndPosition()

        if 'neocom' in sm.services:
            sm.StartService('neocom').UpdateNeocom()
        settings.user.ui.Delete('targetOrigin')
        sm.GetService('target').ArrangeTargets()



    def OpenWindows(self):
        if not (eve.rookieState and eve.rookieState < 10):
            instation = []
            if session.stationid2:
                office = sm.GetService('corp').GetOffice()
                if office is not None:
                    instation += [['corpHangar_%s' % office.itemID, self.OpenCorpHangar]]
            instation += [[form.CorpMarketHangar, uicore.cmd.OpenCorpDeliveries]]
            if eve.rookieState is not None or not settings.user.windows.Get('dockshipsanditems', 0):
                instation += [[form.ItemHangar, uicore.cmd.OpenHangarFloor], [form.ShipHangar, uicore.cmd.OpenShipHangar], ['drones_%s' % eve.session.shipid, uicore.cmd.OpenDroneBayOfActiveShip]]
            anywhere = [[form.MailWindow, uicore.cmd.OpenMail],
             [form.Wallet, uicore.cmd.OpenWallet],
             [form.Corporation, uicore.cmd.OpenCorporationPanel],
             [form.AssetsWindow, uicore.cmd.OpenAssets],
             [form.Channels, uicore.cmd.OpenChannels],
             [form.Journal, uicore.cmd.OpenJournal],
             [form.jukebox, uicore.cmd.OpenJukebox],
             [form.Logger, uicore.cmd.OpenLog],
             [form.CharacterSheet, uicore.cmd.OpenCharactersheet],
             [form.AddressBook, uicore.cmd.OpenPeopleAndPlaces],
             [form.RegionalMarket, uicore.cmd.OpenMarket],
             [form.Notepad, uicore.cmd.OpenNotepad],
             ['shipCargo_%s' % eve.session.shipid, uicore.cmd.OpenCargoHoldOfActiveShip]]
            if eve.session.stationid:
                sm.GetService('gameui').ScopeCheck(['station', 'station_inflight'])
                anywhere += instation
            elif eve.session.solarsystemid and eve.session.shipid:
                sm.GetService('gameui').ScopeCheck(['inflight', 'station_inflight'])
                anywhere += [[form.Scanner, uicore.cmd.OpenScanner]]
            else:
                sm.GetService('gameui').ScopeCheck()
            for each in anywhere:
                if len(each) == 1:
                    windowClass = each[0]
                    windowID = windowClass.default_windowID
                    stackID = windowClass.GetRegisteredOrDefaultStackID()
                    func = windowClass.Open
                else:
                    (windowClass_or_windowID, func,) = each
                    if type(windowClass_or_windowID) in types.StringTypes:
                        windowID = windowClass_or_windowID
                        stackID = uicls.Window.GetRegisteredOrDefaultStackID(windowID=windowClass_or_windowID)
                    else:
                        windowID = windowClass_or_windowID.default_windowID
                        stackID = windowClass_or_windowID.GetRegisteredOrDefaultStackID()
                wnd = uicls.Window.GetIfOpen(windowID)
                if (uicore.registry.GetRegisteredWindowState(windowID, 'open') and stackID or not uicore.registry.GetRegisteredWindowState(windowID, 'minimized')) and not wnd:
                    apply(func)

        form.Lobby.CloseIfOpen()
        if session.stationid2:
            if not (eve.rookieState and eve.rookieState < 5):
                form.Lobby.Open()



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



    def OpenCorpHangar(self, officeID = None, officeFolderID = None, info = 0, isMinimized = False):
        if officeID is None or officeFolderID is None:
            if session.stationid2:
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
                if not session.stationid2:
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
        container = sm.GetService('invCache').GetInventoryFromId(officeFolderID)
        container.List()
        wnd = form.CorpHangar.ToggleOpenClose(windowID='corpHangar_%s' % officeID, officeID=officeID)
        if wnd and isMinimized:
            wnd.Minimize(animate=0)



    def OpenCorpHangarArray(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot'):
        wnd = form.CorpHangarArray.Open(windowID=nameLabel + '_%s' % id_, officeID=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag)
        wnd.displayName = name if name != None else cfg.invgroups.Get(const.groupCorporateHangarArray).name



    def OpenShipCorpHangars(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot'):
        wnd = form.ShipCorpHangars.Open(windowID=nameLabel + '_%s' % id_, officeID=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag)
        wnd.displayName = localization.GetByLabel('UI/Corporations/CorpShipHangarCaption', ship=id_)



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
        wnd = decoClass.ToggleOpenClose(windowID='shipCargo_%s' % itemID, _id=itemID, displayName=name)
        if wnd and itemID == util.GetActiveShip():
            wnd.scope = 'station_inflight'



    def OpenDrones(self, id_, name, displayname = None, typeid = None):
        wnd = form.DroneBay.ToggleOpenClose(windowID='drones_%s' % id_, _id=id_, displayName=name)
        if wnd and id_ == util.GetActiveShip():
            wnd.scope = 'station_inflight'



    def OpenPlanetCustomsOffice(self, id_, name, displayname = None):
        wnd = form.PlanetaryImportExportUI.Open(windowID='customsoffice_%s' % id_, _id=id_, displayName=name)



    def OpenContainer(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot', isWreck = False, windowID = None):
        wnd = form.LootCargoView.Open(windowID=windowID or nameLabel + '_%s' % id_, _id=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag, isWreck=isWreck)
        if wnd and id_ == util.GetActiveShip():
            wnd.scope = 'station_inflight'



    def CloseContainer(self, id_):
        wnd = uicls.Window.GetIfOpen(windowID='loot_%s' % id_)
        if wnd is not None and not wnd.destroyed:
            wnd.Close()



    def OpenSpecialCargoBay(self, id_, name, locationFlag, nameLabel = 'specialBay'):
        wnd = form.SpecialCargoBay.Open(windowID=nameLabel + '%s_%s' % (id_, locationFlag), _id=id_, displayName=name, locationFlag=locationFlag)
        if wnd and id_ == util.GetActiveShip():
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
                if eve.Message('CantSurrenderCEONotAtStationPageInstead', {'name': e.args[1]['charID']}, uiconst.YESNO) == uiconst.ID_YES:
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




