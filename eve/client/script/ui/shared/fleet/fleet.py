import xtriui
import uix
import mathUtil
import util
import uthread
import listentry
import destiny
import blue
import state
import _weakref
import fleetbr
import chat
import types
import uiutil
import uiconst
import uicls
import form
import fleetcommon
import log
import trinity
from fleetcommon import CHANNELSTATE_LISTENING, CHANNELSTATE_SPEAKING, CHANNELSTATE_MAYSPEAK, CHANNELSTATE_NONE
from fleetcommon import SQUAD_STATUS_NOSQUADCOMMANDER, SQUAD_STATUS_TOOMANYMEMBERS, SQUAD_STATUS_TOOFEWMEMBERS, FLEET_STATUS_TOOFEWWINGS, FLEET_STATUS_TOOMANYWINGS

def CommanderName(group):
    cmdr = group['commander']
    if cmdr:
        return cfg.eveowners.Get(cmdr).name
    else:
        return '<color=0x%%(alpha)xffffff>%s</color>' % mls.UI_FLEET_NOCOMMANDER



def SquadronName(fleet, squadID):
    squadron = fleet['squads'][squadID]
    squadronName = squadron['name']
    if squadronName == '':
        squadno = GroupNumber(fleet, 'squad', squadID)
        squadronName = '%s %s' % (mls.UI_FLEET_SQUAD, squadno)
    return squadronName



def WingName(fleet, wingID):
    wing = fleet['wings'][wingID]
    wingName = wing['name']
    if wingName == '':
        wingno = GroupNumber(fleet, 'wing', wingID)
        wingName = '%s %s' % (mls.UI_FLEET_WING, wingno)
    return wingName



def GroupNumber(fleet, groupType, groupID):
    ids = fleet[('%ss' % groupType)].keys()
    ids.sort()
    return ids.index(groupID) + 1



def ChannelTypeToHeaderType(channelType):
    if channelType == 'squadid':
        return 'squad'
    if channelType == 'wingid':
        return 'wing'
    if channelType == 'fleetid':
        return 'fleet'



def HeaderTypeToChannelType(channelType):
    if channelType == 'squad':
        return 'squadid'
    if channelType == 'wing':
        return 'wingid'
    if channelType == 'fleet':
        return 'fleetid'



def GetParsedChannelID(channelID):
    ch = util.KeyVal()
    if type(channelID) is types.TupleType:
        if type(channelID[0]) is types.TupleType:
            channelID = channelID[0]
        ch.tuple = channelID
        ch.type = channelID[0]
        ch.integer = channelID[1]
    else:
        ch.tuple = (channelID,)
        ch.type = None
        ch.integer = channelID
    return ch



def GetChannelMenu(what, id):
    channelName = (what, id)
    m = []
    state = sm.GetService('fleet').GetVoiceChannelState(channelName)
    if state in [CHANNELSTATE_LISTENING, CHANNELSTATE_SPEAKING, CHANNELSTATE_MAYSPEAK]:
        m.append((mls.UI_CMD_LEAVECHANNEL, sm.GetService('vivox').LeaveChannel, (channelName,)))
    elif sm.GetService('fleet').CanIJoinChannel(what, id):
        m.append((mls.UI_CMD_JOINCHANNEL, sm.GetService('vivox').JoinChannel, (channelName,)))
    if not (session.fleetrole == const.fleetRoleLeader and what != 'fleetid' or session.fleetrole == const.fleetRoleWingCmdr and (what != 'wingid' or id != session.wingid or session.fleetrole == const.fleetRoleSquadCmdr and (what != 'squadid' or id != session.squadid or session.fleetrole == const.fleetRoleMember))):
        if sm.GetService('fleet').GetChannelMuteStatus(channelName):
            m.append((mls.UI_CMD_UNMUTECHANNEL, sm.GetService('fleet').SetVoiceMuteStatus, (0, channelName)))
        else:
            m.append((mls.UI_CMD_MUTECHANNEL, sm.GetService('fleet').SetVoiceMuteStatus, (1, channelName)))
    if m:
        m = [(mls.UI_GENERIC_CHANNEL, m)]
    return m



def GetSquadMenu(squadID):
    m = []
    if sm.GetService('fleet').IsBoss() or session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr):
        m = [(mls.UI_FLEET_CHANGENAME, lambda : sm.GetService('fleet').ChangeSquadName(squadID)), (mls.UI_FLEET_DELETESQUAD, lambda : sm.GetService('fleet').DeleteSquad(squadID))]
    m += GetChannelMenu('squadid', squadID)
    m.append((mls.UI_FLEET_ADDSQUADTOWATCHLIST, lambda : sm.GetService('fleet').AddFavoriteSquad(squadID)))
    return m



class FleetView(uicls.Container):
    __guid__ = 'form.FleetView'
    __notifyevents__ = ['OnFleetMemberChanging',
     'OnVoiceChannelJoined',
     'OnVoiceChannelLeft',
     'OnVoiceSpeakingChannelSet',
     'OnVoiceChannelIconClicked',
     'OnCollapsed',
     'OnExpanded',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnFleetWingAdded_Local',
     'OnFleetWingDeleted_Local',
     'OnFleetSquadAdded_Local',
     'OnFleetSquadDeleted_Local',
     'OnFleetMemberChanged_Local',
     'OnFleetWingNameChanged_Local',
     'OnFleetSquadNameChanged_Local',
     'OnVoiceMuteStatusChange_Local',
     'OnMemberMuted_Local',
     'OnFleetOptionsChanged_Local']

    def PostStartup(self):
        sm.RegisterNotify(self)
        header = self
        header.baseHeight = 30
        e = self.sr.topEntry = FleetChannels(parent=header, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=22)
        e.Startup()
        self.top = -1
        uicls.Container(name='push', parent=self, align=uiconst.TOBOTTOM, height=3)
        self.sr.scroll = uicls.Scroll(parent=self)
        self.isFlat = settings.user.ui.Get('flatFleetView', True)
        self.members = {}
        self.voiceChannels = {}
        self.askingJoinVoice = False
        self.pending_RefreshFromRec = []
        self.scrollToProportion = 0
        self.HandleFleetChanged()
        if sm.GetService('fleet').GetOptions().isVoiceEnabled:
            self.SetAutoJoinVoice()



    def Load(self, args):
        if not self.sr.Get('inited', 0):
            setattr(self.sr, 'inited', 1)
            self.PostStartup()
        if session.fleetid is not None:
            if getattr(self.sr, 'scroll', None):
                self.sr.scroll._OnResize()



    def GetCollapsedHeight(self):
        return form.ActionPanel.GetCollapsedHeight(self) + self.sr.topParent.height



    def OnFleetMemberChanging(self, charID):
        rec = self.members.get(charID)
        if rec is not None:
            rec.changing = True
            self.RefreshFromRec(rec)



    def UpdateHeader(self):
        wnd = sm.GetService('window').GetWindow('fleetwindow')
        wnd.UpdateHeader()



    def CheckHint(self):
        if not self.sr.scroll.GetNodes():
            self.sr.scroll.ShowHint(mls.UI_INFLIGHT_NOFLEET)
        else:
            self.sr.scroll.ShowHint()
        self.UpdateHeader()



    def OnFleetWingAdded_Local(self, *args):
        self.HandleFleetChanged()



    def OnFleetWingDeleted_Local(self, *args):
        self.HandleFleetChanged()



    def OnFleetSquadAdded_Local(self, *args):
        self.HandleFleetChanged()



    def OnFleetSquadDeleted_Local(self, *args):
        self.HandleFleetChanged()



    def OnFleetSquadNameChanged_Local(self, squadID, name):
        self.fleet['squads'][squadID]['name'] = name
        headerNode = self.HeaderNodeFromGroupTypeAndID('squad', squadID)
        if headerNode:
            numMembers = len(sm.GetService('fleet').GetMembersInSquad(squadID))
            if numMembers == 0:
                headerNode.label = '%s (%s)' % (name, mls.UI_FLEET_NOMEMBERS)
            else:
                headerNode.groupInfo = '%s (%s)' % (name, numMembers)
            if headerNode.panel:
                headerNode.panel.Load(headerNode)



    def OnFleetWingNameChanged_Local(self, wingID, name):
        self.fleet['wings'][wingID]['name'] = name
        headerNode = self.HeaderNodeFromGroupTypeAndID('wing', wingID)
        if headerNode:
            numMembers = len(sm.GetService('fleet').GetMembersInWing(wingID))
            if numMembers == 0:
                headerNode.groupInfo = '%s (%s)' % (name, mls.UI_FLEET_NOMEMBERS)
            else:
                headerNode.groupInfo = '%s (%s)' % (name, numMembers)
            if headerNode.panel:
                headerNode.panel.Load(headerNode)



    def OnVoiceMuteStatusChange_Local(self, status, channel, leader, exclusionList):
        if session.charid not in getattr(self, 'members', []):
            return 
        t = 'fleet'
        if channel[0][0] == 'wingid':
            t = 'wing'
        elif channel[0][0] == 'squadid':
            t = 'squad'
        headerNode = self.HeaderNodeFromGroupTypeAndID(t, channel[0][1])
        if headerNode:
            headerNode.channelIsMuted = status
            if headerNode.panel:
                headerNode.panel.Load(headerNode)
                self.ReloadScrollEntry(headerNode)



    def OnMemberMuted_Local(self, charID, channel, isMuted):
        rec = self.members[charID]
        self.RefreshFromRec(rec)
        if charID == session.charid:
            parsedChannelID = GetParsedChannelID(channel)
            headerType = ChannelTypeToHeaderType(parsedChannelID.type)
            fleetHeader = self.HeaderNodeFromGroupTypeAndID(headerType, parsedChannelID.integer)
            if fleetHeader and fleetHeader.panel:
                fleetHeader.panel.UpdateVoiceIcon()



    def OnFleetJoin_Local(self, rec):
        if not self or self.destroyed:
            return 
        if rec.charID == session.charid:
            self.HandleFleetChanged()
        else:
            self.AddChar(rec)



    def GetPanel(self, what):
        return sm.GetService('window').GetWindow(what)



    def OnFleetOptionsChanged_Local(self, oldOptions, options):
        if not oldOptions.isVoiceEnabled and options.isVoiceEnabled and self.askingJoinVoice == False:
            self.askingJoinVoice = True
            self.SetAutoJoinVoice()



    def SetAutoJoinVoice(self):
        if FleetSvc().IsBoss():
            sm.GetService('fleet').SetAutoJoinVoice()
        elif settings.user.audio.Get('talkAutoJoinFleet', 1) and not getattr(sm.GetService('fleet'), 'isAutoJoinVoice', 0):
            if eve.Message('FleetConfirmAutoJoinVoice', {}, uiconst.YESNO) == uiconst.ID_YES:
                sm.GetService('fleet').SetAutoJoinVoice()
            else:
                settings.user.audio.Set('talkAutoJoinFleet', 0)
        self.askingJoinVoice = False



    def AddChar(self, rec):
        self.members[rec.charID] = rec
        FleetSvc().AddToFleet(self.fleet, rec)
        if not self.isFlat:
            self.HandleFleetChanged()
        self.RefreshFromRec(rec)



    def OnFleetLeave_Local(self, rec):
        if rec.charID == session.charid:
            return 
        self.RemoveChar(rec.charID)
        if rec.role == const.fleetRoleSquadCmdr:
            self.FlashHeader('squad', rec.squadID)
        elif rec.role == const.fleetRoleWingCmdr:
            self.FlashHeader('wing', rec.wingID)
        elif rec.role == const.fleetRoleLeader:
            self.FlashHeader('fleet', session.fleetid)



    def RemoveChar(self, charID):
        rec = self.members.pop(charID, None)
        if None not in (rec.squadID, rec.wingID):
            self.RemoveFromFleet(self.fleet, rec)
            if self.isFlat:
                self.RemoveCharFromScroll(charID)
            else:
                self.HandleFleetChanged()
            self.RefreshFromRec(rec, removing=1)



    def OnFleetMemberChanged_Local(self, charID, fleetID, oldWingID, oldSquadID, oldRole, oldJob, oldBooster, newWingID, newSquadID, newRole, newJob, newBooster):
        rec = self.members[charID]

        def UpdateRec():
            rec.changing = False
            (rec.role, rec.job,) = (newRole, newJob)
            (rec.wingID, rec.squadID,) = (newWingID, newSquadID)
            rec.roleBooster = newBooster


        if (oldWingID, oldSquadID) != (newWingID, newSquadID):
            if self.isFlat:
                UpdateRec()
                self.RefreshFromRec(rec)
            elif const.fleetRoleLeader in (oldRole, newRole):
                self.HandleFleetChanged()
            else:
                self.RemoveChar(charID)
                UpdateRec()
                self.AddChar(rec)
        else:
            UpdateRec()
            if oldRole == const.fleetRoleSquadCmdr != newRole:
                self.fleet['squads'][rec.squadID]['commander'] = None
            elif oldRole == const.fleetRoleMember != newRole:
                self.fleet['squads'][rec.squadID]['commander'] = rec.charID
            self.RefreshFromRec(rec)
        if oldRole == const.fleetRoleSquadCmdr and (newRole != const.fleetRoleSquadCmdr or newSquadID != oldSquadID):
            self.FlashHeader('squad', oldSquadID)
        elif oldRole == const.fleetRoleWingCmdr and (newRole != const.fleetRoleWingCmdr or newWingID != oldWingID):
            self.FlashHeader('wing', oldWingID)
        elif oldRole == const.fleetRoleLeader != newRole:
            self.FlashHeader('fleet', session.fleetid)



    def FlashHeader(self, groupType, groupID):
        headerNode = self.HeaderNodeFromGroupTypeAndID(groupType, groupID)
        if headerNode and headerNode.panel:
            if hasattr(headerNode.panel, 'Flash'):
                headerNode.panel.Flash()



    def RemoveFromFleet(self, fleet, rec):

        def Name(charID):
            return charID and cfg.eveowners.Get(charID).name



        def RemoveCommander(group, charID):
            if group['commander'] == charID:
                group['commander'] = None
            else:
                log.LogError('Commander is', Name(group['commander']), 'not', Name(charID))


        if rec.squadID != -1:
            squad = fleet['squads'][rec.squadID]
            if rec.role == const.fleetRoleSquadCmdr:
                RemoveCommander(squad, rec.charID)
            try:
                squad['members'].remove(rec.charID)
            except ValueError:
                log.LogError(Name(rec.charID), 'not in squad.')
        elif rec.wingID != -1:
            RemoveCommander(fleet['wings'][rec.wingID], rec.charID)
        else:
            RemoveCommander(fleet, rec.charID)



    def RefreshFromRec(self, rec, removing = 0):
        self.scrollToProportion = self.sr.scroll.GetScrollProportion()
        if getattr(self, 'loading_RefreshFromRec', 0):
            self.pending_RefreshFromRec.append(rec)
            return 
        setattr(self, 'loading_RefreshFromRec', 1)
        try:
            if self.isFlat:
                if not removing:
                    self.AddOrUpdateScrollEntry(rec.charID)
            elif rec.wingID not in (None, -1):
                wingHeaderNode = self.HeaderNodeFromGroupTypeAndID('wing', rec.wingID)
                if rec.squadID not in (None, -1):
                    if wingHeaderNode:
                        self.ReloadScrollEntry(wingHeaderNode)
                else:
                    fleetHeaderNode = self.HeaderNodeFromGroupTypeAndID('fleet', session.fleetid)
                    if fleetHeaderNode:
                        self.ReloadScrollEntry(fleetHeaderNode)
            else:
                self.HandleFleetChanged()
            self.UpdateHeader()
            setattr(self, 'loading_RefreshFromRec', 0)
            if self.pending_RefreshFromRec:
                rec = self.pending_RefreshFromRec[0].copy()
                del self.pending_RefreshFromRec[0]
                self.RefreshFromRec(rec)

        finally:
            setattr(self, 'loading_RefreshFromRec', 0)




    def ReloadScrollEntry(self, headerNode):
        if headerNode:
            scroll = getattr(headerNode, 'scroll', None)
            if scroll:
                scroll.PrepareSubContent(headerNode)



    def HeaderNodeFromGroupTypeAndID(self, groupType, groupID):
        for entry in self.sr.scroll.GetNodes():
            if entry.groupType == groupType and entry.groupID == groupID:
                return entry




    def HandleFleetChanged(self):
        uthread.pool('FleetView::HandleFleetChanged', self.DoHandleFleetChanged)



    def DoHandleFleetChanged(self):
        if not self or self.destroyed:
            return 
        if getattr(self, 'loading_HandleFleetChanged', 0):
            setattr(self, 'pending_HandleFleetChanged', 1)
            return 
        setattr(self, 'loading_HandleFleetChanged', 1)
        blue.pyos.synchro.Sleep(1000)
        setattr(self, 'pending_HandleFleetChanged', 0)
        try:
            try:
                self.members = FleetSvc().GetMembers().copy()
                if session.charid in self.members:
                    self.sr.scroll.Load(contentList=[])
                    self.LoadFleet()
                    self.CheckHint()
                setattr(self, 'loading_HandleFleetChanged', 0)
                if getattr(self, 'pending_HandleFleetChanged', 0):
                    setattr(self, 'pending_HandleFleetChanged', 0)
                    self.HandleFleetChanged()

            finally:
                setattr(self, 'loading_HandleFleetChanged', 0)

        except:
            pass



    def EmptyGroupEntry(self, label, indent):
        data = util.KeyVal()
        data.label = '( %s )' % label
        data.indent = indent
        return listentry.Get('EmptyGroup', data=data)



    def MakeCharEntry(self, charID, sublevel = 0, isLast = False):
        data = self.GetMemberData(charID, sublevel=sublevel)
        data.isLast = isLast
        return listentry.Get('FleetMember', data=data)



    def MakeSquadEntry(self, squadID, sublevel = 0):
        headerdata = self.GetHeaderData('squad', squadID, sublevel)
        if headerdata.numMembers == 0:
            data = util.KeyVal()
            data.squadID = squadID
            data.groupType = 'squad'
            data.groupID = squadID
            data.label = '%s (%s)' % (headerdata.groupInfo, mls.UI_FLEET_NOMEMBERS)
            data.GetMenu = self.EmptySquadMenu
            data.indent = 2
            return listentry.Get('EmptyGroup', data=data)
        else:
            return listentry.Get('FleetHeader', data=headerdata)



    def EmptySquadMenu(self, entry):
        return GetSquadMenu(entry.sr.node.squadID)



    def MakeWingEntry(self, wingID, sublevel = 0):
        headerdata = self.GetHeaderData('wing', wingID, sublevel)
        return listentry.Get('FleetHeader', data=headerdata)



    def MakeFleetEntry(self):
        headerdata = self.GetHeaderData('fleet', session.fleetid, 0)
        return listentry.Get('FleetHeader', data=headerdata)



    def AddToScroll(self, *entries):
        self.sr.scroll.AddEntries(-1, entries)



    def RemoveCharFromScroll(self, charID):
        for entry in self.sr.scroll.GetNodes():
            if entry.charID == charID:
                self.sr.scroll.RemoveEntries([entry])
                return 




    def LoadFleet(self):
        fleet = self.fleet = FleetSvc().GetFleetHierarchy(dict([ (charID, member) for (charID, member,) in self.members.iteritems() if None not in (member.squadID, member.wingID) ]))
        if self.isFlat:
            scrolllist = []
            for charID in self.members.keys():
                entry = self.MakeCharEntry(charID, sublevel=1, isLast=True)
                scrolllist.append((cfg.eveowners.Get(charID).name, entry))

            scrolllist = uiutil.SortListOfTuples(scrolllist)
            self.sr.scroll.Load(contentList=scrolllist)
        else:
            self.AddToScroll(self.MakeFleetEntry())
            self.sr.scroll.ScrollToProportion(self.scrollToProportion, updateScrollHandle=True)



    def GetMemberData(self, charID, slimItem = None, member = None, sublevel = 0):
        if slimItem is None:
            slimItem = util.SlimItemFromCharID(charID)
        data = util.KeyVal()
        data.charRec = cfg.eveowners.Get(charID)
        data.itemID = data.id = data.charID = charID
        data.typeID = data.charRec.typeID
        data.squadID = None
        data.wingID = None
        data.displayName = data.charRec.name
        data.roleString = ''
        data.roleIcons = []
        data.muteStatus = sm.GetService('fleet').CanIMuteOrUnmuteCharInMyChannel(charID)
        member = member or self.members.get(charID)
        if member:
            data.squadID = member.squadID
            data.wingID = member.wingID
            data.role = member.role
            if member.job & const.fleetJobCreator:
                data.roleString += ' (%s)' % mls.UI_FLEET_ABBREV_JOBCREATOR
                data.roleIcons.append({'id': '73_20',
                 'hint': mls.UI_FLEET_BOSS})
            if member.role in (const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr):
                data.roleString += ' (%s)' % mls.UI_FLEET_ABBREV_COMMANDER
            b = None
            if member.roleBooster == const.fleetBoosterFleet:
                b = mls.UI_FLEET_FLEETINITIAL
                data.roleIcons.append({'id': '73_22',
                 'hint': mls.UI_FLEET_FLEETBOOSTER})
            elif member.roleBooster == const.fleetBoosterWing:
                b = mls.UI_FLEET_WINGINITIAL
                data.roleIcons.append({'id': '73_23',
                 'hint': mls.UI_FLEET_WINGBOOSTER})
            elif member.roleBooster == const.fleetBoosterSquad:
                b = mls.UI_FLEET_SQUADINITIAL
                data.roleIcons.append({'id': '73_24',
                 'hint': mls.UI_FLEET_SQUADBOOSTER})
            if b:
                data.roleString += ' (%s)' % b
            if member.role == const.fleetRoleLeader:
                data.roleIcons.append({'id': '73_17',
                 'hint': mls.UI_FLEET_FLEETCOMMANDER})
            elif member.role == const.fleetRoleWingCmdr:
                data.roleIcons.append({'id': '73_18',
                 'hint': mls.UI_FLEET_WINGCOMMANDER})
            elif member.role == const.fleetRoleSquadCmdr:
                data.roleIcons.append({'id': '73_19',
                 'hint': mls.UI_FLEET_SQUADCOMMANDER})
        data.label = data.displayName
        data.isSub = 0
        data.sort_name = data.displayName
        data.sublevel = sublevel
        data.member = member
        if slimItem:
            data.slimItem = _weakref.ref(slimItem)
        else:
            data.slimItem = None
        data.changing = getattr(member, 'changing', False)
        return data



    def GetHeaderData(self, gtype, gid, sublevel):
        data = util.KeyVal()
        data.id = ('fleet', '%s_%s' % (gtype, gid))
        channelName = (HeaderTypeToChannelType(gtype), gid)
        data.voiceChannelName = channelName
        data.groupType = gtype
        data.groupID = gid
        data.rawText = ''
        data.displayName = data.label = ''
        data.sublevel = sublevel
        data.expanded = True
        data.showicon = 'hide'
        data.hideFill = True
        data.hideTopLine = True
        data.hideExpanderLine = True
        data.showlen = False
        data.BlockOpenWindow = 1
        data.voiceIconChannel = None
        data.channelIsMuted = sm.GetService('fleet').GetChannelMuteStatus(channelName)
        data.labelstyle = {'uppercase': True,
         'fontsize': 9,
         'letterspacing': 2}
        group = self.GetGroup(gtype, gid)
        data.commanderName = CommanderName(group) % {'alpha': 119}
        data.commanderMuteStatus = sm.GetService('fleet').CanIMuteOrUnmuteCharInMyChannel(group['commander'])
        data.commanderData = None
        num = 0
        if gtype == 'squad':
            data.GetSubContent = self.SquadContentGetter(gid, sublevel)
            num = len(sm.GetService('fleet').GetMembersInSquad(gid))
            if num == 0:
                data.groupInfo = SquadronName(self.fleet, gid)
            else:
                data.groupInfo = '%s (%s)' % (SquadronName(self.fleet, gid), num)
        elif gtype == 'wing':
            data.GetSubContent = self.WingContentGetter(gid, sublevel)
            num = len(sm.GetService('fleet').GetMembersInWing(gid))
            data.groupInfo = '%s (%s)' % (WingName(self.fleet, gid), num)
        elif gtype == 'fleet':
            data.GetSubContent = self.FleetContentGetter(gid, sublevel)
            num = len(self.members)
            data.groupInfo = '%s (%s)' % (mls.UI_FLEET_FLEET, num)
            data.scroll = self.sr.scroll
        else:
            raise NotImplementedError
        data.numMembers = num
        if group['commander']:
            commanderData = self.GetMemberData(group['commander'])
            data.commanderData = commanderData
        data.active = self.IsGroupActive(gtype, gid)
        data.openByDefault = data.open = True
        return data



    def AddOrUpdateScrollEntry(self, charID):
        newEntry = self.MakeCharEntry(charID)
        newEntry.sublevel = 1
        newEntry.isLast = 1
        for (i, data,) in enumerate(self.sr.scroll.GetNodes()):
            if data.Get('id', None) == charID:
                newEntry.panel = data.Get('panel', None)
                scroll = data.Get('scroll', None)
                if scroll is not None:
                    newEntry.scroll = scroll
                newEntry.idx = i
                self.sr.scroll.GetNodes()[i] = newEntry
                if newEntry.panel is not None:
                    newEntry.panel.Load(newEntry)
                return 

        self.sr.scroll.AddEntries(-1, [newEntry])
        self.sr.scroll.Sort(by='name')



    def IsGroupActive(self, gtype, gid):
        return self.GetGroup(gtype, gid)['active']



    def SquadContentGetter(self, squadID, sublevel):

        def GetContent(*blah):
            squad = self.fleet['squads'][squadID]
            ret = []
            if squad['members']:
                sortedMembers = uiutil.SortListOfTuples([ ((charID != squad['commander'], self.members[charID].job != const.fleetJobCreator, cfg.eveowners.Get(charID).name), charID) for charID in squad['members'] ])
                if squad['commander'] is not None:
                    sortedMembers.remove(squad['commander'])
                for i in range(len(sortedMembers)):
                    charID = sortedMembers[i]
                    ret.append(self.MakeCharEntry(charID, sublevel=sublevel + 1, isLast=i == len(sortedMembers) - 1))

            if not ret:
                ret = [self.EmptyGroupEntry(mls.UI_FLEET_NOMEMBERS, sublevel + 1)]
            return ret


        return GetContent



    def WingContentGetter(self, wingID, sublevel):

        def GetContent(*blah):
            wing = self.fleet['wings'][wingID]
            ret = []
            squads = wing['squads'][:]
            squads.sort()
            for squadID in squads:
                ret.append(self.MakeSquadEntry(squadID, sublevel + 1))

            if not ret:
                ret = [self.EmptyGroupEntry(mls.UI_FLEET_NOCOMMANDERORSQUADS, sublevel + 1)]
            return ret


        return GetContent



    def FleetContentGetter(self, fleetID, sublevel):

        def GetContent(*blah):
            ret = []
            wings = self.fleet['wings'].keys()
            wings.sort()
            for wingID in wings:
                ret.append(self.MakeWingEntry(wingID, sublevel + 1))

            return ret


        return GetContent



    def GetGroup(self, groupType, groupID):
        if groupType == 'fleet':
            return self.fleet
        if groupType == 'wing':
            return self.fleet['wings'][groupID]
        if groupType == 'squad':
            return self.fleet['squads'][groupID]
        raise NotImplementedError



    def GetMemberEntry(self, charID):
        for entry in self.sr.scroll.GetNodes():
            if entry.charID == charID:
                return entry




    def OnVoiceChannelJoined(self, channelID):
        parsedChannelID = GetParsedChannelID(channelID)
        headerType = ChannelTypeToHeaderType(parsedChannelID.type)
        fleetHeader = self.HeaderNodeFromGroupTypeAndID(headerType, parsedChannelID.integer)
        if fleetHeader and fleetHeader.panel:
            fleetHeader.panel.UpdateVoiceIcon()



    def OnVoiceChannelLeft(self, channelID):
        state = sm.GetService('fleet').GetVoiceChannelState(channelID)
        parsedChannelID = GetParsedChannelID(channelID)
        headerType = ChannelTypeToHeaderType(parsedChannelID.type)
        fleetHeader = self.HeaderNodeFromGroupTypeAndID(headerType, parsedChannelID.integer)
        if fleetHeader and fleetHeader.panel:
            fleetHeader.panel.UpdateVoiceIcon()



    def OnVoiceSpeakingChannelSet(self, channelID, oldChannelID):
        if channelID:
            state = sm.GetService('fleet').GetVoiceChannelState(channelID)
            parsedChannelNew = GetParsedChannelID(channelID)
        parsedChannelOld = GetParsedChannelID(oldChannelID)
        if channelID:
            headerTypeNew = ChannelTypeToHeaderType(parsedChannelNew.type)
        headerTypeOld = ChannelTypeToHeaderType(parsedChannelOld.type)
        if channelID:
            fleetHeaderNew = self.HeaderNodeFromGroupTypeAndID(headerTypeNew, parsedChannelNew.integer)
        fleetHeaderOld = self.HeaderNodeFromGroupTypeAndID(headerTypeOld, parsedChannelOld.integer)
        if channelID and fleetHeaderNew and fleetHeaderNew.panel:
            fleetHeaderNew.panel.UpdateVoiceIcon()
        if fleetHeaderOld and fleetHeaderOld.panel:
            fleetHeaderOld.panel.UpdateVoiceIcon()



    def OnVoiceChannelIconClicked(self, iconHeader):
        state = sm.GetService('fleet').GetVoiceChannelState(iconHeader.sr.node.voiceChannelName)
        if state == CHANNELSTATE_NONE:
            sm.GetService('vivox').JoinChannel(iconHeader.sr.node.voiceIconChannel)
        elif state == CHANNELSTATE_MAYSPEAK:
            sm.GetService('vivox').SetSpeakingChannel(iconHeader.sr.node.voiceIconChannel)
        elif state == CHANNELSTATE_SPEAKING:
            sm.GetService('vivox').SetSpeakingChannel(None)



    def UpdateVoiceIcon(self, id):
        for node in self.GetNodes():
            if node.id == id and node.panel:
                node.panel.UpdateVoiceIcon()




    def OnCollapsed(self, wnd, *args):
        self.sr.headerLine.state = uiconst.UI_NORMAL



    def OnExpanded(self, wnd, *args):
        pass




class FleetHeader(listentry.Group):
    __guid__ = 'listentry.FleetHeader'

    def Startup(self, *args, **kw):
        listentry.Group.Startup(self, *args, **kw)
        sel = uiutil.GetChild(self, 'selection')
        idx = sel.parent.children.index(sel)
        text_gaugepar = uicls.Container(name='text_gaugepar', parent=sel.parent, idx=idx, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        text_gaugepar.width = 0
        self.sr.text_gaugepar = text_gaugepar
        self.sr.label.parent.width = 0
        uiutil.Transplant(self.sr.label.parent, text_gaugepar)
        uicls.Container(name='toppush', parent=self.sr.label.parent, align=uiconst.TOTOP, height=14)
        roleIconsContainer = uicls.Container(name='roleIconsContainer', parent=self.sr.label.parent, width=0, align=uiconst.TORIGHT)
        self.roleIconsContainer = roleIconsContainer
        self.sr.topLabel = uicls.Label(text='', parent=self.sr.label.parent, left=0, top=0, state=uiconst.UI_DISABLED, color=None, idx=0)
        self.sr.bottomLabel = uicls.Label(text='', parent=self.sr.label.parent, left=0, top=12, state=uiconst.UI_DISABLED, color=None, idx=0)
        changing = uicls.AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPRIGHT, parent=self, pos=(0, 13, 16, 16))
        self.sr.changing = changing
        changing.state = uiconst.UI_NORMAL



    def Load(self, node, *args, **kw):
        sublevel = node.Get('sublevel', 0)
        if node.groupType != 'fleet':
            node.hasArrow = True
        listentry.Group.Load(self, node, *args, **kw)
        if node.groupType not in ('fleet', 'wing'):
            self.sr.expander.left += 24
        else:
            self.sr.expander.left += 16
        self.sr.bottomLineLeft.width += 16 + 16 * sublevel
        if node.groupType == 'squad':
            left = 44
        else:
            left = 38
        left += sublevel * 16
        self.sr.label.left = left
        self.sr.topLabel.left = left
        self.sr.bottomLabel.left = left
        self.sr.topLabel.text = '<b>' + node.groupInfo + '</b>'
        if node.numMembers == 0:
            self.sr.topLabel.text = '<color=0x88ffffff>%s</color>' % self.sr.topLabel.text
        if node.channelIsMuted:
            self.sr.topLabel.text += ' (<color=0xff992222>%s</color>)' % mls.UI_FLEET_MUTED
        self.sr.bottomLabel.top = max(12, self.sr.topLabel.top + self.sr.topLabel.textheight)
        self.sr.bottomLabel.text = node.commanderName
        if node.commanderMuteStatus > 0:
            self.sr.bottomLabel.text += ' (%s)' % mls.UI_FLEET_UNMUTED
        icons = getattr(node.commanderData, 'roleIcons', [])
        UpdateRoleIcons(self.roleIconsContainer, icons)
        self.CreateVoiceIcon()
        if node.commanderData and node.commanderData.changing:
            self.sr.changing.state = uiconst.UI_DISABLED
            self.hint = mls.UI_FLEET_MEMBERCHANGING
            self.sr.changing.Play()
        else:
            self.hint = None
            self.sr.changing.Stop()
            self.sr.changing.state = uiconst.UI_HIDDEN



    def GetHeight(self, *args):
        (node, width,) = args
        topLabelHeight = uix.GetTextHeight('<b>' + node.groupInfo + '</b>', autoWidth=1, singleLine=1)
        bottomLabelHeight = uix.GetTextHeight(node.commanderName, autoWidth=1, singleLine=1)
        node.height = max(12, topLabelHeight) + bottomLabelHeight + 2
        return node.height



    def ToggleAllSquads(self, node, isOpen = True):
        uthread.pool('FleetHeader::ToggleAllSquads', self.DoToggleAllSquads, node, isOpen)



    def DoToggleAllSquads(self, node, isOpen):
        scroll = node.scroll
        groupID = node.groupID
        groupType = node.groupType
        for entry in scroll.GetNodes():
            if entry.__guid__ != 'listentry.FleetHeader':
                continue
            if entry.groupType == 'squad':
                if entry.panel:
                    self.ShowOpenState(isOpen)
                    self.UpdateLabel()
                    uicore.registry.SetListGroupOpenState(entry.id, isOpen)
                    scroll.PrepareSubContent(entry)
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, isOpen)
                    entry.scroll.PrepareSubContent(entry)




    def GetMenu(self):
        m = []
        commanderData = self.sr.node.commanderData
        if commanderData:
            m += sm.GetService('menu').FleetMenu(commanderData.charID, unparsed=False)
        if self.sr.node.groupType == 'squad':
            return m + [None] + GetSquadMenu(self.sr.node.groupID)
        if self.sr.node.groupType == 'wing':
            return m + [None] + self.GetWingMenu(self.sr.node.groupID)
        if self.sr.node.groupType == 'fleet':
            m += [None] + self.GetFleetMenu()
            m += [None, (mls.UI_FLEET_OPENALLSQUADS, self.ToggleAllSquads, (self.sr.node, True)), (mls.UI_FLEET_CLOSEALLSQUADS, self.ToggleAllSquads, (self.sr.node, False))]
            return m
        raise NotImplementedError



    def GetFleetMenu(self):
        ret = []
        if session.fleetrole != const.fleetRoleLeader:
            ret += [(mls.UI_FLEET_LEAVE, FleetSvc().LeaveFleet)]
        if FleetSvc().IsBoss() or session.fleetrole == const.fleetRoleLeader:
            ret.extend([None, (mls.UI_FLEET_CREATEWING, lambda : FleetSvc().CreateWing())])
        else:
            ret.append(None)
        if session.fleetrole in [const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr]:
            ret.append((mls.UI_FLEET_REGROUP, lambda : FleetSvc().Regroup()))
        if FleetSvc().HasActiveBeacon(session.charid):
            ret.append((mls.UI_FLEET_BROADCASTBEACON, lambda : FleetSvc().SendBroadcast_JumpBeacon()))
        ret.append((mls.UI_FLEET_BROADCASTLOCATION, lambda : FleetSvc().SendBroadcast_Location()))
        ret += GetChannelMenu('fleetid', session.fleetid)
        return ret



    def GetWingMenu(self, wingID):
        if FleetSvc().IsBoss() or session.fleetrole in (const.fleetRoleLeader, const.fleetRoleWingCmdr):
            m = [(mls.UI_FLEET_DELETEWING, lambda : sm.GetService('fleet').DeleteWing(wingID)), (mls.UI_FLEET_CHANGENAME, lambda : sm.GetService('fleet').ChangeWingName(wingID)), (mls.UI_FLEET_CREATESQUAD, lambda : sm.GetService('fleet').CreateSquad(wingID))]
            m += GetChannelMenu('wingid', wingID)
            return m
        else:
            return []



    def Flash(self):
        sm.GetService('ui').BlinkSpriteA(self.sr.topLabel, 1.0, 400, 8, passColor=0)
        sm.GetService('ui').BlinkSpriteA(self.sr.bottomLabel, 1.0, 400, 8, passColor=0)



    def CreateVoiceIcon(self):
        if self.sr.Get('voiceIconContainer'):
            self.UpdateVoiceIcon()
            return 
        container = self.sr.voiceIconContainer = uicls.Container(name='voiceIconContainer', align=uiconst.TOPLEFT, width=16, height=16, state=uiconst.UI_NORMAL, parent=self, idx=0)
        container.OnClick = self.VoiceIconClicked
        self.sr.voiceIcon = uicls.Icon(icon='ui_73_16_36', parent=container, size=16, left=1, top=0, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
        self.UpdateVoiceIcon()



    def SetVoiceIconChannel(self, channel):
        self.sr.node.voiceIconChannel = channel



    def UpdateVoiceIcon(self):
        channelType = HeaderTypeToChannelType(self.sr.node.groupType)
        channelID = (channelType, int(self.sr.node.groupID))
        self.SetVoiceIconChannel(channelID)
        state = sm.GetService('fleet').GetVoiceChannelState(self.sr.node.voiceChannelName)
        self.sr.voiceIcon.state = uiconst.UI_DISABLED
        canJoinChannel = sm.GetService('fleet').CanIJoinChannel(self.sr.node.groupType, self.sr.node.groupID)
        if state == fleetcommon.CHANNELSTATE_LISTENING:
            self.sr.voiceIcon.LoadIcon('ui_73_16_37')
            self.sr.voiceIcon.parent.hint = mls.UI_FLEET_LISTENING_HINT
        elif state == fleetcommon.CHANNELSTATE_SPEAKING:
            self.sr.voiceIcon.LoadIcon('ui_73_16_33')
            self.sr.voiceIcon.parent.hint = mls.UI_FLEET_SPEAKING_HINT
        elif state == fleetcommon.CHANNELSTATE_MAYSPEAK:
            self.sr.voiceIcon.LoadIcon('ui_73_16_35')
            self.sr.voiceIcon.parent.hint = mls.UI_FLEET_MAYSPEAK_HINT
        elif canJoinChannel:
            self.sr.voiceIcon.LoadIcon('ui_73_16_36')
            self.sr.voiceIcon.parent.hint = mls.UI_FLEET_CLICKTOJOIN_HINT
        else:
            self.sr.voiceIcon.state = uiconst.UI_HIDDEN



    def VoiceIconClicked(self, *etc):
        sm.ScatterEvent('OnVoiceChannelIconClicked', self)




def RefreshDiode(self, groupType, groupID, active):
    diode = self.sr.Get('diode', None)
    if groupType == 'fleet' or groupType == 'wing' and groupID == session.wingid or groupType == 'squad' and groupID == session.squadid:
        if diode is None:
            diode = self.sr.diode = Diode(parent=self, idx=0, left=4, top=3)
        if active:
            diode.hint = getattr(mls, 'UI_FLEET_GETTINGBONUSESFROM%s' % groupType.upper())
            diode.On()
        else:
            diode.hint = getattr(mls, 'UI_FLEET_NOTGETTINGBONUSESFROM%s' % groupType.upper())
            diode.Off()
    elif diode is not None:
        diode.Hide()



def UpdateRoleIcons(parent, icons):
    for child in parent.children[:]:
        parent.children.remove(child)

    left = 0
    if icons is not None and len(icons):
        parent.width = len(icons) * 20
        for icon in icons:
            iconpath = icon['id']
            icon = uicls.Icon(icon=iconpath, parent=parent, pos=(left,
             0,
             16,
             16), align=uiconst.TOPLEFT, hint=icon['hint'])
            left += 20




def FleetSvc():
    return sm.GetService('fleet')



def GetFleetMenu():
    ret = [(mls.UI_FLEET_LEAVE, FleetSvc().LeaveFleet)]
    if FleetSvc().IsBoss() or session.fleetrole == const.fleetRoleLeader:
        ret.extend([None, (mls.UI_FLEET_REGROUP, lambda : FleetSvc().Regroup())])
    else:
        ret.append(None)
    if FleetSvc().HasActiveBeacon(session.charid):
        ret.append((mls.UI_FLEET_BROADCASTBEACON, lambda : FleetSvc().SendBroadcast_JumpBeacon()))
    ret.append((mls.UI_FLEET_BROADCASTLOCATION, lambda : FleetSvc().SendBroadcast_Location()))
    return ret



class EmptyGroup(listentry.Generic):
    __guid__ = 'listentry.EmptyGroup'

    def Load(self, data):
        listentry.Generic.Load(self, data)
        self.sr.label.left = 6 + 28 * data.indent
        self.sr.label.color.a = 0.7



    def UpdateVoiceIcon(self):
        pass




class FleetMember(listentry.BaseTacticalEntry):
    __guid__ = 'listentry.FleetMember'

    def Startup(self, *args, **kw):
        listentry.BaseTacticalEntry.Startup(self, *args, **kw)
        idx = self.sr.label.parent.children.index(self.sr.label)
        text_gaugepar = uicls.Container(name='text_gaugepar', parent=self, idx=idx, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        text_gaugepar.width = 0
        textpar = uicls.Container(name='textpar', parent=text_gaugepar, idx=idx, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=True)
        self.sr.text_gaugepar = text_gaugepar
        self.children.remove(self.sr.label)
        textpar.children.append(self.sr.label)
        uicls.Container(name='toppush', parent=textpar, align=uiconst.TOTOP, height=2)
        roleIconsContainer = uicls.Container(name='roleIconsContainer', parent=textpar, width=0, align=uiconst.TORIGHT)
        self.roleIconsContainer = roleIconsContainer
        changing = uicls.AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPRIGHT, parent=self, pos=(0, 0, 16, 16))
        self.sr.changing = changing
        changing.state = uiconst.UI_HIDDEN
        self.sr.selection.width = -200
        self.sr.hilite.width = -200



    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.line.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][node.isLast]
        data = node
        if settings.user.ui.Get('flatFleetView', 1):
            left = 0
        else:
            left = 44
        indent = left + node.sublevel * 16
        self.sr.label.left = indent
        if node.muteStatus > 0:
            self.sr.label.text += ' (unmuted)'
        (selected,) = sm.GetService('state').GetStates(data.itemID, [state.selected])
        self.Select(selected)
        icons = node.Get('roleIcons', None)
        UpdateRoleIcons(self.roleIconsContainer, icons)
        if node.changing:
            self.sr.changing.state = uiconst.UI_DISABLED
            self.hint = mls.UI_FLEET_MEMBERCHANGING
            self.sr.changing.Play()
        else:
            self.hint = None
            self.sr.changing.Stop()
            self.sr.changing.state = uiconst.UI_HIDDEN



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4
        return node.height



    def GetMenu(self):
        shipItem = util.SlimItemFromCharID(self.sr.node.charID)
        if shipItem is None:
            ret = []
        else:
            ret = [ entry for entry in sm.GetService('menu').CelestialMenu(shipItem.itemID) if entry if entry[0] in (mls.UI_CMD_LOCKTARGET,
             mls.UI_CMD_APPROACH,
             mls.UI_CMD_ORBIT,
             mls.UI_CMD_KEEPATRANGE) ]
            ret.append(None)
        ret.extend(sm.GetService('menu').FleetMenu(self.sr.node.charID, unparsed=False))
        return ret


    GetMenu = uiutil.ParanoidDecoMethod(GetMenu, ('sr', 'node'))


class FleetAction(xtriui.Action):
    __guid__ = 'xtriui.FleetAction'

    def Prepare_(self, icon = None):
        pass



    def Startup(self, hint, iconPath):
        uicls.Frame(parent=self, color=(1.0, 1.0, 1.0, 0.2), state=uiconst.UI_DISABLED)
        self.sr.icon = uicls.Icon(icon=iconPath, parent=self, align=uiconst.CENTER, pos=(1, 0, 16, 16), state=uiconst.UI_DISABLED)
        self.hint = hint
        self.sr.fill = uicls.Fill(parent=self, state=uiconst.UI_HIDDEN, top=0, left=0, width=self.width, height=self.height, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))



    def OnMouseMove(self, *args):
        pass



    def GetHint(self, *args):
        return self.hint




class Diode(uicls.Container):
    __guid__ = 'xtriui.SquareDiode'
    default_name = 'diode'
    default_align = uiconst.CENTERRIGHT
    default_state = uiconst.UI_NORMAL
    default_width = 10
    default_height = 10

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        dotproduct = uicls.Sprite(parent=self, name='dotproduct', padding=(1, 1, 1, 1), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SquareDiode/shapeShadow.png', color=(0.34, 0.53, 0.33, 1.0), spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.diode = diode = uicls.Sprite(parent=self, name='diode', padding=(1, 1, 1, 1), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SquareDiode/shapeFill.png', color=(0.75, 0.0, 0.0, 1.0))
        self.selection = selection = uicls.Sprite(parent=self, name='selection', padding=(-4, -4, -4, -4), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/miniSoftGlow.png', color=(0.75, 0.0, 0.0, 1.0))



    def On(self):
        self._Show(0.25, 0.75, 0.0)



    def Off(self):
        self._Show(0.5, 0.1, 0.0)



    def Hide(self):
        self.state = uiconst.UI_HIDDEN
        self._color = None



    def _Show(self, r, g, b):
        self.state = uiconst.UI_NORMAL
        old = getattr(self, '_color', None)
        self._color = (r, g, b)
        self.SetRGB(r, g, b)
        if old not in (None, self._color):
            uthread.pool('Diode::Animate', Flash, self, lambda t: self.SetRGB(*[ mathUtil.Lerp(each, 1, t) for each in self._color ]))



    def SetRGB(self, r, g, b):
        self.diode.SetRGB(r, g, b)
        self.selection.SetRGB(r, g, b)




class FleetChannels(uicls.Container):
    __guid__ = 'xtriui.FleetChannels'
    __notifyevents__ = ['OnVoiceChannelJoined',
     'OnVoiceChannelLeft',
     'OnVoiceSpeakingChannelSet',
     'OnMyFleetInfoChanged',
     'OnSessionChanged',
     'OnMemberMuted_Local',
     'OnSpeakingEvent',
     'OnFleetActive_Local',
     'OnWingActive_Local',
     'OnSquadActive_Local']
    __dependencies__ = ['vivox', 'fleet']

    def Startup(self):
        self.name = 'channelspanel'
        sm.RegisterNotify(self)
        self.buttons = {}
        self.speakingChannelButton = None
        row = uicls.Container(name='channelButtonsContainer', parent=self, align=uiconst.TOTOP, height=18, padTop=2, padRight=2, padLeft=3)
        self.buttonsContainer = uicls.Container(name='buttonsContainer', parent=row, align=uiconst.TORIGHT, width=0)
        self.bonusIconContainer = uicls.Container(name='bonusIconContainer', parent=row, align=uiconst.TOLEFT, width=18)
        uicls.Fill(parent=self.buttonsContainer, left=2, top=2, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        uicls.Fill(parent=self.buttonsContainer, left=2, top=5, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        uicls.Fill(parent=self.buttonsContainer, left=2, top=8, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        uicls.Fill(parent=self.buttonsContainer, left=32, top=2, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        uicls.Fill(parent=self.buttonsContainer, left=32, top=5, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        uicls.Fill(parent=self.buttonsContainer, left=62, top=2, width=2, height=2, state=uiconst.UI_DISABLED, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))
        self.roleIconsContainer = uicls.Container(name='roleIconsContainer', parent=row, align=uiconst.TOLEFT)
        self.InitButtons()
        self.UpdateBonusIcon()
        self.UpdateRoleIcons()
        self.UpdateButtons()



    def OnSpeakingEvent(self, charID, channelID, isSpeaking):
        if int(charID) == session.charid and self.speakingChannelButton:
            self.speakingChannelButton.SetSpeakingIndicator(isSpeaking)



    def UpdateRoleIcons(self):
        info = sm.GetService('fleet').GetMemberInfo(session.charid)
        if info is None:
            return 
        roleMap = {const.fleetRoleLeader: {'id': 'ui_73_16_17',
                                 'hint': mls.UI_FLEET_FLEETCOMMANDER},
         const.fleetRoleWingCmdr: {'id': 'ui_73_16_18',
                                   'hint': mls.UI_FLEET_WINGCOMMANDER},
         const.fleetRoleSquadCmdr: {'id': 'ui_73_16_19',
                                    'hint': mls.UI_FLEET_SQUADCOMMANDER}}
        jobMap = {const.fleetJobCreator: {'id': 'ui_73_16_20',
                                 'hint': mls.UI_FLEET_BOSS}}
        boosterMap = {const.fleetBoosterFleet: {'id': 'ui_73_16_22',
                                   'hint': mls.UI_FLEET_FLEETBOOSTER},
         const.fleetBoosterWing: {'id': 'ui_73_16_23',
                                  'hint': mls.UI_FLEET_WINGBOOSTER},
         const.fleetBoosterSquad: {'id': 'ui_73_16_24',
                                   'hint': mls.UI_FLEET_SQUADBOOSTER}}
        icons = []
        if info.role in [const.fleetRoleLeader, const.fleetRoleWingCmdr, const.fleetRoleSquadCmdr]:
            icons.append(roleMap[info.role])
        if info.job & const.fleetJobCreator:
            icons.append(jobMap[const.fleetJobCreator])
        if info.booster in [const.fleetBoosterFleet, const.fleetBoosterWing, const.fleetBoosterSquad]:
            icons.append(boosterMap[info.booster])
        UpdateRoleIcons(self.roleIconsContainer, icons)



    def InitButtons(self):
        buttonNames = ['fleet',
         'wing',
         'squad',
         'op1',
         'op2']
        for name in buttonNames:
            b = self.buttons.get(name, None)
            if b is None:
                b = xtriui.ChannelsPanelAction()
                b.Startup(self.buttonsContainer, name)
                self.buttons[name] = b
            b.Clear()




    def UpdateButtons(self):
        self.InitButtons()
        self.speakingChannelButton = None
        channels = sm.GetService('fleet').GetVoiceChannels()
        for (name, data,) in channels.iteritems():
            if data is None:
                continue
            button = self.buttons[name]
            button.channelID = data.name
            button.SetAsJoined()
            if data.state == CHANNELSTATE_SPEAKING:
                self.speakingChannelButton = button




    def UpdateBonusIcon(self):
        squadActive = wingActive = fleetActive = False
        activeStatus = sm.GetService('fleet').GetActiveStatus()
        if not activeStatus:
            return 
        fleetActive = activeStatus.fleet
        squadID = session.squadid
        fleetID = session.fleetid
        wingID = session.wingid
        if squadID > 0:
            squadActive = activeStatus.squads.get(squadID, None)
        if wingID > 0:
            wingActive = activeStatus.wings.get(wingID, None)
        log.LogInfo('UpdateBonusIcon() - FLEET:', fleetActive, '- WING:', wingActive, '- SQUAD:', squadActive)
        amIActive = False
        hint = ''
        if session.fleetrole == const.fleetRoleLeader:
            if fleetActive > 0:
                amIActive = True
                hint = mls.UI_FLEET_GIVINGBONUSFLEET
            else:
                hint = '<b>' + mls.UI_FLEET_NOTGIVINGBONUSES + '</b><br>'
                if fleetActive == fleetcommon.FLEET_STATUS_TOOFEWWINGS:
                    hint += mls.UI_FLEET_NOTGIVINGBONUSFLEET_TOOFEW
                elif fleetActive == fleetcommon.FLEET_STATUS_TOOMANYWINGS:
                    hint += mls.UI_FLEET_NOTGIVINGBONUSFLEET_TOOMANY
        elif session.fleetrole == const.fleetRoleWingCmdr:
            if wingActive > 0:
                amIActive = True
                hint = mls.UI_FLEET_GIVINGBONUSWING
            else:
                hint = '<b>' + mls.UI_FLEET_NOTGIVINGBONUSES + '</b><br>'
                hint += mls.UI_FLEET_NOTGIVINGBONUSWING
        elif session.fleetrole == const.fleetRoleSquadCmdr:
            if squadActive > 0:
                amIActive = True
                hint = mls.UI_FLEET_GIVINGBONUSSQUAD
            else:
                hint = '<b>' + mls.UI_FLEET_NOTGIVINGBONUSES + '</b><br>'
                if squadActive == SQUAD_STATUS_NOSQUADCOMMANDER:
                    hint += mls.UI_FLEET_NOTGIVINGBONUSSQUAD_NOCMDR
                elif squadActive == SQUAD_STATUS_TOOMANYMEMBERS:
                    hint += mls.UI_FLEET_NOTGIVINGBONUSSQUAD_TOOMANY
                elif squadActive == SQUAD_STATUS_TOOFEWMEMBERS:
                    hint += mls.UI_FLEET_NOTGIVINGBONUSSQUAD_TOOFEW
        elif squadActive > 0:
            amIActive = True
            hint = mls.UI_FLEET_YOUAREGETTINGBONUSESFROM + '<br><b>'
            hint += mls.UI_FLEET_SQUADBOOSTER
            if wingActive > 0:
                hint += ', ' + mls.UI_FLEET_WINGBOOSTER
                if fleetActive > 0:
                    hint += ', ' + mls.UI_FLEET_FLEETBOOSTER
            hint += '</b>'
        else:
            hint = '<b>' + mls.UI_FLEET_NOTRECEIVINGBONUSES + '</b><br>'
            if squadActive == SQUAD_STATUS_NOSQUADCOMMANDER:
                hint += mls.UI_FLEET_NOTGETTINGBONUS_NOCMDR
            elif squadActive == SQUAD_STATUS_TOOMANYMEMBERS:
                hint += mls.UI_FLEET_NOTGETTINGBONUS_TOOMANY
            elif squadActive == SQUAD_STATUS_TOOFEWMEMBERS:
                pass
        icon = 'ui_38_16_193' if amIActive else 'ui_38_16_194'
        lastHint = getattr(self, 'bonusIconHint', '')
        setattr(self, 'bonusIconHint', hint)
        if hasattr(self, 'bonusIcon'):
            self.bonusIcon.Close()
        self.bonusIcon = uicls.Icon(icon=icon, parent=self.bonusIconContainer, size=16, align=uiconst.RELATIVE)
        if lastHint != getattr(self, 'bonusIconHint', ''):
            sm.GetService('ui').BlinkSpriteA(self.bonusIcon, 1.0, 400, 10, passColor=0)
        self.bonusIcon.hint = hint



    def OnVoiceChannelJoined(self, channelID):
        self.UpdateButtons()



    def OnVoiceChannelLeft(self, channelID):
        self.UpdateButtons()



    def OnVoiceSpeakingChannelSet(self, channelID, oldChannelID):
        self.UpdateButtons()



    def OnMyFleetInfoChanged(self):
        self.UpdateRoleIcons()
        self.UpdateBonusIcon()



    def OnMemberMuted_Local(self, charID, channel, isMuted):
        if charID == session.charid:
            self.UpdateButtons()



    def OnFleetActive_Local(self, isActive):
        self.UpdateBonusIcon()



    def OnWingActive_Local(self, wingID, isActive):
        self.UpdateBonusIcon()



    def OnSquadActive_Local(self, squadID, isActive):
        self.UpdateBonusIcon()



    def OnSessionChanged(self, isRemote, sess, change):
        if not self.destroyed:
            self.UpdateRoleIcons()




class ChannelsPanelAction(uicls.Container):
    __guid__ = 'xtriui.ChannelsPanelAction'

    def Startup(self, parent, name):
        self.name = name
        self.channelID = None
        self.channelState = CHANNELSTATE_NONE
        if name.startswith('op'):
            width = 21
            iconLeft = 3
        else:
            width = 28
            iconLeft = 8
        left = parent.width
        parent.width += width + 2
        self.container = uicls.Container(name=name + '_button', align=uiconst.TOPLEFT, width=width, height=18, top=0, left=left, state=uiconst.UI_NORMAL, parent=parent)
        self.frame = uicls.Frame(parent=self.container, color=(1.0, 1.0, 1.0, 0.3))
        self.fill = uicls.Fill(parent=self.container, state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.02))
        self.sr.icon = uicls.Icon(icon='ui_73_16_36', parent=self.container, pos=(iconLeft,
         1,
         16,
         16), align=uiconst.TOPLEFT, idx=0, state=uiconst.UI_DISABLED)
        self.container.OnClick = self.OnChannelButtonClicked
        self.container.GetMenu = self.OnChannelButtonGetMenu
        self.container.OnMouseEnter = self.OnChannelButtonMouseEnter
        self.container.OnMouseExit = self.OnChannelButtonMouseExit
        self.SetAsUnavailable()



    def OnChannelButtonGetMenu(self, *etc):
        m = []
        state = sm.GetService('fleet').GetVoiceChannelState(self.channelID)
        if state in [CHANNELSTATE_LISTENING, CHANNELSTATE_SPEAKING, CHANNELSTATE_MAYSPEAK]:
            m.append((mls.UI_CMD_LEAVECHANNEL, sm.GetService('vivox').LeaveChannel, (self.channelID,)))
            m.append(None)
        wings = sm.GetService('fleet').wings
        wingids = wings.keys()
        wingids.sort()
        if self.name == 'fleet' and sm.GetService('vivox').IsVoiceChannel(('fleetid', session.fleetid)) == False:
            m.append((mls.UI_CMD_JOINCHANNEL + ': ' + mls.UI_FLEET_FLEET, sm.GetService('vivox').JoinChannel, (('fleetid', session.fleetid),)))
        elif self.name == 'wing':
            for i in range(len(wingids)):
                wid = wingids[i]
                w = wings[wid]
                if sm.GetService('fleet').CanIJoinChannel('wing', wid):
                    name = w.name
                    if not name:
                        name = mls.UI_FLEET_WING + ' %s' % (i + 1)
                    if sm.GetService('vivox').IsVoiceChannel(('wingid', wid)) == False:
                        m.append((mls.UI_CMD_JOINCHANNEL + ': ' + name, sm.GetService('vivox').JoinChannel, (('wingid', wid),)))
                i += 1

        elif self.name == 'squad':
            squadids = []
            squadNames = {}
            i = 1
            for i in range(len(wingids)):
                wid = wingids[i]
                w = wings[wid]
                for (sid, s,) in w.squads.iteritems():
                    squadids.append(sid)
                    name = s.name
                    squadNames[sid] = name
                    i += 1


            squadids.sort()
            for i in range(len(squadids)):
                sid = squadids[i]
                name = squadNames[sid]
                if not name:
                    name = mls.UI_FLEET_SQUAD + ' %s' % (i + 1)
                if sm.GetService('fleet').CanIJoinChannel('squad', sid) and sm.GetService('vivox').IsVoiceChannel(('squadid', sid)) == False:
                    m.append((mls.UI_CMD_JOINCHANNEL + ': ' + name, sm.GetService('vivox').JoinChannel, (('squadid', sid),)))

        elif self.name.startswith('op'):
            import copy
            if not util.IsNPC(session.corpid) and not sm.GetService('vivox').IsVoiceChannel((('corpid', session.corpid),)):
                m.append((mls.UI_CMD_JOINCHANNEL + ': ' + mls.UI_GENERIC_CORP, sm.GetService('vivox').JoinChannel, (('corpid', session.corpid),)))
            if session.allianceid and not sm.GetService('vivox').IsVoiceChannel((('allianceid', session.allianceid),)):
                m.append((mls.UI_CMD_JOINCHANNEL + ': ' + mls.UI_GENERIC_ALLIANCE, sm.GetService('vivox').JoinChannel, (('allianceid', session.allianceid),)))
            channels = copy.copy(settings.char.ui.Get('lscengine_mychannels', []))
            for c in channels:
                channel = sm.services['LSC'].channels.get(c, None)
                if channel is None or channel.info and channel.info.mailingList:
                    continue
                if type(channel.channelID) is int and channel.channelID < 1000 and channel.channelID > 0:
                    continue
                name = ''
                ownerID = None
                if channel.info:
                    ownerID = channel.info.ownerID
                    name = channel.info.displayName
                if ownerID not in (session.allianceid, session.corpid) and not sm.GetService('vivox').IsVoiceChannel(channel.channelID):
                    m.append((mls.UI_CMD_JOINCHANNEL + ': ' + name, sm.GetService('vivox').JoinChannel, (channel.channelID,)))

        return m



    def Clear(self):
        self.SetAsUnavailable()



    def OnChannelButtonMouseEnter(self, *etc):
        self.fill.color.a = 0.3



    def OnChannelButtonMouseExit(self, *etc):
        self.fill.color.a = 0.0



    def OnChannelButtonClicked(self, *etc):
        if self.channelState == CHANNELSTATE_MAYSPEAK:
            sm.GetService('vivox').SetSpeakingChannel(self.channelID)
        elif self.channelState == CHANNELSTATE_SPEAKING:
            sm.GetService('vivox').SetSpeakingChannel(None)



    def SetAsUnavailable(self):
        self.sr.icon.LoadIcon('ui_73_16_36')
        self.channelState = CHANNELSTATE_NONE
        self.container.hint = self.GetChannelNotSetHint()
        self.channelID = None



    def SetAsJoined(self):
        if sm.GetService('vivox').GetSpeakingChannel() == self.channelID:
            self.SetAsSpeaking()
            return 
        if FleetSvc().IsVoiceMuted(self.channelID):
            self.SetAsMuted()
            return 
        self.sr.icon.LoadIcon('ui_73_16_35')
        self.channelState = CHANNELSTATE_MAYSPEAK
        displayName = chat.GetDisplayName(self.channelID)
        self.container.hint = '<b>%s</b><br>%s' % (displayName, mls.UI_FLEET_SET_AS_SPEAKING_CHANNEL)



    def SetAsSpeaking(self):
        self.sr.icon.LoadIcon('ui_73_16_33')
        self.channelState = CHANNELSTATE_SPEAKING
        displayName = chat.GetDisplayName(self.channelID)
        self.container.hint = '<b>%s</b><br>%s' % (displayName, mls.UI_FLEET_SPEAKING_IN_CHANNEL)



    def SetAsMuted(self):
        self.sr.icon.LoadIcon('ui_73_16_37')
        displayName = chat.GetDisplayName(self.channelID)
        self.container.hint = '<b>%s</b><br>%s' % (displayName, mls.UI_FLEET_MUTED_IN_CHANNEL)



    def SetSpeakingIndicator(self, incomingVoice):
        if incomingVoice:
            self.sr.icon.LoadIcon('ui_73_16_34')
        else:
            self.sr.icon.LoadIcon('ui_73_16_33')



    def GetChannelNotSetHint(self):
        channelType = {'fleet': mls.UI_FLEET_FLEET,
         'wing': mls.UI_FLEET_WING,
         'squad': mls.UI_FLEET_SQUAD,
         'op1': mls.UI_FLEET_OPTIONAL_CHANNEL,
         'op2': mls.UI_FLEET_OPTIONAL_CHANNEL}[self.name]
        hint = '<b>%s</b><br>%s' % (channelType, mls.UI_FLEET_CHANNEL_NOT_SET)
        return hint




class WatchListPanel(form.ActionPanel):
    __guid__ = 'form.WatchListPanel'
    __notifyevents__ = ['OnSpeakingEvent',
     'OnFleetFavoriteAdded',
     'OnFleetFavoriteRemoved',
     'OnFleetMemberChanged_Local',
     'DoBallsAdded',
     'DoBallRemove',
     'OnVoiceSpeakingChannelSet',
     'OnFleetBroadcast_Local',
     'OnInstantVoiceChannelReady',
     'OnInstantVoiceChannelFailed',
     'OnVoiceChannelLeft',
     'OnMyFleetInfoChanged']
    __dependencies__ = ['vivox', 'fleet']

    def IsFavorite(self, charid):
        return charid in sm.GetService('fleet').GetFavorites()



    def AddBroadcastIcon(self, charid, icon, hint):
        if not self.IsFavorite(charid):
            return 
        self.broadcasts[charid] = util.KeyVal(icon=icon, hint=hint, timestamp=blue.os.GetTime())
        self.UpdateAll()



    def OnFleetBroadcast_Local(self, broadcast):
        if broadcast.name not in fleetbr.types:
            icon = 'ui_38_16_70'
        else:
            icon = fleetbr.types[broadcast.name]['smallIcon']
        self.AddBroadcastIcon(broadcast.charID, icon, broadcast.broadcastName)
        caption = fleetbr.GetCaption(broadcast.charID, broadcast.broadcastName, broadcast.broadcastExtra)
        caption = '<b>%s</b>' % caption



    def OnVoiceSpeakingChannelSet(self, channelID, oldChannelID):
        if self.destroyed:
            return 
        if sm.GetService('vivox').GetInstantVoiceParticipant() is not None:
            self.UpdateAll()



    def OnInstantVoiceChannelReady(self):
        self.UpdateAll()



    def OnInstantVoiceChannelFailed(self):
        self.UpdateAll()



    def OnVoiceChannelLeft(self, channelName):
        if type(channelName) is types.TupleType and channelName[0].startswith('inst'):
            self.UpdateAll()



    def OnMyFleetInfoChanged(self):
        self.UpdateAll()



    def PostStartup(self):
        self.scope = 'all'
        self.name = 'watchlistpanel'
        self.broadcasts = {}
        self.sr.scroll = uicls.Scroll(parent=self.sr.main)
        self.SetHeaderIcon()
        self.SetMinSize((256, 50))
        hicon = self.sr.headerIcon
        hicon.GetMenu = self.GetWatchListMenu
        hicon.expandOnLeft = 1



    def GetWatchListMenu(self):
        ret = []
        if FleetSvc().IsDamageUpdates():
            ret.append((mls.UI_FLEET_TURNOFFDAMAGEUPDATES, self.SetDamageUpdates, (False,)))
        else:
            ret.append((mls.UI_FLEET_TURNONDAMAGEUPDATES, self.SetDamageUpdates, (True,)))
        return ret



    def SetDamageUpdates(self, isit):
        FleetSvc().SetDamageUpdates(isit)
        self.UpdateAll()



    def UpdateAll(self):
        self.sr.scroll.Clear()
        favorites = sm.GetService('fleet').GetFavorites()
        entries = []
        for charID in favorites:
            data = self.GetEntryData(charID)
            if data is not None:
                entries.append(listentry.Get('WatchListEntry', data=data))

        self.sr.scroll.AddEntries(-1, entries)



    def OnSpeakingEvent(self, charID, channelID, isSpeaking):
        pass



    def OnFleetFavoriteAdded(self, charID):
        self.UpdateAll()



    def OnFleetFavoriteRemoved(self, charID):
        if self.destroyed:
            return 
        self.UpdateAll()



    def OnFleetMemberChanged_Local(self, charID, *args):
        if charID in sm.GetService('fleet').GetFavorites():
            self.UpdateAll()



    def DoBallsAdded(self, lst):
        for (ball, slimItem,) in lst:
            if ball.id < destiny.DSTLOCALBALLS:
                return 
            if slimItem.charID in sm.GetService('fleet').GetFavorites():
                member = self.GetEntryData(slimItem.charID)
                self.UpdateAll()




    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem is None:
            return 
        if getattr(slimItem, 'charID', None) in sm.GetService('fleet').GetFavorites():
            member = self.GetEntryData(slimItem.charID)
            self.UpdateAll()



    def GetEntryData(self, charID):
        slimItem = util.SlimItemFromCharID(charID)
        data = util.KeyVal()
        member = sm.GetService('fleet').GetMemberInfo(charID)
        if not member:
            return 
        data.charRec = cfg.eveowners.Get(charID)
        data.itemID = data.id = data.charID = charID
        data.typeID = data.charRec.typeID
        data.squadID = member.squadID
        data.wingID = member.wingID
        data.displayName = member.charName
        data.roleString = member.roleName
        data.hint = '<b>' + mls.UI_FLEET_ROLE + ':</b>' + data.roleString + '<br>'
        data.voiceStatus = CHANNELSTATE_NONE
        data.channelName = None
        if sm.GetService('vivox').GetInstantVoiceParticipant() == charID:
            channelNameMine = ('inst', session.charid)
            channelNameOther = ('inst', charID)
            if sm.GetService('vivox').IsVoiceChannel(channelNameMine):
                data.channelName = channelNameMine
            elif sm.GetService('vivox').IsVoiceChannel(channelNameOther):
                data.channelName = channelNameOther
            data.voiceStatus = [CHANNELSTATE_MAYSPEAK, CHANNELSTATE_SPEAKING][(sm.GetService('vivox').GetSpeakingChannel() == data.channelName)]
        if member.job:
            data.hint += '<b>' + mls.UI_FLEET_JOB + ':</b>' + member.jobName + '<br>'
        if member.booster:
            data.hint += '<b>' + mls.UI_FLEET_BOOSTER + ':</b>' + member.boosterName + '<br>'
        data.label = data.displayName
        data.member = member
        data.slimItem = None
        if charID in self.broadcasts:
            data.icon = self.broadcasts[charID].icon
            data.hint += '<b>%s %s:</b>%s (%s)<br>' % (mls.UI_GENERIC_LAST,
             mls.UI_FLEET_BROADCAST,
             self.broadcasts[charID].hint,
             util.FmtDate(self.broadcasts[charID].timestamp, 'ns'))
        else:
            data.icon = None
        if slimItem:
            data.slimItem = _weakref.ref(slimItem)
        return data




class WatchListEntry(listentry.BaseTacticalEntry):
    __guid__ = 'listentry.WatchListEntry'
    __notifyevents__ = ['OnSpeakingEvent']

    def Startup(self, *args, **kw):
        listentry.BaseTacticalEntry.Startup(self, *args, **kw)
        idx = self.sr.label.parent.children.index(self.sr.label)
        instaSpeakContainer = uicls.Container(name='instaSpeakContainer', parent=self, width=20, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.instaSpeakContainer = instaSpeakContainer
        uicls.Line(parent=self, align=uiconst.TOLEFT)
        gaugesContainer = uicls.Container(name='gaugesContainer', parent=self, width=85, align=uiconst.TORIGHT)
        self.sr.gaugesContainer = gaugesContainer
        uicls.Line(parent=self, align=uiconst.TORIGHT)
        broadcastIconContainer = uicls.Container(name='broadcastIconContainer', parent=self, align=uiconst.TORIGHT)
        self.broadcastIconContainer = broadcastIconContainer
        self.voiceStatus = CHANNELSTATE_NONE
        self.isSpeaking = False
        progress = uicls.AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPLEFT, parent=self, pos=(2, 0, 16, 16))
        progress.state = uiconst.UI_HIDDEN
        self.sr.progress = progress



    def OnInstaSpeakClicked(self, btn, *args):
        if self.voiceStatus == CHANNELSTATE_NONE:
            self.InstantVoice()
        elif self.voiceStatus == CHANNELSTATE_MAYSPEAK:
            sm.GetService('vivox').SetSpeakingChannel(self.sr.node.channelName)
        else:
            sm.GetService('vivox').LeaveInstantChannel()



    def OnSpeakingEvent(self, charID, channelID, isSpeaking):
        if int(charID) == session.charid and type(channelID) is types.TupleType and channelID[0].startswith('inst'):
            instant = sm.GetService('vivox').GetInstantVoiceParticipant()
            if hasattr(self, 'sr') and instant == self.sr.node.itemID:
                icon = ['ui_73_16_33', 'ui_73_16_34'][isSpeaking]
                if self.isSpeaking or isSpeaking:
                    self.instaSpeakButton.LoadIcon(icon)
                self.isSpeaking = isSpeaking



    def Load(self, node):
        listentry.Generic.Load(self, node)
        data = node
        self.sr.label.left = 25
        self.UpdateDamage()
        (selected,) = sm.GetService('state').GetStates(data.itemID, [state.selected])
        fleetSvc = sm.GetService('fleet')
        self.Select(selected)
        if node.icon is None:
            if self.sr.Get('icon'):
                self.sr.icon.state = uiconst.UI_HIDDEN
        else:
            self.sr.icon = uicls.Icon(icon=node.icon, parent=self.broadcastIconContainer, pos=(1, 1, 16, 16), align=uiconst.TOPRIGHT)
            self.sr.icon.state = uiconst.UI_DISABLED
        icon = 'ui_73_16_36'
        hint = mls.UI_FLEET_OPENPRIVATEVOICECHANNEL
        self.voiceStatus = data.voiceStatus
        if data.voiceStatus == CHANNELSTATE_SPEAKING:
            icon = 'ui_73_16_33'
            hint = mls.UI_FLEET_LEAVEPRIVATEVOICECHANNEL
        elif data.voiceStatus == CHANNELSTATE_MAYSPEAK:
            icon = 'ui_73_16_35'
            hint = mls.UI_FLEET_SET_AS_SPEAKING_CHANNEL
        self.instaSpeakButton = uicls.Icon(icon=icon, parent=self.instaSpeakContainer, size=16, align=uiconst.RELATIVE)
        charID = self.sr.node.charID
        instant = sm.GetService('vivox').GetInstantVoiceParticipant()
        isSubordinate = fleetSvc.IsMySubordinate(charID)
        if instant is None and isSubordinate:
            self.instaSpeakContainer.OnMouseDown = self.OnInstaSpeakClicked
            self.instaSpeakButton.state = uiconst.UI_DISABLED
            self.instaSpeakContainer.hint = hint
        elif instant and charID == instant:
            self.instaSpeakButton.LoadIcon('ui_73_16_33')
        else:
            self.instaSpeakButton.state = uiconst.UI_HIDDEN



    def UpdateDamage(self):
        if not sm.GetService('fleet').IsDamageUpdates():
            self.HideDamageDisplay()
            return False
        if listentry.BaseTacticalEntry.UpdateDamage(self):
            i = 0
            startCol = (self.sr.label.color.r, self.sr.label.color.g, self.sr.label.color.b)
            while i < 10:
                fadeToCol = (1.0, 0.2, 0.2)
                c = startCol
                if not self or self.destroyed:
                    return 
                if (self.sr.label.color.r, self.sr.label.color.g, self.sr.label.color.b) == startCol:
                    c = fadeToCol
                    fadeToCol = startCol
                sm.GetService('ui').FadeRGB(fadeToCol, c, self.sr.label, time=500.0)
                i += 1




    def GetShipID(self):
        if not self.sr.node:
            return 
        else:
            known = self.sr.node.Get('slimItemID', None)
            if known:
                return known
            item = util.SlimItemFromCharID(self.sr.node.charID)
            if item is None:
                return 
            self.sr.node.slimItemID = item.itemID
            return item.itemID



    def GetHeight(_self, *args):
        (node, width,) = args
        node.height = uix.GetTextHeight(node.label, autoWidth=1, singleLine=1) + 4
        return node.height



    def OnClick(self, *args):
        if not uicore.uilib.Key(uiconst.VK_CONTROL):
            return 
        item = util.SlimItemFromCharID(self.sr.node.charID)
        if item:
            sm.GetService('target').TryLockTarget(item.itemID)



    def GetMenu(self):
        charID = self.sr.node.charID
        shipItem = util.SlimItemFromCharID(charID)
        if shipItem is None:
            ret = []
        else:
            ret = [ entry for entry in sm.GetService('menu').CelestialMenu(shipItem.itemID) if entry if entry[0] in (mls.UI_CMD_LOCKTARGET,
             mls.UI_CMD_APPROACH,
             mls.UI_CMD_ORBIT,
             mls.UI_CMD_KEEPATRANGE) ]
            ret.append(None)
        ret += sm.GetService('menu').FleetMenu(charID, unparsed=False)
        instant = sm.GetService('vivox').GetInstantVoiceParticipant()
        member = sm.GetService('fleet').GetMemberInfo(charID)
        isSubordinate = False
        if session.fleetrole == const.fleetRoleLeader or session.fleetrole == const.fleetRoleWingCmdr and member.wingID == session.wingid or session.fleetrole == const.fleetRoleSquadCmdr and member.squadID == session.squadid:
            isSubordinate = True
        if instant is None and isSubordinate:
            ret.append((mls.UI_FLEET_OPENPRIVATEVOICECHANNEL, self.InstantVoice))
        elif instant == charID or instant == session.charid:
            ret.append((mls.UI_FLEET_LEAVEPRIVATEVOICECHANNEL, sm.GetService('vivox').LeaveInstantChannel))
        return ret



    def InstantVoice(self):
        sm.GetService('vivox').InstantVoice(self.sr.node.charID)
        self.sr.progress.state = uiconst.UI_NORMAL
        self.sr.progress.Play()
        self.instaSpeakButton.state = uiconst.UI_HIDDEN
        self.instaSpeakContainer.hint = mls.UI_FLEET_CONNECTINGOTHERUSER



    def InitGauges(self):
        parent = self.sr.gaugesContainer
        if getattr(self, 'gaugesInited', False):
            self.sr.gaugeParent.state = uiconst.UI_DISABLED
            return 
        (barw, barh,) = (24, 6)
        borderw = 2
        barsw = (barw + borderw) * 3 + borderw
        par = uicls.Container(name='gauges', parent=parent, align=uiconst.TORIGHT, width=barsw + 2, height=0, left=0, top=0, idx=0)
        self.sr.gauges = []
        l = 2
        for each in ('SHIELD', 'ARMOR', 'STRUCT'):
            g = uicls.Container(name=each, align=uiconst.CENTERLEFT, width=barw, height=barh, left=l)
            g.name = 'gauge_%s' % each.lower()
            uicls.Frame(parent=g)
            g.sr.bar = uicls.Fill(parent=g, align=uiconst.TOLEFT)
            uicls.Fill(parent=g, color=(158 / 256.0,
             11 / 256.0,
             14 / 256.0,
             1.0))
            par.children.append(g)
            self.sr.gauges.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)
            l += barw + borderw

        self.sr.gaugeParent = par
        self.gaugesInited = True




