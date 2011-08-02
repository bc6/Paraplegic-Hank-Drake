import uix
import uicls
import uiconst
import uiutil
import xtriui
import util
import uthread
import blue
import sys
import state
import trinity

class User(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.User'
    __params__ = ['charID']
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnPortraitCreated',
     'OnContactNoLongerContact',
     'OnStateSetupChance',
     'ProcessSessionChange',
     'OnFleetJoin',
     'OnFleetLeave',
     'ProcessOnUIAllianceRelationshipChanged',
     'OnContactChange',
     'OnBlockContacts',
     'OnUnblockContacts']

    def init(self):
        self.charid = None
        self.selected = 0
        self.big = 0
        self.id = None
        self.groupID = None
        self.picloaded = 0
        self.fleetCandidate = 0
        self.label = None
        self.slimuser = False



    def Startup(self, *args):
        self.sr.picture = uicls.Container(parent=self, pos=(0, 0, 64, 64), name='picture', state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)
        self.sr.picture.width = 32
        self.sr.picture.height = 32
        self.sr.picture.left = 2
        self.sr.picture.top = 2
        self.sr.extraIconCont = uicls.Container(name='extraIconCont', parent=self, idx=0, pos=(0, 0, 16, 16), align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN)
        self.sr.namelabel = uicls.Label(text='', parent=self, state=uiconst.UI_DISABLED, idx=0)
        self.sr.contactLabels = uicls.Label(text='', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.BOTTOMLEFT)
        self.sr.contactLabels.top = 2
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.125), state=uiconst.UI_HIDDEN)
        self.sr.voiceIcon = None
        uicls.Line(parent=self, align=uiconst.TOBOTTOM, idx=0)
        self.sr.standingLabel = uicls.Label(text='', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.TOPRIGHT)
        self.sr.blockedicon = uicls.Icon(icon='ui_77_32_12', parent=self, pos=(16, 18, 13, 13), state=uiconst.UI_HIDDEN, ignoreSize=True, align=uiconst.TOPRIGHT)
        self.sr.corpApplicationLabel = uicls.Label(text='', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.corpApplicationLabel.left = 16
        sm.RegisterNotify(self)



    def PreLoad(node):
        data = node
        charinfo = data.Get('info', None) or cfg.eveowners.Get(data.charID)
        data.info = charinfo
        if data.GetLabel:
            data.label = data.GetLabel(data)
        elif not data.Get('label', None):
            label = charinfo.name
            agentInfo = sm.GetService('agents').GetAgentByID(data.charID)
            if agentInfo:
                if data.charID in sm.GetService('agents').GetTutorialAgentIDs():
                    label += ', %s' % mls.CHAR_TUTORIAL_AGENT
                elif agentInfo.agentTypeID == const.agentTypeEpicArcAgent:
                    label += ', %s' % mls.CHAR_EPICARC_AGENT
                elif agentInfo.agentTypeID == const.agentTypeAura:
                    label = 'Aura'
                elif agentInfo.agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent, const.agentTypeEventMissionAgent):
                    label += ', %s: %s' % (mls.UI_GENERIC_LEVEL, uiutil.GetLevel(agentInfo.level))
                else:
                    t = {const.agentTypeGenericStorylineMissionAgent: mls.UI_SHARED_STORYLINE,
                     const.agentTypeStorylineMissionAgent: mls.UI_SHARED_STORYLINE,
                     const.agentTypeEventMissionAgent: mls.UI_SHARED_EVENT}.get(agentInfo.agentTypeID, None)
                    if t:
                        label += ', %s' % t
                if agentInfo.stationID and eve.session.stationid != agentInfo.stationID:
                    label += '<br>%s %s' % (mls.UI_SHARED_LOCATEDAT, cfg.evelocations.Get(agentInfo.stationID).name)
                if agentInfo.agentTypeID != const.agentTypeAura and (not data.Get('defaultDivisionID', None) or data.defaultDivisionID != agentInfo.divisionID):
                    label += '<br>%s: %s' % (mls.UI_GENERIC_DIVISION, sm.GetService('agents').GetDivisions()[agentInfo.divisionID].divisionName.replace('&', '&amp;'))
            elif data.bounty:
                label += '<br>%s: %s' % (mls.UI_GENERIC_BOUNTY, util.FmtISK(data.bounty.bounty))
            elif data.killTime:
                label += '<br>%s: %s' % (mls.UI_GENERIC_EXPIRES, util.FmtDate(data.killTime + 25920000000000L))
            data.label = label
        invtype = cfg.invtypes.Get(data.info.typeID)
        data.invtype = invtype
        data.IsCharacter = invtype.groupID == const.groupCharacter
        data.IsCorporation = invtype.groupID == const.groupCorporation
        data.IsFaction = invtype.groupID == const.groupFaction
        data.IsAlliance = invtype.groupID == const.groupAlliance
        if data.IsCorporation and not util.IsNPC(data.charID):
            logoData = cfg.corptickernames.Get(data.charID)



    def Load(self, node):
        self.sr.node = node
        data = node
        self.name = data.info.name
        self.sr.namelabel.text = data.label
        self.sr.namelabel.linespace = 11
        self.charid = self.id = data.itemID = data.charID
        self.picloaded = 0
        self.sr.parwnd = data.Get('dad', None)
        self.fleetCandidate = data.Get('fleetster', 1) and not data.info.IsNPC()
        self.confirmOnDblClick = data.Get('dblconfirm', 1)
        self.leaveDadAlone = data.Get('leavedad', 0)
        self.slimuser = data.Get('slimuser', False)
        self.data = {'Name': self.name,
         'charid': data.charID}
        self.inWatchlist = sm.GetService('addressbook').IsInWatchlist(data.charID)
        self.isContactList = data.Get('contactType', None)
        self.applicationDate = data.Get('applicationDate', None)
        self.contactLevel = None
        if self.isContactList:
            self.contactLevel = data.contactLevel
            self.sr.namelabel.top = 2
            self.SetLabelText()
        else:
            self.sr.namelabel.SetAlign(uiconst.CENTERLEFT)
        self.isCorpOrAllianceContact = data.contactType and data.contactType != 'contact'
        data.listvalue = [data.info.name, data.charID]
        level = self.sr.node.Get('sublevel', 0)
        self.sr.picture.left = 2 + max(0, 16 * level)
        self.LoadPortrait()
        if data.IsCharacter:
            uthread.new(self.SetRelationship, data)
            if self.sr.Get('onlinestatus', None):
                self.sr.onlinestatus.state = uiconst.UI_HIDDEN
            if data.charID != eve.session.charid:
                if not util.IsNPC(data.charID) and not self.isCorpOrAllianceContact and self.inWatchlist:
                    try:
                        self.SetOnline(sm.GetService('onlineStatus').GetOnlineStatus(data.charID, fetch=False))
                    except IndexError:
                        sys.exc_clear()
            else:
                uix.ClearStateFlag(self)
        elif self.sr.Get('onlinestatus', None):
            self.sr.onlinestatus.state = uiconst.UI_HIDDEN
        if data.charID != eve.session.charid:
            uthread.new(self.SetRelationship, data)
        self.sr.namelabel.left = 40
        self.sr.contactLabels.left = 40
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        if not self.isCorpOrAllianceContact:
            self.contactLevel = sm.GetService('addressbook').GetStandingsLevel(self.charid, 'contact')
            self.SetBlocked(1)
        else:
            self.SetBlocked(0)
        if self.isCorpOrAllianceContact:
            self.SetStandingText(self.contactLevel)
        if self.applicationDate:
            formattedDate = util.FmtDate(self.applicationDate, 'sn')
            self.sr.corpApplicationLabel.SetText(mls.UI_CORP_APPLIED + ' ' + formattedDate)
            self.sr.corpApplicationLabel.Show()
            data.Set('sort_' + mls.UI_GENERIC_DATE, self.applicationDate)
            data.Set('sort_' + mls.UI_GENERIC_NAME, data.info.name)
        else:
            self.sr.corpApplicationLabel.SetText('')
            self.sr.corpApplicationLabel.Hide()



    def GetValue(self):
        return [self.name, self.id]



    def OnMouseEnter(self, *args):
        if self is None or self.destroyed or self.parent is None or self.parent.destroyed:
            return 
        self.Select()



    def OnMouseExit(self, *args):
        if self is None or self.destroyed or self.parent is None or self.parent.destroyed:
            return 
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = max(37, uix.GetTextHeight(node.label, linespace=11, autoWidth=1))
        return node.height



    def OnContactLoggedOn(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != eve.session.charid and not util.IsNPC(charID):
            self.SetOnline(1)



    def OnContactLoggedOff(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != eve.session.charid and not util.IsNPC(charID):
            self.SetOnline(0)



    def OnContactNoLongerContact(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != eve.session.charid:
            self.SetOnline(None)



    def OnPortraitCreated(self, charID):
        if self.destroyed:
            return 
        if self.sr.node and charID == self.sr.node.charID and not self.picloaded:
            self.LoadPortrait(orderIfMissing=False)



    def OnContactChange(self, contactIDs, contactType = None):
        if self.destroyed:
            return 
        self.SetRelationship(self.sr.node)
        if self.charid in contactIDs:
            if sm.GetService('addressbook').IsInAddressBook(self.charid, contactType):
                if not self.isContactList:
                    self.isContactList = contactType
            else:
                self.isContactList = None
            self.inWatchlist = sm.GetService('addressbook').IsInWatchlist(self.charid)
            if not self.inWatchlist:
                if self.sr.Get('onlinestatus', None):
                    self.sr.onlinestatus.state = uiconst.UI_HIDDEN
            elif self.sr.Get('onlinestatus', None):
                self.sr.onlinestatus.state = uiconst.UI_DISABLED



    def OnBlockContacts(self, contactIDs):
        if not self or self.destroyed:
            return 
        if self.charid in contactIDs:
            self.SetBlocked(1)



    def OnUnblockContacts(self, contactIDs):
        if not self or self.destroyed:
            return 
        if self.charid in contactIDs:
            self.SetBlocked(0)



    def OnStateSetupChance(self, what):
        if self.destroyed:
            return 
        self.SetRelationship(self.sr.node)



    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.destroyed:
            return 
        self.SetRelationship(self.sr.node)



    def OnFleetJoin(self, charID, state = 'Active'):
        if self.destroyed:
            return 
        myID = util.GetAttrs(self, 'sr', 'node', 'charID')
        if myID is not None and charID == myID:
            uthread.new(self.SetRelationship, self.sr.node)



    def OnFleetLeave(self, charID):
        if self.destroyed:
            return 
        myID = util.GetAttrs(self, 'sr', 'node', 'charID')
        if myID is not None and charID == myID:
            uthread.new(self.SetRelationship, self.sr.node)



    def ProcessSessionChange(self, isRemote, session, change):
        if self.destroyed:
            return 
        if 'fleetid' in change and eve.session.solarsystemid:
            uthread.new(self.SetRelationship, self.sr.node)



    def SetOnline(self, online):
        if self.destroyed:
            return 
        if self.slimuser:
            return 
        if online is None or not self.inWatchlist or self.isCorpOrAllianceContact:
            if self.sr.Get('onlinestatus', None):
                self.sr.onlinestatus.state = uiconst.UI_HIDDEN
        elif not self.sr.Get('onlinestatus', None):
            col = xtriui.SquareDiode(parent=self, align=uiconst.TOPRIGHT, pos=(3, 3, 12, 12))
            self.sr.onlinestatus = col
        self.sr.onlinestatus.SetRGB(float(not online) * 0.75, float(online) * 0.75, 0.0)
        self.sr.onlinestatus.hint = [mls.UI_GENERIC_OFFLINE, mls.UI_GENERIC_ONLINE][online]
        self.sr.onlinestatus.state = uiconst.UI_NORMAL



    def SetBlocked(self, blocked):
        isBlocked = sm.GetService('addressbook').IsBlocked(self.charid)
        if blocked and isBlocked and not self.isCorpOrAllianceContact:
            self.sr.blockedicon.state = uiconst.UI_DISABLED
        else:
            self.sr.blockedicon.state = uiconst.UI_HIDDEN



    def SetLabelText(self):
        labelMask = sm.GetService('addressbook').GetLabelMask(self.charid)
        self.sr.node.labelMask = labelMask
        labeltext = sm.GetService('addressbook').GetLabelText(labelMask, self.isContactList)
        if not self or self.destroyed:
            return 
        self.sr.contactLabels.text = labeltext



    def SetStandingText(self, standing):
        self.sr.standingLabel.text = standing
        self.sr.standingLabel.left = 2
        self.sr.standingLabel.top = 2



    def SetRelationship(self, data, debugFlag = None):
        if self.destroyed:
            return 
        if self.slimuser:
            return 
        if not data:
            return 
        if data.Get('contactType', None):
            if self.contactLevel is None:
                return 
            if self.contactLevel > const.contactGoodStanding:
                flag = state.flagStandingHigh
            elif self.contactLevel <= const.contactGoodStanding and self.contactLevel > const.contactNeutralStanding:
                flag = state.flagStandingGood
            elif self.contactLevel == const.contactNeutralStanding:
                flag = state.flagStandingNeutral
            elif self.contactLevel >= const.contactBadStanding and self.contactLevel < const.contactNeutralStanding:
                flag = state.flagStandingBad
            elif self.contactLevel <= const.contactBadStanding:
                flag = state.flagStandingHorrible
            uix.SetStateFlagForFlag(self, flag)
        else:
            uix.SetStateFlag(self, data)



    def LoadPortrait(self, orderIfMissing = True):
        self.sr.picture.Flush()
        if self.sr.node is None:
            return 
        if uiutil.GetOwnerLogo(self.sr.picture, self.id, size=32, callback=True, orderIfMissing=orderIfMissing):
            self.picloaded = 1



    def RemoveFromListGroup(self, listGroupIDs, charIDs, listname):
        if self.destroyed:
            return 
        if listGroupIDs:
            for (listGroupID, charID,) in listGroupIDs:
                uicore.registry.RemoveFromListGroup(listGroupID, charID)

            sm.GetService('addressbook').RefreshWindow()
        if charIDs and listname:
            name = [mls.UI_SHARED_USERENTRYTEXT1, cfg.eveowners.Get(charIDs[0]).name][(len(charIDs) == 1)]
            if eve.Message('WarnDeleteFromAddressbook', {'name': name,
             'type': listname}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return 
            sm.GetService('addressbook').DeleteEntryMulti(charIDs, None)



    def GetMenu(self):
        if self.destroyed:
            return 
        m = []
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        if multi:
            return self._GetMultiMenu(selected)
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(self.id, self.sr.node.invtype.typeID)
        if self.sr.node.IsCharacter:
            doShowInfo = True
            if util.IsNPC(self.charid):
                agentInfo = sm.GetService('agents').GetAgentByID(self.charid)
                if agentInfo and agentInfo.agentTypeID == const.agentTypeAura:
                    doShowInfo = False
            if doShowInfo:
                m.insert(0, (mls.UI_CMD_SHOWINFO, self.ShowInfo))
            if self.sr.node.Get('GetMenu', None) is not None:
                m += self.sr.node.GetMenu(self.sr.node)
        listGroupID = self.sr.node.Get('listGroupID', None)
        if listGroupID is not None:
            group = uicore.registry.GetListGroup(listGroupID)
            if group:
                if listGroupID not in [('buddygroups', 'all'), ('buddygroups', 'allcorps'), ('agentgroups', 'all')]:
                    m.append(None)
                    m.append(('%s %s' % (mls.UI_SHARED_REMOVEFROM, group['label']), self.RemoveFromListGroup, ([(listGroupID, self.charid)], [], '')))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction([self.sr.node])
            m += cm
        if self.isContactList is not None:
            if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.isContactList):
                m.append(None)
                assignLabelMenu = sm.StartService('addressbook').GetAssignLabelMenu(selected, [self.charid], self.isContactList)
                if len(assignLabelMenu) > 0:
                    m.append((mls.UI_EVEMAIL_ASSIGNLABEL, assignLabelMenu))
                removeLabelMenu = sm.StartService('addressbook').GetRemoveLabelMenu(selected, [self.charid], self.isContactList)
                if len(removeLabelMenu) > 0:
                    m.append((mls.UI_EVEMAIL_REMOVELABEL, removeLabelMenu))
        return m



    def _GetMultiMenu(self, selected):
        m = []
        charIDs = []
        multiCharIDs = []
        listGroupIDs = {}
        listGroupID_charIDs = []
        onlyCharacters = True
        for entry in selected:
            listGroupID = entry.listGroupID
            if listGroupID:
                listGroupIDs[listGroupID] = 0
                listGroupID_charIDs.append((listGroupID, entry.charID))
            if entry.charID:
                charIDs.append((entry.charID, None))
                multiCharIDs.append(entry.charID)
                if not util.IsCharacter(entry.charID):
                    onlyCharacters = False

        if self.isContactList is None:
            if onlyCharacters:
                m += sm.GetService('menu').CharacterMenu(charIDs)
            if listGroupIDs:
                listname = ''
                delCharIDs = []
                rem = []
                for (listGroupID, charID,) in listGroupID_charIDs:
                    if listGroupID in [('buddygroups', 'all'), ('buddygroups', 'allcorps'), ('agentgroups', 'all')]:
                        if onlyCharacters:
                            return m
                        group = uicore.registry.GetListGroup(listGroupID)
                        listname = [mls.UI_GENERIC_AGENTLIST, mls.UI_GENERIC_BUDDYLIST][(listGroupID == ('buddygroups', 'all'))]
                        delCharIDs.append(charID)
                        rem.append((listGroupID, charID))

                for each in rem:
                    listGroupID_charIDs.remove(each)

                foldername = 'folders'
                if len(listGroupIDs) == 1:
                    group = uicore.registry.GetListGroup(listGroupIDs.keys()[0])
                    if group:
                        foldername = group['label']
                label = ''
                if delCharIDs and listname:
                    label = '%s (%s)' % (mls.UI_CMD_REMOVEFROMADDRESSBOOK, len(delCharIDs))
                    if listGroupID_charIDs:
                        label += ', '
                if listGroupID_charIDs:
                    label += '%s %s (%s)' % (mls.UI_SHARED_REMOVEFROM, foldername, len(listGroupID_charIDs))
                m.append((label, self.RemoveFromListGroup, (listGroupID_charIDs, delCharIDs, listname)))
        else:
            addressBookSvc = sm.GetService('addressbook')
            counter = len(selected)
            blocked = 0
            if self.isContactList == 'contact':
                editLabel = '%s (%s)' % (mls.UI_CONTACTS_EDITCONTACTS, counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'contact']))
                deleteLabel = '%s (%s)' % (mls.UI_CONTACTS_REMOVECONTACTS, counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'contact']))
                for charid in multiCharIDs:
                    if sm.GetService('addressbook').IsBlocked(charid):
                        blocked += 1

                if blocked == counter:
                    unblockLabel = '%s (%s)' % (mls.UI_CMD_UNBLOCK, blocked)
                    m.append((unblockLabel, addressBookSvc.UnblockOwner, [multiCharIDs]))
            elif self.isContactList == 'corpcontact':
                editLabel = '%s (%s)' % (mls.UI_CONTACTS_EDITCORPCONTACTS, counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'corpcontact']))
                deleteLabel = '%s (%s)' % (mls.UI_CONTACTS_REMOVECORPCONTACTS, counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'corpcontact']))
            elif self.isContactList == 'alliancecontact':
                editLabel = '%s (%s)' % (mls.UI_CONTACTS_EDITALLIANCECONTACTS, counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'alliancecontact']))
                deleteLabel = '%s (%s)' % (mls.UI_CONTACTS_REMOVEALLIANCECONTACTS, counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'alliancecontact']))
            m.append(None)
            assignLabelMenu = sm.StartService('addressbook').GetAssignLabelMenu(selected, multiCharIDs, self.isContactList)
            if len(assignLabelMenu) > 0:
                m.append((mls.UI_EVEMAIL_ASSIGNLABEL, assignLabelMenu))
            removeLabelMenu = sm.StartService('addressbook').GetRemoveLabelMenu(selected, multiCharIDs, self.isContactList)
            if len(removeLabelMenu) > 0:
                m.append((mls.UI_EVEMAIL_REMOVELABEL, removeLabelMenu))
            m.append(None)
            m.append((mls.UI_CMD_CAPTUREPORTRAIT, sm.StartService('photo').SavePortraits, [multiCharIDs]))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction(selected)
            m += cm
        return m



    def ShowInfo(self, *args):
        if self.destroyed:
            return 
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charid).typeID, self.charid)



    def OnClick(self, *args):
        if self.destroyed:
            return 
        eve.Message('ListEntryClick')
        self.sr.node.scroll.SelectNode(self.sr.node)
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)



    def OnDblClick(self, *args):
        if self.destroyed:
            return 
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
            return 
        if self.sr.parwnd and hasattr(self.sr.parwnd, 'Select') and self.confirmOnDblClick:
            self.sr.parwnd.Select(self)
            self.sr.parwnd.Confirm()
            return 
        if not self.leaveDadAlone and self.sr.parwnd and uicore.registry.GetModalWindow() == self.sr.parwnd:
            self.sr.parwnd.SetModalResult(uiconst.ID_OK)
            return 
        if util.IsNPC(self.charid):
            agentInfo = sm.GetService('agents').GetAgentByID(self.charid)
            if eve.session.stationid and agentInfo:
                sm.GetService('agents').InteractWith(self.charid)
                return 
            self.ShowInfo()
        else:
            onDblClick = settings.user.ui.Get('dblClickUser', 0)
            if onDblClick == 0:
                sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charid).typeID, self.charid)
            elif onDblClick == 1:
                sm.GetService('LSC').Invite(self.charid)



    def GetDragData(self, *args):
        if self and not self.destroyed and not self.slimuser:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        else:
            return []



    def Select(self):
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_DISABLED



    def Deselect(self):
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN




class OnOfflineUserEntry(uicls.SE_BaseClassCore):
    __guid__ = 'form.OnOfflineUserEntry'
    default_name = 'onOfflineUserEntry'
    default_left = default_top = 64
    default_width = default_height = 64
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        par = uicls.Container(parent=self, name='par', align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        dot = uicls.Sprite(parent=par, name='dot', pos=(-1, -1, 66, 66), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/shapeDot.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        icon = uicls.Sprite(parent=par, name='icon', pos=(0, 0, 64, 64), state=uiconst.UI_DISABLED)
        shadow = uicls.Sprite(parent=par, name='shadow', pos=(-13, -6, 90, 90), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/shapeShadow.png')



    def Startup(self, charid, online):
        self.CheckPos(self.parent)
        self.state = uiconst.UI_NORMAL
        self.sr.picture = uiutil.GetChild(self, 'icon')
        self.charid = charid
        self.online = online
        sm.GetService('photo').GetPortrait(self.charid, 128, self.sr.picture)
        self.sr.hint = [mls.UI_SHARED_USERISNOWOFFLINE, mls.UI_SHARED_USERISNOWONLINE][online] % {'name': cfg.eveowners.Get(charid).name}
        nme = uicls.Label(text='<center>%s' % uiutil.UpperCase(cfg.eveowners.Get(charid).name), parent=self, left=0, top=1, width=self.width, autowidth=False, letterspace=1, fontsize=9, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.75), idx=0)
        h = nme.height
        nme.top = self.height - h
        uicls.Fill(parent=self, width=self.width, height=h + 1, top=self.height - h - 1, color=(float(not online) * 0.5,
         float(online) * 0.5,
         0.0,
         1.0), idx=1, align=uiconst.RELATIVE)
        uthread.new(self.Kill)



    def Kill(self):
        blue.pyos.synchro.Sleep(10000)
        par = self.parent
        if self.online:
            sm.GetService('ui').CharacterDoneOn(self.charid)
        else:
            sm.GetService('ui').CharacterDoneOff(self.charid)
        self.state = uiconst.UI_HIDDEN
        self.CheckPos(par)
        self.Close()



    def CheckPos(self, par):
        all = []
        for each in par.children:
            if getattr(each, '__guid__', None) == 'form.OnOfflineUserEntry':
                all.append(each)

        i = 0
        for each in all:
            each.left = uicore.desktop.width - 76
            each.top = uicore.desktop.height - 106 - i * 80
            i = i + 1





