import form
import uix
import uiutil
import listentry
import xtriui
import uthread
import util
import blue
import uicls
import uiconst
from fleetcommon import *
GETFLEETS_THROTTLETIME = 2000
SIZE_FULLUI = (390, 250)
COMBO_SIZES = [110, 90, 86]

class FleetFinderWindow(uicls.Container):
    __guid__ = 'form.FleetFinderWindow'
    __notifyevents__ = ['OnFleetFinderAdvertChanged']
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.inited = False
        self.fleets = {}
        self.isNoAdvert = False
        sm.RegisterNotify(self)
        self.SetupContainers()
        self.SetupStuff()
        self.inited = True
        self.LoadMyAdvert()



    def Load(self, args):
        if not self.inited:
            return 
        if args == 'myadvert':
            self.LoadMyAdvert()



    def Height(self):
        return self.height or self.absoluteBottom - self.absoluteTop



    def Width(self):
        return self.width or self.absoluteRight - self.absoluteLeft



    def _OnResize(self, *args):
        if self.sr.Get('scopeCombo'):
            if self.Width() < SIZE_FULLUI[0]:
                d = SIZE_FULLUI[0] - self.Width()
                self.sr.scopeCombo.width = COMBO_SIZES[0] - d / 3
                l = self.sr.scopeCombo.width + 3
                self.sr.rangeCombo.width = COMBO_SIZES[1] - d / 3
                self.sr.rangeCombo.left = l
                l += self.sr.rangeCombo.width + 2
                self.sr.standingCombo.left = l
                self.sr.standingCombo.width = COMBO_SIZES[2] - d / 3
            else:
                self.sr.scopeCombo.width = COMBO_SIZES[0]
                l = self.sr.scopeCombo.width + 3
                self.sr.rangeCombo.width = COMBO_SIZES[1]
                self.sr.rangeCombo.left = l
                l += self.sr.rangeCombo.width + 2
                self.sr.standingCombo.left = l
                self.sr.standingCombo.width = COMBO_SIZES[2]
        if self.sr.Get('infoCont'):
            if self.Height() < SIZE_FULLUI[1]:
                self.sr.infoCont.height = 155 - (SIZE_FULLUI[1] - self.Height())
            else:
                self.sr.infoCont.height = 155
        if self.sr.Get('myAdvertText'):
            if self.Height() < 180:
                self.sr.myAdvertText.state = uiconst.UI_HIDDEN
                if self.sr.myAdvertDesc.state != uiconst.UI_HIDDEN:
                    setattr(self, 'oldMyAdvertDescState', self.sr.myAdvertDesc.state)
                self.sr.myAdvertDesc.state = uiconst.UI_HIDDEN
            else:
                self.sr.myAdvertText.state = uiconst.UI_NORMAL
                if self.sr.myAdvertDesc.state != uiconst.UI_HIDDEN:
                    setattr(self, 'oldMyAdvertDescState', self.sr.myAdvertDesc.state)
                if self.isNoAdvert:
                    setattr(self, 'oldMyAdvertDescState', uiconst.UI_HIDDEN)
                self.sr.myAdvertDesc.state = getattr(self, 'oldMyAdvertDescState', uiconst.UI_HIDDEN)



    def SetupContainers(self):
        findFleetsParent = uicls.Container(name='findfleets', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        myAdvertParent = uicls.Container(name='myadvert', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.myAdvertButtons = uicls.Container(name='myAdvertButtons', parent=myAdvertParent, align=uiconst.TOBOTTOM, height=35)
        self.sr.tabs = uicls.TabGroup(name='fleetfindertabs', parent=self, idx=0)
        tabs = [[mls.UI_FLEET_FINDFLEETS,
          findFleetsParent,
          self,
          'findfleets'], [mls.UI_FLEET_MYADVERT,
          myAdvertParent,
          self,
          'myadvert']]
        self.sr.tabs.Startup(tabs, 'fleetfindertabs', 0)
        uthread.new(self.sr.tabs.ShowPanelByName, mls.UI_FLEET_FINDFLEETS)
        uicls.Container(name='push', parent=findFleetsParent, width=const.defaultPadding, align=uiconst.TOLEFT)
        uicls.Container(name='push', parent=findFleetsParent, width=const.defaultPadding, align=uiconst.TORIGHT)
        self.sr.filterCont = uicls.Container(name='filterCont', parent=findFleetsParent, align=uiconst.TOTOP, height=35)
        self.sr.infoCont = uicls.Container(name='infoCont', parent=findFleetsParent, align=uiconst.TOBOTTOM, height=155, state=uiconst.UI_HIDDEN)
        uicls.Container(name='push', parent=findFleetsParent, height=const.defaultPadding, align=uiconst.TOBOTTOM)
        self.sr.topInfoCont = uicls.Container(name='topInfoCont', parent=self.sr.infoCont, align=uiconst.TOTOP, height=20)
        self.sr.descrCont = uicls.Container(name='descrCont', parent=self.sr.infoCont, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.scrollCont = uicls.Container(name='scrollCont', parent=findFleetsParent, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        uicls.Container(name='push', parent=myAdvertParent, width=const.defaultPadding, align=uiconst.TOLEFT)
        uicls.Container(name='push', parent=myAdvertParent, width=const.defaultPadding, align=uiconst.TORIGHT)
        self.sr.myAdvertCont = uicls.Container(name='myAdvertCont', parent=myAdvertParent, align=uiconst.TOALL, pos=(10, 0, 10, 0))



    def SetupStuff(self):
        options = [(mls.UI_FLEET_AVAILABLEFLEETS, INVITE_ALL), (mls.UI_FLEET_CORPFLEETS, INVITE_CORP)]
        selected = settings.user.ui.Get('fleetfinder_scopeFilter', None)
        if session.allianceid is not None:
            options.append((mls.UI_FLEET_ALLIANCEFLEETS, INVITE_ALLIANCE))
        elif selected == INVITE_ALLIANCE:
            selected = None
        if session.warfactionid is not None:
            options.append((mls.UI_FLEET_MILITIAFLEETS, INVITE_MILITIA))
        elif selected == INVITE_MILITIA:
            selected = None
        options.append((mls.UI_FLEET_STANDINGONLY, INVITE_PUBLIC))
        l = 1
        combo = self.sr.scopeCombo = uicls.Combo(label=mls.UI_FLEET_SCOPE, parent=self.sr.filterCont, options=options, name='fleetfinder_scopeFilter', select=selected, pos=(l,
         14,
         0,
         0), width=COMBO_SIZES[0])
        self.sr.scopeCombo.OnChange = self.OnComboChange
        l += combo.width + 3
        selected = settings.user.ui.Get('fleetfinder_rangeFilter', None)
        options = [(mls.UI_GENERIC_ANY, None),
         (mls.UI_FLEET_NJUMPS % {'n': 5}, 5),
         (mls.UI_FLEET_NJUMPS % {'n': 10}, 10),
         (mls.UI_FLEET_REGION, -1)]
        combo = self.sr.rangeCombo = uicls.Combo(label=mls.UI_FLEET_RANGE, parent=self.sr.filterCont, options=options, name='fleetfinder_rangeFilter', select=selected, pos=(l,
         14,
         0,
         0), width=COMBO_SIZES[1])
        self.sr.rangeCombo.OnChange = self.OnComboChange
        l += combo.width + 3
        selected = settings.user.ui.Get('fleetfinder_standingFilter', None)
        options = [(mls.UI_GENERIC_ANY, None), (mls.UI_CONTACTS_GOODSTANDING, const.contactGoodStanding), (mls.UI_CONTACTS_HIGHSTANDING, const.contactHighStanding)]
        combo = self.sr.standingCombo = uicls.Combo(label=mls.UI_FLEET_STANDING, parent=self.sr.filterCont, options=options, name='fleetfinder_standingFilter', select=selected, pos=(l,
         14,
         0,
         0), width=COMBO_SIZES[2])
        self.sr.standingCombo.OnChange = self.OnComboChange
        l += combo.width + 3
        self.sr.getFleetsBtn = btn = uicls.Button(parent=self.sr.filterCont, label=mls.UI_FLEET_GETFLEETS, pos=(0, 14, 0, 0), func=self.GetFleetsClick, align=uiconst.TOPRIGHT)
        self.sr.scroll = uicls.Scroll(parent=self.sr.scrollCont)
        self.sr.scroll.sr.id = 'fleetfinderScroll'
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.Load(contentList=[], headers=[], scrolltotop=0, noContentHint=mls.UI_FLEET_FLEETFINDERSCROLLHINT)
        self.sr.caption = uicls.CaptionLabel(text='', parent=self.sr.topInfoCont, align=uiconst.RELATIVE, fontsize=13, left=4, top=2, state=uiconst.UI_NORMAL)
        self.sr.detailsText = uicls.Edit(parent=self.sr.descrCont, padTop=2, state=uiconst.UI_NORMAL, readonly=1, hideBackground=1)
        uicls.Frame(parent=self.sr.detailsText, color=(0.4, 0.4, 0.4, 0.7))
        self.sr.detailsText.AllowResizeUpdates(1)
        tabs = [110, 540]
        self.sr.infoText = uicls.Label(text='', parent=self.sr.descrCont, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL)
        self.sr.joinBtn = btn = uicls.Button(parent=self.sr.topInfoCont, label=mls.UI_FLEET_JOINFLEET, pos=(0, 1, 0, 0), func=self.JoinFleet, align=uiconst.CENTERRIGHT)
        self.sr.joinRequestBtn = btn = uicls.Button(parent=self.sr.topInfoCont, label=mls.UI_FLEET_REQUESTJOINFLEET, pos=(0, 1, 0, 0), func=self.JoinFleet, align=uiconst.CENTERRIGHT)
        self.sr.myAdvertMainCont = uicls.Container(name='myAdvertMainCont', parent=self.sr.myAdvertCont, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.myAdvertButtons = [(mls.UI_FLEET_EDITREGISTRATION,
          sm.GetService('fleet').OpenRegisterFleetWindow,
          (),
          84), (mls.UI_FLEET_UNREGISTER,
          sm.GetService('fleet').UnregisterFleet,
          (),
          84)]
        self.sr.myAdvertButtonWnd = uicls.ButtonGroup(btns=self.myAdvertButtons, parent=self.sr.myAdvertButtons, unisize=1)
        self.sr.myAdvertCaption = uicls.CaptionLabel(text='', parent=self.sr.myAdvertCont, align=uiconst.TOTOP, fontsize=16, autowidth=0, left=0, top=7, state=uiconst.UI_DISABLED)
        self.sr.myAdvertDescCont = uicls.Container(name='myAdvertDescCont', parent=self.sr.myAdvertCont, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.myAdvertText = uicls.Label(text='', parent=self.sr.myAdvertCont, top=const.defaultPadding, tabs=tabs, autowidth=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.sr.myAdvertDesc = uicls.Edit(parent=self.sr.myAdvertDescCont, padTop=2, state=uiconst.UI_NORMAL, readonly=1)
        self.sr.myAdvertDesc.AllowResizeUpdates(1)
        self.myAdvertButtons_Register = [(mls.UI_FLEET_REGISTERFLEET,
          sm.GetService('fleet').OpenRegisterFleetWindow,
          (),
          84)]
        self.sr.myAdvertButtonWnd_Register = uicls.ButtonGroup(btns=self.myAdvertButtons_Register, parent=self.sr.myAdvertButtons, unisize=1)
        self.sr.myAdvertButtonWnd_Register.state = uiconst.UI_HIDDEN
        if self.sr.tabs.GetSelectedArgs() == 'findfleets':
            self.GetFleetsClick()



    def LoadMyAdvert(self):
        self.sr.myAdvertText.text = ''
        self.sr.detailsText.LoadHTML('')
        self.sr.myAdvertButtonWnd.state = uiconst.UI_HIDDEN
        self.sr.myAdvertButtonWnd_Register.state = uiconst.UI_HIDDEN
        self.sr.myAdvertMainCont.left = 0
        self.sr.myAdvertCaption.left = 4
        if session.fleetid is None:
            caption = mls.UI_FLEET_NOTINAFLEET
            self.sr.myAdvertCaption.text = caption
            self.sr.myAdvertText.text = mls.UI_FLEET_NOTINAFLEET_DESC
            self.sr.myAdvertDesc.state = uiconst.UI_HIDDEN
            self.isNoAdvert = True
            self.sr.myAdvertCont.left = 10
            self.sr.myAdvertCaption.left = 0
            return 
        fleet = sm.GetService('fleet').GetMyFleetFinderAdvert()
        if fleet is None:
            caption = mls.UI_FLEET_NOADVERT
            self.sr.myAdvertCaption.text = caption
            self.sr.myAdvertText.text = mls.UI_FLEET_NOADVERT_DESC
            self.sr.myAdvertDesc.state = uiconst.UI_HIDDEN
            self.sr.myAdvertButtonWnd_Register.state = uiconst.UI_NORMAL
            self.isNoAdvert = True
            self.sr.myAdvertCont.left = 10
            self.sr.myAdvertCaption.left = 0
            if self.sr.dragIcon:
                self.sr.dragIcon.Close()
            return 
        self.isNoAdvert = False
        self.sr.myAdvertButtonWnd.state = uiconst.UI_NORMAL
        caption = '%s' % (fleet.fleetName or mls.UI_GENERIC_UNNAMED)
        self.sr.myAdvertCaption.text = caption
        self.sr.dragIcon = dragIcon = xtriui.AdvertDraggableIcon(name='theicon', align=uiconst.TOPLEFT, parent=self.sr.myAdvertCont, height=64, width=64, top=const.defaultPadding, left=const.defaultPadding, state=uiconst.UI_NORMAL, idx=0)
        dragIcon.Startup(fleet)
        dragIcon.hint = mls.UI_FLEET_DRAGTOSHAREADVERT
        dragIcon.state = uiconst.UI_NORMAL
        text = self.GetFleetDetailsEntry(fleet)
        h = 0
        if fleet.joinNeedsApproval:
            text += '<t><b>%s</b><t>' % mls.UI_FLEET_NEEDSAPPROVAL
            h += 10
        self.sr.myAdvertText.text = text
        h += self.sr.myAdvertText.top + self.sr.myAdvertText.height - 5
        desc = fleet.description
        self.sr.myAdvertDesc.top = h
        self.sr.myAdvertDesc.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][(desc == '')]
        self.sr.myAdvertDesc.LoadHTML('<html><body>%s</body></html>' % desc)
        self._OnResize()



    def SetInfoCont(self, entry):
        selected = util.GetAttrs(entry.sr.node, 'selected')
        if not selected:
            self.ClearInfoCont()
            return 
        fleet = entry.sr.node.fleet
        self.sr.infoCont.isOpen = True
        if self.Height() >= SIZE_FULLUI[1]:
            self.sr.infoCont.state = uiconst.UI_PICKCHILDREN
        caption = '%s' % (fleet.fleetName or mls.UI_GENERIC_UNNAMED)
        self.sr.caption.text = caption
        text = self.GetFleetDetailsEntry(fleet)
        self.sr.infoText.text = text
        self.sr.detailsText.top = self.sr.infoText.height - 5
        desc = fleet.description
        self.sr.detailsText.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][(desc == '')]
        self.sr.detailsText.LoadHTML('<html><body>%s</body></html>' % desc)
        self.sr.joinBtn.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][fleet.joinNeedsApproval]
        self.sr.joinRequestBtn.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][(not fleet.joinNeedsApproval)]



    def GetFleetDetailsEntry(self, fleet):

        def AddBasicInfoRow(key, val):
            return '<b>%(key)s</b><t>%(val)s<br>' % {'key': key,
             'val': val}


        text = ''
        bossName = '<url:showinfo:1376//%s>%s</url>' % (fleet.leader.charID, cfg.eveowners.Get(fleet.leader.charID).name)
        if fleet.solarSystemID:
            loc = mls.UI_FLEET_FLEETLOCATIONHINT % {'name': cfg.evelocations.Get(fleet.solarSystemID).name,
             'jumps': fleet.numJumps}
            bossName += ' - <url:showinfo:5//%s>%s</url> (<url:showrouteto:%s>%s</url>)' % (fleet.solarSystemID,
             cfg.evelocations.Get(fleet.solarSystemID).name,
             fleet.solarSystemID,
             mls.UI_FLEET_JUMPS % {'num': fleet.numJumps})
        text += AddBasicInfoRow(mls.UI_FLEET_FLEETBOSS, bossName)
        text += AddBasicInfoRow(mls.UI_FLEET_FLEETAGE, util.FmtDate(blue.os.GetTime() - fleet.dateCreated, 'ss'))
        hint = ''
        if fleet.numMembers:
            text += AddBasicInfoRow(mls.UI_FLEET_NUMMEMBERS, fleet.numMembers)
        scopeLines = []
        if IsOpenToCorp(fleet):
            scopeLines.append('<b>%s</b> (<url:showinfo:%s//%s>%s</url>)' % (mls.UI_FLEET_CORP,
             const.typeCorporation,
             fleet.leader.corpID,
             cfg.eveowners.Get(fleet.leader.corpID).name))
        if IsOpenToAlliance(fleet):
            scopeLines.append('<b>%s</b> (<url:showinfo:%s//%s>%s</url>)' % (mls.UI_FLEET_ALLIANCE,
             const.typeAlliance,
             fleet.leader.allianceID,
             cfg.eveowners.Get(fleet.leader.allianceID).name))
        if IsOpenToMilitia(fleet):
            scopeLines.append('<b>%s</b> (<url:showinfo:%s//%s>%s</url>)' % (mls.UI_FLEET_MILITIA,
             const.typeFaction,
             fleet.leader.warFactionID,
             cfg.eveowners.Get(fleet.leader.warFactionID).name))
        if fleet.local_minStanding is not None or fleet.local_minSecurity is not None:
            lineText = ''
            if fleet.local_minStanding is not None:
                if fleet.local_minStanding == const.contactGoodStanding:
                    minStanding = mls.UI_CONTACTS_GOODSTANDING
                else:
                    minStanding = mls.UI_CONTACTS_HIGHSTANDING
                lineText += '%s: %s' % (mls.UI_FLEET_MINSTANDING, minStanding)
                if fleet.local_minSecurity is not None:
                    lineText += ' - '
            if fleet.local_minSecurity is not None:
                lineText += '%s: %.1f' % (mls.UI_FLEET_MINSECURITY, fleet.local_minSecurity)
            scopeLines.append(lineText)
        if IsOpenToPublic(fleet):
            scopeLines.append('<b>%s</b>' % mls.UI_FLEET_STANDINGONLY)
            if fleet.public_minStanding == const.contactGoodStanding:
                minStanding = mls.UI_CONTACTS_GOODSTANDING
            else:
                minStanding = mls.UI_CONTACTS_HIGHSTANDING
            lineText = '%s: %s' % (mls.UI_FLEET_MINSTANDING, minStanding)
            if fleet.public_minSecurity is not None:
                lineText += ' - %s: %.1f' % (mls.UI_FLEET_MINSECURITY, fleet.public_minSecurity)
            scopeLines.append(lineText)
        text += AddBasicInfoRow(mls.UI_FLEET_SCOPE, '<br><t>'.join(scopeLines))
        return text



    def ClearInfoCont(self):
        self.sr.infoCont.state = uiconst.UI_HIDDEN
        self.sr.infoCont.isOpen = False
        self.sr.detailsText.LoadHTML('')



    def OnComboChange(self, combo, header, value, *args):
        settings.user.ui.Set(combo.name, value)



    def CreateFleet(self, *args):
        if session.fleetid is not None:
            raise UserError('FleetYouAreAlreadyInFleet')
        sm.GetService('menu').InviteToFleet(session.charid)



    def EditDetail(self, *args):
        sm.GetService('fleet').OpenRegisterFleetWindow()



    def Register(self, *args):
        if util.IsNPC(session.corpid) and sm.GetService('facwar').GetCorporationWarFactionID(session.corpid) is None:
            raise UserError('CantUseFleetfinder')
        if session.fleetid is None:
            return 
        if sm.GetService('fleet').IsBoss():
            if sm.GetService('fleet').options.isRegistered:
                self.EditDetail()
            else:
                wnd = sm.GetService('window').GetWindow('RegisterFleetWindow')
                if wnd:
                    wnd.CloseX()
                sm.GetService('window').GetWindow('RegisterFleetWindow', create=1, decoClass=form.RegisterFleetWindow)



    def Unregister(self, *args):
        sm.GetService('fleet').UnregisterFleet()



    def LeaveFleet(self, *args):
        sm.GetService('fleet').LeaveFleet()



    def GetFleetsClick(self, *args):
        try:
            self.sr.getFleetsBtn.state = uiconst.UI_DISABLED
            self.sr.getFleetsBtn.SetLabel('<color=gray>' + self.sr.getFleetsBtn.text + '</color>')
            self.Refresh()

        finally:
            uthread.new(self.EnableButtonTimer)




    def EnableButtonTimer(self):
        blue.pyos.synchro.Sleep(GETFLEETS_THROTTLETIME)
        try:
            self.sr.getFleetsBtn.state = uiconst.UI_NORMAL
            self.sr.getFleetsBtn.SetLabel(mls.UI_FLEET_GETFLEETS)
        except:
            pass



    def Refresh(self):
        filterScope = self.sr.scopeCombo.GetValue()
        filterRange = self.sr.rangeCombo.GetValue()
        filterStanding = self.sr.standingCombo.GetValue()
        self.GetFleets()
        self.DrawScrollList(filterScope, filterRange, filterStanding)
        self.ClearInfoCont()



    def JoinFleet(self, *args):
        if session.fleetid:
            raise UserError('FleetYouAreAlreadyInFleet')
        fleetID = None
        selected = self.sr.scroll.GetSelected()
        if len(selected) > 0:
            selected = selected[0]
            fleetID = getattr(selected, 'fleetID', None)
            if fleetID is None:
                return 
        if fleetID:
            sm.GetService('fleet').ApplyToJoinFleet(fleetID)



    def DrawScrollList(self, filterScope = None, filterRange = None, filterStanding = None):
        fleets = self.fleets
        self.PrimeStuff(fleets)
        scrolllist = []
        for fleet in fleets.itervalues():
            if filterScope is not None:
                if fleet.inviteScope & filterScope == 0:
                    continue
                elif filterScope == INVITE_CORP and fleet.leader.corpID != session.corpid:
                    continue
                elif filterScope == INVITE_ALLIANCE and fleet.leader.allianceID != session.allianceid:
                    continue
                elif filterScope == INVITE_MILITIA and fleet.leader.warFactionID != session.warfactionid:
                    continue
            if filterRange is not None:
                if not hasattr(fleet, 'numJumps'):
                    continue
                if filterRange > 0 and fleet.numJumps > filterRange:
                    continue
                if filterRange == -1 and fleet.regionID != session.regionid:
                    continue
            if filterStanding is not None:
                if filterStanding != fleet.standing:
                    continue
            bossName = cfg.eveowners.Get(fleet.leader.charID).name
            systemString = ' (%s)' % cfg.evelocations.Get(fleet.solarSystemID).locationName
            numMembers = fleet.numMembers
            if fleet.hideInfo:
                numMembers = '<color=0xff888888>%s</color>' % mls.UI_GENERIC_HIDDEN.lower()
                systemString = ''
            label = '%s%s<t>%s<t>%s<t>%s' % (bossName,
             systemString,
             fleet.fleetName,
             numMembers,
             fleet.description)
            data = {'label': label,
             'fleetID': fleet.fleetID,
             'charID': fleet.leader.charID,
             'fleet': fleet,
             'OnClick': self.SetInfoCont,
             'corpID': fleet.leader.corpID,
             'allianceID': fleet.leader.allianceID,
             'warFactionID': fleet.leader.warFactionID,
             'securityStatus': fleet.leader.securityStatus}
            scrolllist.append(listentry.Get('FleetFinderEntry', data))

        headers = [mls.UI_FLEET_FLEETLEADER,
         mls.UI_FLEET_NAMEOFFLEET,
         mls.UI_FACWAR_PILOTS,
         mls.UI_GENERIC_DESCRIPTION]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers, scrolltotop=0, noContentHint=mls.UI_RMR_TEXT10)



    def PrimeStuff(self, fleets):
        pathfinderSvc = sm.GetService('pathfinder')
        mapSvc = sm.GetService('map')
        standingSvc = sm.GetService('standing')
        namesForPriming = set()
        locationsForPriming = set()
        for fleet in fleets.itervalues():
            for id in [fleet.leader.charID, fleet.leader.corpID, fleet.leader.allianceID]:
                if id is not None:
                    namesForPriming.add(id)

            fleet.regionID = None
            fleet.standing = standingSvc.GetStanding(session.charid, fleet.leader.charID)
            if fleet.Get('solarSystemID', 0):
                locationsForPriming.add(fleet.solarSystemID)
                numJumps = int(pathfinderSvc.GetJumpCountFromCurrent(fleet.solarSystemID))
                fleet.numJumps = numJumps
                constellationID = mapSvc.GetParent(fleet.solarSystemID)
                fleet.regionID = mapSvc.GetParent(constellationID)
                fleet.standing = standingSvc.GetStanding(session.charid, fleet.leader.charID)

        if len(namesForPriming) > 0:
            cfg.eveowners.Prime(namesForPriming)
        if len(locationsForPriming) > 0:
            cfg.evelocations.Prime(locationsForPriming)



    def GetMyFleet(self, force = 0):
        if session.fleetid is None or not sm.GetService('fleet').options.isRegistered:
            return 
        myFleet = self.fleets.get(session.fleetid, None)
        if myFleet is None or force:
            self.GetFleets()
            myFleet = self.fleets.get(session.fleetid, None)
        return myFleet



    def GetFleets(self):
        self.fleets = sm.GetService('fleet').GetFleetsForChar()
        return self.fleets



    def OnFleetFinderAdvertChanged(self):
        if self.sr.tabs.GetSelectedArgs() == 'myadvert':
            self.Load('myadvert')




class FleetFinderEntry(listentry.Generic):
    __guid__ = 'listentry.FleetFinderEntry'

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)
        self.picture = uicls.Container(name='picture', parent=self, pos=(const.defaultPadding,
         2,
         32,
         32), state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT)
        self.portrait = uicls.Icon(name='portrait', parent=self.picture, size=32, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)



    def Load(self, node):
        listentry.Generic.Load(self, node)
        uicls.Frame(parent=self.picture)
        sm.GetService('photo').GetPortrait(node.charID, 32, self.portrait)
        uix.SetStateFlag(self.picture, node, top=23, left=0)
        self.portrait.OnClick = (sm.GetService('info').ShowInfo, cfg.eveowners.Get(node.charID).typeID, node.charID)
        self.sr.label.left = 40
        self.sr.label.text = node.label



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 37
        return node.height



    def GetMenu(self, *args):
        menuSvc = sm.GetService('menu')
        m = []
        fleet = self.sr.node.fleet
        fleetSvc = sm.GetService('fleet')
        if self.sr.node.fleetID != session.fleetid:
            m += [(mls.UI_FLEET_JOINFLEET, fleetSvc.ApplyToJoinFleet, [fleet.fleetID])]
            m += [None]
        elif fleetSvc.IsBoss():
            m += [(mls.UI_FLEET_EDITREGISTRATION, fleetSvc.OpenRegisterFleetWindow)]
            if sm.GetService('fleet').GetMyFleetFinderAdvert() is not None:
                m += [(mls.UI_FLEET_UNREGISTER, fleetSvc.UnregisterFleet)]
            m += [None]
        fleetbossMenu = menuSvc.CharacterMenu(fleet.leader.charID)
        fleetbossMenu.insert(0, (mls.UI_CMD_SHOWINFO, sm.StartService('info').ShowInfo, (const.typeCharacterGallente, fleet.leader.charID)))
        m += [(mls.UI_FLEET_BOSS, fleetbossMenu)]
        if fleet.solarSystemID:
            m += [(mls.UI_FLEET_BOSSLOCATION, menuSvc.CelestialMenu(itemID=fleet.solarSystemID))]
        return m



    def GetHint(self):
        fleet = self.sr.node.fleet
        hint = ''
        hint += '<b>%s:</b>%s<br>' % (mls.UI_FLEET_NAME, fleet.fleetName)
        hint += '<b>%s:</b>%s<br>' % (mls.UI_FLEET_FLEETBOSS, cfg.eveowners.Get(fleet.leader.charID).name)
        if fleet.standing is not None:
            hint += '<b>%s:</b>%.2f<br>' % (mls.UI_GENERIC_STANDING, fleet.standing)
        if fleet.solarSystemID:
            loc = mls.UI_FLEET_FLEETLOCATIONHINT % {'name': cfg.evelocations.Get(fleet.solarSystemID).name,
             'jumps': fleet.numJumps}
            hint += '<b>%s:</b>%s<br>' % (mls.UI_FLEET_BOSSLOCATION, loc)
        hint += '<b>%s:</b>%s<br>' % (mls.UI_FLEET_FLEETAGE, util.FmtDate(blue.os.GetTime() - fleet.dateCreated, 'ss'))
        if fleet.numMembers:
            hint += '<b>%s:</b>%s<br>' % (mls.UI_FLEET_NUMMEMBERS, fleet.numMembers)
        hint += '<b>%s:</b><br>' % mls.UI_FLEET_SCOPE
        if IsOpenToCorp(fleet):
            hint += '%s<br>' % mls.CORPORATION
        if IsOpenToAlliance(fleet):
            hint += '%s<br>' % mls.ALLIANCE
        if IsOpenToMilitia(fleet):
            hint += '%s<br>' % mls.UI_FLEET_MILITIA
        if fleet.local_minStanding is not None:
            hint += '<i>%s:</i>%.1f<br>' % (mls.UI_FLEET_MINSTANDING, fleet.local_minStanding)
        if fleet.local_minSecurity is not None:
            hint += '<i>%s:</i>%.1f<br>' % (mls.UI_FLEET_MINSECURITY, fleet.local_minSecurity)
        if IsOpenToPublic(fleet):
            hint += '%s<br>' % mls.UI_FLEET_STANDINGONLY
        if fleet.public_minStanding is not None:
            hint += '<i>%s:</i>%.1f<br>' % (mls.UI_FLEET_MINSTANDING, fleet.public_minStanding)
        if fleet.public_minSecurity is not None:
            hint += '<i>%s:</i>%.1f<br>' % (mls.UI_FLEET_MINSECURITY, fleet.public_minSecurity)
        if fleet.joinNeedsApproval:
            hint += '<b>%s</b><br>' % mls.UI_FLEET_JOINNEEDSAPPROVAL
        if fleet.description:
            hint += '<b>%s:</b><br>%s<br>' % (mls.UI_FLEET_FLEETDESCRIPTION, fleet.description)
        return hint



    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes




class AdvertDraggableIcon(uicls.Container):
    __guid__ = 'xtriui.AdvertDraggableIcon'

    def Startup(self, fleet):
        self.fleet = fleet



    def GetDragData(self, *args):
        entry = util.KeyVal()
        entry.fleet = self.fleet
        entry.__guid__ = 'listentry.FleetFinderEntry'
        return [entry]




