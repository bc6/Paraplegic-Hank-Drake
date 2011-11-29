import service
import blue
import uthread
import uix
import uiutil
import xtriui
import operator
import util
import base
import form
import listentry
import state
import types
from itertools import starmap
import standingUtil
import log
import uicls
import uiconst
import localization

class Standing(service.Service):
    __exportedcalls__ = {'GetTransactionWnd': [],
     'GetCompositionWnd': [],
     'GetStandingEntries': [],
     'GetStandingEntry': [],
     'GetMySecurityRating': []}
    __notifyevents__ = ['OnStandingSet', 'OnStandingsModified', 'ProcessSessionChange']
    __guid__ = 'svc.standing'
    __servicename__ = 'standing'
    __displayname__ = 'Standing Service'

    def __init__(self):
        service.Service.__init__(self)
        self.gotten = 0
        (self.npccorpstandings, self.npccharstandings, self.npcnpcstandingsto, self.npcnpcstandingsfrom,) = ({},
         {},
         {},
         {})
        self.toStandingHeader = blue.DBRowDescriptor((('toID', const.DBTYPE_I4), ('standing', const.DBTYPE_R5)))
        self.fromStandingHeader = blue.DBRowDescriptor((('fromID', const.DBTYPE_I4), ('standing', const.DBTYPE_R5)))



    def OnStandingSet(self, fromID, toID, standing):
        if util.IsNPC(fromID):
            if toID == eve.session.charid:
                if not standing:
                    if fromID in self.npccharstandings:
                        if session.warfactionid:
                            sm.ScatterEvent('OnNPCStandingChange', fromID, 0.0, self.npccharstandings[fromID].standing)
                        del self.npccharstandings[fromID]
                else:
                    oldStanding = 0.0
                    if fromID in self.npccharstandings:
                        oldStanding = self.npccharstandings[fromID].standing
                    if session.warfactionid:
                        sm.ScatterEvent('OnNPCStandingChange', fromID, standing, oldStanding)
                    self.npccharstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, standing])
            elif toID == eve.session.corpid:
                if not standing:
                    if fromID in self.npccorpstandings:
                        del self.npccorpstandings[fromID]
                else:
                    self.npccorpstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, standing])



    def OnStandingsModified(self, modifications):
        for modification in modifications:
            (fromID, toID, m, minAbs, maxAbs,) = modification
            (minAbs, maxAbs,) = (minAbs * 10.0, maxAbs * 10.0)
            if toID == eve.session.charid:
                if fromID in self.npccharstandings:
                    newval = self.npccharstandings[fromID].standing
                    if m > 0.0:
                        if self.npccharstandings[fromID].standing < maxAbs:
                            newval = min(maxAbs, 10.0 * (1.0 - (1.0 - self.npccharstandings[fromID].standing / 10.0) * (1.0 - m)))
                    elif self.npccharstandings[fromID].standing > minAbs:
                        newval = max(minAbs, 10.0 * (self.npccharstandings[fromID].standing / 10.0 + (1.0 + self.npccharstandings[fromID].standing / 10.0) * m))
                    if session.warfactionid:
                        sm.ScatterEvent('OnNPCStandingChange', fromID, newval, self.npccharstandings[fromID].standing)
                    self.npccharstandings[fromID].standing = newval
                else:
                    newval = max(min(10.0 * m, maxAbs), minAbs)
                    self.npccharstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, newval])
            elif toID == eve.session.corpid:
                if fromID in self.npccorpstandings:
                    newval = self.npccorpstandings[fromID].standing
                    if m > 0.0:
                        if self.npccorpstandings[fromID].standing < maxAbs:
                            newval = min(maxAbs, 10.0 * (1.0 - (1.0 - self.npccorpstandings[fromID].standing / 10.0) * (1.0 - m)))
                    elif self.npccorpstandings[fromID].standing > minAbs:
                        newval = max(minAbs, 10.0 * (self.npccorpstandings[fromID].standing / 10.0 + (1.0 + self.npccharstandings[fromID].standing / 10.0) * m))
                    self.npccorpstandings[fromID].standing = newval
                else:
                    newval = max(min(10.0 * m, maxAbs), minAbs)
                    self.npccorpstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, newval])




    def Run(self, memStream = None):
        self._Standing__RefreshStandings()



    def Stop(self, memStream = None):
        pass



    def CanUseAgent(self, factionID, corporationID, agentID, level, agentTypeID):
        self._Standing__Init()
        if factionID in self.npccharstandings:
            fac = self.npccharstandings[factionID].standing
        else:
            fac = 0.0
        if corporationID in self.npccharstandings:
            coc = self.npccharstandings[corporationID].standing
        else:
            coc = 0.0
        if agentID in self.npccharstandings:
            cac = self.npccharstandings[agentID].standing
        else:
            cac = 0.0
        return util.CanUseAgent(level, agentTypeID, fac, coc, cac, corporationID, factionID, {})



    def GetMySecurityRating(self):
        self._Standing__Init()
        if const.ownerCONCORD in self.npccharstandings:
            return self.npccharstandings[const.ownerCONCORD].standing
        return 0.0



    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change and change['charid'][1] or 'corpid' in change and change['corpid'][1]:
            self._Standing__RefreshStandings()



    def __Init(self):
        for i in range(120):
            if self.gotten:
                break
            self.LogInfo('Waiting while acquiring standings')
            blue.pyos.synchro.SleepWallclock(1000)




    def __RefreshStandings(self):
        if not eve.session.charid:
            return 
        tmp = sm.RemoteSvc('standing2').GetNPCNPCStandings()
        self.npcnpcstandingsto = tmp.Filter('toID')
        self.npcnpcstandingsfrom = tmp.Filter('fromID')
        if util.IsNPC(eve.session.corpid):
            self.npccharstandings = sm.RemoteSvc('standing2').GetCharStandings()
            self.npccorpstandings = {}
        else:
            ret = uthread.parallel([(sm.RemoteSvc('standing2').GetCharStandings, ()), (sm.RemoteSvc('standing2').GetCorpStandings, ())])
            self.npccharstandings = ret[0]
            self.npccorpstandings = ret[1]
        if type(self.npccorpstandings) != types.DictType:
            self.npccorpstandings = self.npccorpstandings.Index('fromID')
        self.npccharstandings = self.npccharstandings.Index('fromID')
        self.gotten = 1



    def GetStanding(self, fromID, toID):
        self._Standing__Init()
        relationship = None
        standing = None
        if fromID == eve.session.charid:
            relationship = sm.GetService('addressbook').GetContacts().contacts.get(toID, None)
        elif fromID == eve.session.corpid and not util.IsNPC(eve.session.corpid):
            relationship = sm.GetService('addressbook').GetContacts().corpContacts.get(toID, None)
        elif fromID == eve.session.allianceid:
            relationship = sm.GetService('addressbook').GetContacts().allianceContacts.get(toID, None)
        elif toID == eve.session.charid:
            if util.IsNPC(fromID) and fromID in self.npccharstandings:
                standing = self.npccharstandings[fromID]
        elif toID == eve.session.corpid and not util.IsNPC(eve.session.corpid):
            if util.IsNPC(fromID) and fromID in self.npccorpstandings:
                standing = self.npccorpstandings[fromID]
        elif util.IsNPC(fromID) and util.IsNPC(toID) and fromID in self.npcnpcstandingsfrom:
            for each in self.npcnpcstandingsfrom[fromID]:
                if each.toID == toID:
                    standing = each
                    break

        if standing is not None:
            ret = standing.standing
        elif relationship is not None:
            ret = relationship.relationshipID
        else:
            ret = const.contactNeutralStanding
        return ret



    def GetEffectiveStanding(self, fromID, toID):
        standing = self.GetStanding(fromID, toID) or 0.0
        bonus = None
        if toID == eve.session.charid and util.IsNPC(fromID):
            bonus = ('', 0.0)
            char = sm.GetService('godma').GetItem(eve.session.charid)
            if util.IsCorporation(fromID):
                fromFactionID = sm.GetService('faction').GetFaction(fromID)
            elif util.IsFaction(fromID):
                fromFactionID = fromID
            else:
                agent = sm.GetService('agents').GetAgentByID(fromID)
                fromFactionID = agent.factionID
            relevantSkills = {}
            for skillTypeID in (const.typeDiplomacy, const.typeConnections, const.typeCriminalConnections):
                skill = char.skills.get(skillTypeID, None)
                if skill is not None:
                    relevantSkills[skillTypeID] = skill.skillLevel

            bonus = standingUtil.GetStandingBonus(standing, fromFactionID, relevantSkills)
        if bonus is None or bonus[1] <= 0.0:
            bonus = ''
        else:
            effective = (1.0 - (1.0 - standing / 10.0) * (1.0 - bonus[1] / 10.0)) * 10.0
            bonus = localization.GetByLabel('UI/Standings/Common/BonusAdded', bonus=bonus[0], value=standing)
            standing = effective
        return (standing, bonus)



    def GetStandingEntry(self, ownerID, fromID, toID, standing, showBonuses = 1, label = None):
        self._Standing__Init()
        bonus = None
        bonusType = None
        relevantSkills = {}
        if showBonuses:
            if toID == eve.session.charid and util.IsNPC(fromID):
                bonus = ('', 0.0)
                char = sm.GetService('godma').GetItem(eve.session.charid)
                if util.IsCorporation(fromID):
                    fromFactionID = sm.GetService('faction').GetFaction(fromID)
                elif util.IsFaction(fromID):
                    fromFactionID = fromID
                else:
                    agent = sm.GetService('agents').GetAgentByID(fromID)
                    if agent is None:
                        fromFactionID = None
                    else:
                        fromFactionID = agent.factionID
                for skillTypeID in (const.typeDiplomacy, const.typeConnections, const.typeCriminalConnections):
                    skill = char.skills.get(skillTypeID, None)
                    if skill is not None:
                        relevantSkills[skillTypeID] = skill.skillLevel

                (bonusType, bonus,) = standingUtil.GetStandingBonus(standing, fromFactionID, relevantSkills)
        if bonusType is None or bonus <= 0.0:
            bonus = ''
        else:
            effective = (1.0 - (1.0 - standing / 10.0) * (1.0 - bonus / 10.0)) * 10.0
            bonusString = localization.GetByLabel('UI/Common/Unknown')
            if bonusType == const.typeDiplomacy:
                bonusString = localization.GetByLabel('UI/Standings/Common/DiplomacySkill', value=relevantSkills[bonusType])
            elif bonusType == const.typeConnections:
                bonusString = localization.GetByLabel('UI/Standings/Common/ConnectionsSkill', value=relevantSkills[bonusType])
            elif bonusType == const.typeCriminalConnections:
                bonusString = localization.GetByLabel('UI/Standings/Common/CriminalConnectionsSkill', value=relevantSkills[bonusType])
            bonus = localization.GetByLabel('UI/Standings/Common/BonusAdded', bonus=bonusString, value=standing)
            standing = effective
        ownerinfo = cfg.eveowners.Get(ownerID)
        data = {}
        if label is None:
            label = ownerinfo.name
        if standing == 0.0:
            col = '<color=grey>'
        else:
            col = ''
        data['label'] = localization.GetByLabel('UI/Standings/StandingEntry', color=col, label=label, standing=standing, bonus=bonus, standingText=uix.GetStanding(round(standing, 0), 1))
        data['ownerInfo'] = ownerinfo
        data['fromID'] = fromID
        data['toID'] = toID
        data['effective'] = standing
        return listentry.Get('StandingEntry', data)



    def GetStandingRelationshipEntries(self, whoID):
        fromFactionID = sm.GetService('faction').GetFaction(eve.session.corpid)
        fromCorpID = eve.session.corpid
        fromCharID = eve.session.charid
        toAllianceID = None
        if util.IsFaction(whoID):
            toFactionID = whoID
            toCorpID = None
            toCharID = None
        elif util.IsCorporation(whoID):
            toFactionID = sm.GetService('faction').GetFaction(whoID)
            toCorpID = whoID
            toCharID = None
            if not util.IsNPC(whoID):
                toAllianceID = sm.GetService('corp').GetCorporation(whoID).allianceID
        elif util.IsAlliance(whoID):
            toFactionID = None
            toCorpID = None
            toCharID = None
            toAllianceID = whoID
        elif util.IsNPC(whoID) and sm.GetService('agents').GetAgentByID(whoID):
            agent = sm.GetService('agents').GetAgentByID(whoID)
            toFactionID = agent.factionID
            toCorpID = agent.corporationID
            toCharID = whoID
        else:
            pubinfo = sm.RemoteSvc('charMgr').GetPublicInfo(whoID)
            toFactionID = sm.GetService('faction').GetFaction(pubinfo.corporationID)
            if not util.IsNPC(pubinfo.corporationID):
                toAllianceID = sm.GetService('corp').GetCorporation(pubinfo.corporationID).allianceID
            toCorpID = pubinfo.corporationID
            toCharID = whoID

        def GetStanding(fromID, toID):
            return self.GetStanding(fromID, toID)


        GetStanding = util.Memoized(GetStanding)

        def BogusStanding(fromID, toID):
            return None in (fromID, toID) or GetStanding(fromID, toID) is None


        standings = [ (fromID, toID, GetStanding(fromID, toID)) for fromID in [fromFactionID, fromCorpID, fromCharID] for toID in [toFactionID,
         toCorpID,
         toCharID,
         toAllianceID] if not BogusStanding(fromID, toID) ]
        if eve.session.allianceid is not None:
            remoteRels = sm.GetService('addressbook').GetContacts().allianceContacts
            for otherID in (toCorpID, toAllianceID):
                if otherID is not None and otherID in remoteRels:
                    standing = remoteRels[otherID].relationshipID
                    standings.append((eve.session.allianceid, otherID, standing))


        def GetEntry(fromID, toID, standing):
            return self.GetStandingEntry(toID, fromID, toID, standing, label='%s &gt; %s' % (cfg.eveowners.Get(fromID).name, cfg.eveowners.Get(toID).name))


        scrolllist = []
        if not util.IsNPC(whoID):
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Standings/InfoWindow/YourStandings')}))
            scrolllist.extend(starmap(GetEntry, standings))
            nonNeutralStandings = [ standing for (blah, blah, standing,) in standings if standing != 0.0 ]
            if nonNeutralStandings:
                highest = max(nonNeutralStandings)
                data = util.KeyVal()
                data.line = 1
                data.indent = 36
                data.text = localization.GetByLabel('UI/Standings/Common/DerivedStanding', highest=highest, standing=uix.GetStanding(round(highest, 0), 1))
                scrolllist.append(listentry.Get('Divider'))
                scrolllist.append(listentry.Get('Text', data=data))
                scrolllist.append(listentry.Get('Divider'))
        else:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Standings/InfoWindow/StandingsWithYou')}))
            scrolllist.extend([ GetEntry(fromID, toID, self.GetStanding(fromID, toID)) for fromID in (toFactionID, toCorpID, toCharID) for toID in (fromFactionID, fromCorpID, fromCharID) if None not in (fromID, toID) if self.GetStanding(fromID, toID) is not None ])
        if util.IsFaction(whoID):
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Standings/InfoWindow/StandingsOtherEmpires')}))
            factions = cfg.factions
            for faction in factions:
                if faction.factionID not in (whoID, const.factionUnknown):
                    toInfo = cfg.eveowners.Get(faction.factionID)
                    fromName = cfg.eveowners.Get(whoID).name
                    toName = cfg.eveowners.Get(faction.factionID).name
                    fromStanding = self.GetStanding(whoID, faction.factionID)
                    fromStandingText = uix.GetStanding(round(fromStanding, 0), 1)
                    toStanding = self.GetStanding(faction.factionID, whoID)
                    toStandingText = uix.GetStanding(round(toStanding, 0), 1)
                    fromText = localization.GetByLabel('UI/Standings/StandingRelationshipText', leftSide=fromName, rightSide=toName, standing=fromStanding, standingText=fromStandingText)
                    toText = localization.GetByLabel('UI/Standings/StandingRelationshipText', leftSide=toName, rightSide=fromName, standing=toStanding, standingText=toStandingText)
                    data = util.KeyVal()
                    data.toInfo = toInfo
                    data.label = fromText
                    data.otherlabel = toText
                    scrolllist.append(listentry.Get('FactionStandingEntry', data=data))

        return scrolllist



    def GetStandingEntries(self, positive, whoID, exclude = {}, emptyMessage = 1):
        self._Standing__Init()
        if whoID is None:
            whoID = eve.session.charid
        corpIDs = []
        standings = []
        if whoID == session.corpid:
            for npcID in self.npccorpstandings:
                if util.IsCorporation(npcID):
                    corpIDs.append(npcID)
                standings.append((npcID, self.npccorpstandings[npcID].standing))

        if whoID == eve.session.charid:
            for npcID in self.npccharstandings:
                standings.append((npcID, self.npccharstandings[npcID].standing))

        prime = []
        for each in standings:
            if each[0] not in cfg.eveowners:
                prime.append(each[0])

        if prime:
            self.LogError("Remote standings query didn't return required owner info: ", prime)
            cfg.eveowners.Prime(prime)
        cfg.corptickernames.Prime(corpIDs)
        scrolllist = []
        factions = []
        alliances = []
        corps = []
        chars = []
        agents = []
        for each in standings:
            standing = each[1]
            ownerID = each[0]
            if ownerID not in exclude:
                fromID = ownerID
                toID = whoID
                ownerinfo = cfg.eveowners.Get(ownerID)
                entry = (round(standing, 2), ownerinfo.name, self.GetStandingEntry(ownerID, fromID, toID, standing))
                standing = entry[2].effective
                if positive and standing < 0.01 or not positive and standing > -0.01:
                    continue
                if ownerinfo.groupID == const.groupFaction:
                    factions.append(entry)
                elif ownerinfo.groupID == const.groupCorporation:
                    corps.append(entry)
                elif util.IsNPC(ownerID):
                    agents.append(entry)


        def NegSortFunc(x, y):
            if x[0] < y[0]:
                return -1
            if x[0] > y[0]:
                return 1
            if x[1].lower() < y[1].lower():
                return -1
            if x[1].lower() > y[1].lower():
                return 1
            return 0



        def PosSortFunc(x, y):
            if x[0] > y[0]:
                return -1
            if x[0] < y[0]:
                return 1
            if x[1].lower() < y[1].lower():
                return -1
            if x[1].lower() > y[1].lower():
                return 1
            return 0


        if positive:
            SortFunc = PosSortFunc
        else:
            SortFunc = NegSortFunc
        factions.sort(SortFunc)
        alliances.sort(SortFunc)
        corps.sort(SortFunc)
        chars.sort(SortFunc)
        agents.sort(SortFunc)
        if factions:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Common/Factions')}))
            for each in factions:
                scrolllist.append(each[2])

        if alliances:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Common/Alliances')}))
            for each in alliances:
                scrolllist.append(each[2])

        if corps:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Common/Corporations')}))
            for each in corps:
                scrolllist.append(each[2])

        if chars:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Common/Characters')}))
            for each in chars:
                scrolllist.append(each[2])

        if agents:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/Common/Agents')}))
            for each in agents:
                scrolllist.append(each[2])

        if emptyMessage and not (factions or corps or chars or agents or alliances):
            text = ''
            name = cfg.eveowners.Get(whoID).name
            if whoID == session.charid:
                if positive:
                    text = localization.GetByLabel('UI/Standings/Common/EverybodyNegativeYou')
                else:
                    text = localization.GetByLabel('UI/Standings/Common/EverybodyPositiveYou')
            elif positive:
                if util.IsCharacter(whoID):
                    text = localization.GetByLabel('UI/Standings/Common/EverybodyNegativeCharacter', id=whoID)
                else:
                    text = localization.GetByLabel('UI/Standings/Common/EverybodyNegativeName', name=cfg.eveowners.Get(whoID).name)
            elif util.IsCharacter(whoID):
                text = localization.GetByLabel('UI/Standings/Common/EverybodyPositiveCharacter', id=whoID)
            else:
                text = localization.GetByLabel('UI/Standings/Common/EverybodyPositiveName', name=cfg.eveowners.Get(whoID).name)
            scrolllist.append(listentry.Get('Text', {'line': 1,
             'text': text}))
        return scrolllist



    def GetTransactionWnd(self, fromID, toID = None):
        self._Standing__Init()
        if fromID != toID:
            wnd = form.StandingTransactionsWnd.Open()
            wnd.Load(fromID, toID, 1, onPage=0)



    def GetCompositionWnd(self, fromID, toID):
        self._Standing__Init()
        wnd = form.StandingCompositionsWnd.Open()
        wnd.Load(fromID, toID, purge=1)




class StandingTransactionsWnd(uicls.Window):
    __guid__ = 'form.StandingTransactionsWnd'
    default_windowID = 'standingtransactions'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station_inflight'
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetCaption(localization.GetByLabel('UI/Standings/TransactionWindow/WindowTitle'))
        self.SetMinSize([342, 256])
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        eventTypes = [[localization.GetByLabel('UI/Common/All'), None]] + util.GetStandingEventTypes()
        browserParent = uicls.Container(name='browser', parent=self.sr.main, idx=0, align=uiconst.TOTOP, height=36)
        sidepar = uicls.Container(name='sidepar', parent=browserParent, align=uiconst.TORIGHT, width=54)
        btn = uix.GetBigButton(24, sidepar, 0, 12)
        btn.OnClick = (self.Browse, -1)
        btn.hint = localization.GetByLabel('UI/Common/Previous')
        btn.sr.icon.LoadIcon('ui_23_64_1')
        btn.state = uiconst.UI_HIDDEN
        self.sr.backBtn = btn
        btn = uix.GetBigButton(24, sidepar, 24, 12)
        btn.OnClick = (self.Browse, 1)
        btn.hint = localization.GetByLabel('UI/Common/ViewMore')
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.fwdBtn = btn
        self.page = 0
        inpt = uicls.SinglelineEdit(name='fromdate', parent=browserParent, setvalue=self.GetNow(), align=uiconst.TOPLEFT, pos=(8, 16, 92, 0), maxLength=16)
        uicls.EveHeaderSmall(text=localization.GetByLabel('UI/Common/Date'), parent=inpt, width=200, top=-12)
        inpt.OnReturn = self.OnReturn
        self.sr.fromdate = inpt
        i = 0
        for (optlist, label, config, defval,) in [(eventTypes,
          localization.GetByLabel('UI/Standings/TransactionWindow/EventType'),
          'eventType',
          localization.GetByLabel('UI/Common/All'))]:
            combo = uicls.Combo(label=label, parent=browserParent, options=optlist, name=config, select=settings.user.ui.Get(config, defval), callback=self.OnComboChange, pos=(inpt.left + inpt.width + 6 + i * 92,
             inpt.top,
             0,
             0), width=86, align=uiconst.TOPLEFT)
            self.sr.Set(label.replace(' ', '') + 'Combo', combo)
            i += 1




    def OnComboChange(self, entry, header, value, *args):
        if self.sr.Get('data'):
            if entry.name == 'eventType':
                self.sr.data[4] = value
                self.sr.data[0] = None
            self.page = 0
            uthread.pool('standing::OnComboChange', self.Load, self.sr.data[1], self.sr.data[2])



    def OnReturn(self, *args):
        if self.sr.Get('data'):
            self.sr.data[5] = util.ParseDate(self.sr.fromdate.GetValue())
            self.sr.data[0] = None
            uthread.pool('standing::OnReturn', self.Load, self.sr.data[1], self.sr.data[2])



    def Browse(self, direction, *args):
        if self.sr.Get('data') and self.sr.data[3]:
            if direction > 0:
                eventID = None
                for each in self.sr.data[3]:
                    eventID = each.eventID

                self.sr.data[5] = None
                self.sr.data[6] = 0
            else:
                eventID = self.sr.data[0]
                self.sr.data[5] = None
                self.sr.data[6] = 1
            self.sr.data[0] = eventID
            self.page += direction
            uthread.pool('standing::Browse', self.Load, self.sr.data[1], self.sr.data[2])



    def GetNow(self):
        return util.FmtDate(blue.os.GetWallclockTime(), 'sn')



    def Load(self, fromID, toID, purge = 0, onPage = None):
        if getattr(self, 'loading', 0):
            return 
        self.loading = 1
        if onPage is not None:
            self.page = onPage
        try:
            self.sr.scroll.Clear()
            if fromID and toID:
                if util.IsCharacter(fromID) and util.IsCharacter(toID):
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCharacterToCharacter', fromID=fromID, toID=toID)
                elif util.IsCharacter(fromID):
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCharacterToCorp', fromID=fromID, toName=cfg.eveowners.Get(toID).name)
                elif util.IsCharacter(toID):
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCorpToCharacter', fromName=cfg.eveowners.Get(fromID).name, toID=toID)
                else:
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCorpToCorp', fromName=cfg.eveowners.Get(fromID).name, toName=cfg.eveowners.Get(toID).name)
            elif fromID:
                if util.IsCharacter(fromID):
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCharacterToAny', fromID=fromID)
                else:
                    standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCorpToAny', fromName=cfg.eveowners.Get(fromID).name)
            elif util.IsCharacter(toID):
                standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromAnyToCharacter', toID=toID)
            else:
                standing = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromAnyToCorp', toName=cfg.eveowners.Get(toID).name)
            self.SetCaption(standing)
            scrolllist = []
            if not self.sr.Get('data') or purge:
                self.sr.data = [None,
                 None,
                 None,
                 [],
                 None,
                 None,
                 1]
            eventType = self.sr.data[4]
            eventID = self.sr.data[0]
            eventDateTime = self.sr.data[5]
            direction = self.sr.data[6]
            if eventDateTime is not None:
                if direction == 1:
                    eventDateTime += HOUR * 23 + MIN * 59 + SEC * 59
            data = sm.RemoteSvc('standing2').GetStandingTransactions(fromID, toID, direction, eventID, eventType, eventDateTime)
            self.sr.data = [eventID,
             fromID,
             toID,
             data,
             eventType,
             eventDateTime,
             direction]
            if self.page > 0:
                self.sr.backBtn.state = uiconst.UI_NORMAL
            else:
                self.sr.backBtn.state = uiconst.UI_HIDDEN
            if self.sr.data[3]:
                self.sr.data[0] = self.sr.data[3][0].eventID
                if len(self.sr.data[3]) < 25:
                    self.sr.fwdBtn.state = uiconst.UI_HIDDEN
                else:
                    self.sr.fwdBtn.state = uiconst.UI_NORMAL
            else:
                self.sr.fwdBtn.state = uiconst.UI_HIDDEN
            if self.sr.data[3]:
                for each in self.sr.data[3]:
                    (subject, body,) = util.FmtStandingTransaction(each)
                    when = util.FmtDate(each.eventDateTime, 'ls')
                    mod = '%-2.4f' % (each.modification * 100.0)
                    while mod and mod[-1] == '0':
                        if mod[-2:] == '.0':
                            break
                        mod = mod[:-1]

                    if fromID is None:
                        extraFrom = cfg.eveowners.Get(each.fromID).name + '<t>'
                    else:
                        extraFrom = ''
                    if toID is None:
                        extraTo = cfg.eveowners.Get(each.toID).name + '<t>'
                    else:
                        extraTo = ''
                    text = '%s<t>%s<t>%s%s%s %%<t>%s' % (each.eventID,
                     when,
                     extraFrom,
                     extraTo,
                     mod,
                     subject)
                    scrolllist.append(listentry.Get('StandingTransaction', {'line': 1,
                     'text': text,
                     'details': body}))

            else:
                scrolllist.append(listentry.Get('Text', {'line': 1,
                 'text': localization.GetByLabel('UI/Standings/TransactionWindow/NoTransactions')}))
            h = [localization.GetByLabel('UI/Common/ID'), localization.GetByLabel('UI/Common/Date')]
            if fromID is None:
                h += [localization.GetByLabel('UI/Common/From')]
            if toID is None:
                h += [localization.GetByLabel('UI/Common/To')]
            h += [localization.GetByLabel('UI/Common/Value'), localization.GetByLabel('UI/Common/Reason')]
            self.sr.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, headers=h, reversesort=1, sortby=localization.GetByLabel('UI/Common/ID'))

        finally:
            self.loading = 0





class StandingTransaction(listentry.Text):
    __guid__ = 'listentry.StandingTransaction'
    __params__ = ['text', 'details']

    def Load(self, node):
        listentry.Text.Load(self, node)
        self.sr.details = node.details



    def GetMenu(self):
        details = self.sr.details
        return [(localization.GetByLabel('UI/Common/Details'), self.ShowTransactionDetails, (details,))]



    def OnDblClick(self, *args):
        self.ShowTransactionDetails()



    def ShowTransactionDetails(self, details = None, *args):
        details = details if details != None else self.sr.details
        uix.TextBox(localization.GetByLabel('UI/Standings/TransactionWindow/Details'), details)




class StandingEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.StandingEntry'

    def Startup(self, *etc):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=36, top=0, state=uiconst.UI_DISABLED, color=None, singleline=1, align=uiconst.CENTERLEFT)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.iconParent = uicls.Container(parent=self, left=1, top=0, width=32, height=32, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=0, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.text = data.label
        self.sr.iconParent.Flush()
        logo = None
        typeInfo = cfg.invtypes.Get(data.ownerInfo.typeID)
        iconParams = {'parent': self.sr.iconParent,
         'align': uiconst.TOALL,
         'state': uiconst.UI_DISABLED,
         'idx': 0}
        if typeInfo.groupID in (const.groupCorporation, const.groupFaction, const.groupAlliance):
            logo = uiutil.GetLogoIcon(itemID=data.ownerInfo.ownerID, **iconParams)
        elif typeInfo.groupID == const.groupCharacter:
            logo = uicls.Icon(icon=None, **iconParams)
            sm.GetService('photo').GetPortrait(data.ownerInfo.ownerID, 64, logo)
        self.sr.label.left = 36



    def OnDblClick(self, *args):
        self.ShowTransactions(self.sr.node)



    def ShowTransactions(self, node):
        node = node if node != None else self.sr.node
        sm.GetService('standing').GetTransactionWnd(node.fromID, node.toID)



    def ShowCompositions(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('standing').GetCompositionWnd(node.fromID, node.toID)



    def EditStandings(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('standing').GetEditWnd(eve.session.charid, node.toID)



    def ResetStandings(self, node = None):
        node = node if node != None else self.sr.node
        if eve.Message('StandingsConfirmReset', {'who': cfg.eveowners.Get(node.toID).name}, uix.YESNO, suppress=uix.ID_YES) == uix.ID_YES:
            sm.GetService('standing').ResetStandings(eve.session.charid, node.toID)



    def EditCorpStandings(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('standing').GetEditWnd(eve.session.corpid, node.toID)



    def ResetCorpStandings(self, node = None):
        node = node if node != None else self.sr.node
        if eve.Message('StandingsConfirmResetCorp', {'who': cfg.eveowners.Get(node.toID).name}, uix.YESNO, suppress=uix.ID_YES) == uix.ID_YES:
            sm.GetService('standing').ResetStandings(eve.session.corpid, node.toID)



    def ShowInfo(self, node = None, *args):
        if self.sr.node.Get('ownerInfo', None):
            sm.GetService('info').ShowInfo(self.sr.node.ownerInfo.typeID, self.sr.node.ownerInfo.ownerID)



    def GetMenu(self):
        m = []
        node = self.sr.node
        addressBookSvc = sm.GetService('addressbook')
        m.append((localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowInfo, (node,)))
        if self.sr.node.toID != self.sr.node.fromID:
            if util.IsNPC(self.sr.node.fromID) and self.sr.node.toID == eve.session.corpid:
                m.append((localization.GetByLabel('UI/Commands/ShowCompositions'), self.ShowCompositions, (node,)))
            elif self.sr.node.fromID in (eve.session.charid, eve.session.corpid) or util.IsNPC(self.sr.node.fromID) and self.sr.node.toID == eve.session.charid:
                m.append((localization.GetByLabel('UI/Commands/ShowTransactions'), self.ShowTransactions, (node,)))
        if self.sr.node.fromID == eve.session.charid:
            if self.sr.node.toID != self.sr.node.fromID:
                if addressBookSvc.IsInAddressBook(self.sr.node.toID, 'contact'):
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/EditContact'), addressBookSvc.AddToPersonalMulti, (self.sr.node.toID, 'contact', True)))
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/RemoveContact'), addressBookSvc.DeleteEntryMulti, ([self.sr.node.toID], 'contact')))
                else:
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, (self.sr.node.toID, 'contact')))
        if self.sr.node.fromID == eve.session.corpid and const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector:
            if self.sr.node.toID != self.sr.node.fromID and not util.IsNPC(self.sr.node.fromID):
                if addressBookSvc.IsInAddressBook(self.sr.node.toID, 'corpcontact'):
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/EditCorpContact'), addressBookSvc.AddToPersonalMulti, (self.sr.node.toID, 'corpcontact', True)))
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/RemoveCorpContact'), addressBookSvc.DeleteEntryMulti, ([self.sr.node.toID], 'corpcontact')))
                else:
                    m.append((localization.GetByLabel('UI/PeopleAndPlaces/AddContact'), addressBookSvc.AddToPersonalMulti, (self.sr.node.toID, 'corpcontact')))
        return m



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height




class FactionStandingEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.FactionStandingEntry'

    def Startup(self, *etc):
        self.sr.label = uicls.EveLabelMedium(text='', parent=self, left=36, top=0, state=uiconst.UI_DISABLED, singleline=1, align=uiconst.TOPLEFT)
        self.sr.otherlabel = uicls.EveLabelMedium(text='', parent=self, left=36, top=0, state=uiconst.UI_DISABLED, singleline=1, align=uiconst.BOTTOMLEFT)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.iconParent = uicls.Container(parent=self, pos=(1, 0, 32, 32), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        self.sr.infoicon = uicls.InfoIcon(size=16, left=0, top=2, parent=self, idx=0, align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo



    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.text = data.label
        self.sr.otherlabel.text = data.otherlabel
        toInfo = data.toInfo
        self.sr.iconParent.Flush()
        logo = None
        typeInfo = cfg.invtypes.Get(toInfo.typeID)
        iconParams = {'parent': self.sr.iconParent,
         'align': uiconst.TOALL,
         'state': uiconst.UI_DISABLED,
         'idx': 0}
        logo = uiutil.GetLogoIcon(itemID=toInfo.ownerID, **iconParams)
        self.sr.label.left = 36



    def ShowInfo(self, node = None, *args):
        toInfo = cfg.eveowners.Get(self.sr.node.toInfo)
        sm.GetService('info').ShowInfo(toInfo.typeID, toInfo.ownerID)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height




class StandingCompositionsWnd(uicls.Window):
    __guid__ = 'form.StandingCompositionsWnd'
    default_windowID = 'standingcompositions'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station_inflight'
        self.SetCaption(localization.GetByLabel('UI/Standings/CompositionWindow/WindowTitle'))
        self.SetMinSize([342, 256])
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        textParent = uicls.Container(name='text', parent=self.sr.main, idx=0, align=uiconst.TOTOP, height=72)
        self.sr.helpNote = uicls.EveLabelMedium(text=localization.GetByLabel('UI/Standings/CompositionWindow/NPCToPlayerCorp'), parent=textParent, align=uiconst.TOTOP, left=6, top=3, state=uiconst.UI_NORMAL)



    def Load(self, fromID, toID, purge = 0):
        if getattr(self, 'loading', 0):
            return 
        self.loading = 1
        try:
            self.sr.scroll.Clear()
            if util.IsCharacter(fromID) and util.IsCharacter(toID):
                caption = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCharacterToCharacter', fromID=fromID, toID=toID)
            elif util.IsCharacter(fromID):
                caption = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCharacterToCorp', fromID=fromID, toName=cfg.eveowners.Get(toID).name)
            elif util.IsCharacter(toID):
                caption = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCorpToCharacter', fromName=cfg.eveowners.Get(fromID).name, toID=toID)
            else:
                caption = localization.GetByLabel('UI/Standings/TransactionWindow/TitleFromCorpToCorp', fromName=cfg.eveowners.Get(fromID).name, toName=cfg.eveowners.Get(toID).name)
            self.SetCaption(caption)
            scrolllist = []
            if not self.sr.Get('data') or purge:
                self.sr.data = sm.RemoteSvc('standing2').GetStandingCompositions(fromID, toID)
            if self.sr.data:
                prior = 0.0
                for each in self.sr.data:
                    if each.ownerID == fromID:
                        prior = each.standing
                        break

                scrolllist.append(sm.GetService('standing').GetStandingEntry(fromID, fromID, toID, prior, showBonuses=0, label='Current Value'))
                for each in self.sr.data:
                    if each.ownerID == fromID:
                        continue
                    charinfo = cfg.eveowners.Get(each.ownerID)
                    scrolllist.append(sm.GetService('standing').GetStandingEntry(each.ownerID, fromID, each.ownerID, each.standing, showBonuses=0))

            else:
                scrolllist.append(listentry.Get('Text', {'line': 1,
                 'text': localization.GetByLabel('UI/Standings/CompositionWindow/NoInfo')}))
            self.sr.scroll.Load(contentList=scrolllist)

        finally:
            self.loading = 0





