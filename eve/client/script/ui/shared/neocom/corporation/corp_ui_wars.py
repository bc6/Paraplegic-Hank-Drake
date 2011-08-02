import util
import xtriui
import uix
import form
import listentry
import uicls
import uiconst
import log

class CorpWars(uicls.Container):
    __guid__ = 'form.CorpWars'
    __nonpersistvars__ = []

    def Load(self, args):
        if not self.sr.Get('inited', 0):
            self.sr.headers = [mls.UI_GENERIC_STARTED,
             mls.UI_GENERIC_ISSUEDBY,
             mls.UI_CORP_AGAINST,
             mls.UI_GENERIC_FINISHED,
             mls.UI_CORP_CANFIGHT,
             mls.UI_CORP_RETRACTED,
             mls.UI_CORP_MUTUAL]
            self.sr.scroll = None
            self.sr.inited = 1
            btns = [[mls.UI_CMD_SELECT,
              self.SelectCorpOrAlliance,
              None,
              None]]
            self.toolbarContainer = uicls.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            btns = uicls.ButtonGroup(btns=btns, parent=self.toolbarContainer)
            self.toolbarContainer.height = btns.height
            self.sr.scroll = uicls.Scroll(parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            warTabs = [[mls.UI_CORP_OURWARS,
              self,
              self,
              'our'], [mls.UI_CORP_OTHERWARS,
              self,
              self,
              'all']]
            if not util.IsNPC(eve.session.corpid) and const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector or sm.GetService('corp').UserIsCEO():
                warTabs += [[mls.UI_COMBATLOG_CONFIRMEDKILLS,
                  self,
                  self,
                  'combat_kills'], [mls.UI_COMBATLOG_RECORDEDLOSSES,
                  self,
                  self,
                  'combat_losses']]
                btnContainer = uicls.Container(name='pageBtnContainer', parent=self, align=uiconst.TOBOTTOM, idx=0, padBottom=const.defaultPadding)
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0, align=uiconst.TORIGHT)
                btn.hint = mls.UI_GENERIC_VIEWMORE
                btn.state = uiconst.UI_HIDDEN
                btn.sr.icon.LoadIcon('ui_23_64_2')
                btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0, align=uiconst.TOLEFT)
                btn.hint = mls.UI_GENERIC_PREVIOUS
                btn.state = uiconst.UI_HIDDEN
                btn.sr.icon.LoadIcon('ui_23_64_1')
                btnContainer.height = max([ c.height for c in btnContainer.children ])
                self.btnContainer = btnContainer
                btnContainer.state = uiconst.UI_HIDDEN
            else:
                self.btnContainer = None
            tabs = uicls.TabGroup(name='tabparent', parent=self, idx=0)
            tabs.Startup(warTabs, 'corporationwars')
            self.killentries = 25
        sm.GetService('corpui').LoadTop('ui_7_64_7', mls.UI_CORP_WARS)
        self.myWars = 1
        self.viewingOwnerID = eve.session.allianceid or eve.session.corpid
        extrahint = ''
        self._HideNextPrevBtns()
        if args == 'all':
            self.ShowAllWars()
        elif args == 'our':
            self.ShowWars()
        elif args.startswith('combat_'):
            self.ShowCombatLog(args)
            extrahint = mls.UI_CORP_DELAYED15MINUTES
        sm.GetService('corpui').LoadTop('ui_7_64_7', mls.UI_CORP_WARS, extrahint)



    def _HideNextPrevBtns(self):
        if self.btnContainer:
            prevbtn = self.btnContainer.children[1]
            nextbtn = self.btnContainer.children[0]
            prevbtn.state = nextbtn.state = uiconst.UI_HIDDEN
            self.btnContainer.state = uiconst.UI_HIDDEN



    def ShowCombatLog(self, key):
        self.prevIDs = []
        if key == 'combat_kills':
            self.ShowCombatKills()
        elif key == 'combat_losses':
            self.ShowCombatLosses()



    def ShowCombatKills(self, offset = None, *args):
        recent = sm.GetService('corp').GetRecentKills(self.killentries, offset)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatKills, 'kills')



    def ShowCombatLosses(self, offset = None, *args):
        recent = sm.GetService('corp').GetRecentLosses(self.killentries, offset)
        page = 0
        if len(args):
            page = args[0]
        self.ShowKillsEx(recent, page, self.ShowCombatLosses, 'losses')



    def ShowKillsEx(self, recent, pagenum, func, combatType):
        self.toolbarContainer.state = uiconst.UI_HIDDEN
        (scrolllist, headers,) = sm.GetService('charactersheet').GetCombatEntries(recent)
        for c in self.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        self.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = self.btnContainer.children[1]
        nextbtn = self.btnContainer.children[0]
        if pagenum > 0:
            self.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            prevbtn.OnClick = (func, self.prevIDs[(pagenum - 1)], pagenum - 1)
        if len(recent) >= self.killentries:
            self.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), pagenum + 1)
            self.prevIDs.append(max(killIDs) + 1)
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = mls.UI_GENERIC_NOKILLSFOUND
        elif combatType == 'losses':
            noContentHintText = mls.UI_GENERIC_NOLOSSESFOUND
        self.SetHint()
        self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHintText)



    def OnWarChanged(self, warID, declaredByID, againstID, change):
        log.LogInfo('OnWarChanged warID:', warID, 'declaredByID:', declaredByID, 'againstID:', againstID, 'change:', change)
        if not self.sr.Get('inited', 0):
            log.LogInfo('OnWarChanged ui has not been loaded')
            return 
        if self.sr.scroll is None:
            log.LogInfo('OnWarChanged no scroll')
            return 
        ids = [declaredByID, againstID]
        if self.viewingOwnerID not in ids:
            log.LogInfo('OnWarChanged self.viewingOwnerID:', self.viewingOwnerID, 'not in ids:', ids)
            return 
        bAdd = 1
        bRemove = 1
        for (old, new,) in change.itervalues():
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('wars::OnWarChanged WTF')
        if bAdd:
            log.LogInfo('OnWarChanged adding war')
            war = sm.GetService('war').GetWars(self.viewingOwnerID)[warID]
            self.SetHint()
            scrolllist = []
            self._CorpWars__AddToList(war, scrolllist)
            if len(self.sr.scroll.sr.headers) > 0:
                if len(scrolllist):
                    self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
        elif bRemove:
            log.LogInfo('OnWarChanged removing war')
            entry = self.GetEntry(warID)
            if entry is not None:
                self.sr.scroll.RemoveEntries([entry])
            else:
                log.LogWarn('OnWarChanged war not found')
        else:
            log.LogInfo('OnWarChanged updating war')
            entry = self.GetEntry(warID)
            if entry is None:
                log.LogWarn('OnWarChanged war not found')
            else:
                war = sm.GetService('war').GetWars(self.viewingOwnerID)[warID]
                label = self._CorpWars__GetLabel(war)
                if entry.panel is not None:
                    entry.panel.sr.node.label = label
                    entry.panel.sr.label.text = label
                    entry.panel.sr.node.war = war



    def GetEntry(self, warID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.war.warID == warID:
                return entry




    def __GetLabel(self, war):
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(war.timeDeclared) if war.timeDeclared else mls.UI_GENERIC_UNKNOWN,
         cfg.eveowners.Get(war.declaredByID).name,
         cfg.eveowners.Get(war.againstID).name,
         util.FmtDate(war.timeFinished) if war.timeFinished else '',
         mls.UI_GENERIC_YES if util.IsWarInHostileState(war) else mls.UI_GENERIC_NO if war.timeDeclared else mls.UI_GENERIC_YES,
         util.FmtDate(war.retracted) if war.retracted is not None else '',
         mls.UI_GENERIC_YES if war.mutual else mls.UI_GENERIC_NO)
        return label



    def __AddToList(self, war, scrolllist):
        if not self.myWars:
            if eve.session.corpid in [war.declaredByID, war.againstID]:
                return 
        data = util.KeyVal()
        data.label = self._CorpWars__GetLabel(war)
        data.war = war
        if self.myWars:
            data.GetMenu = self.GetWarMenu
        scrolllist.append(listentry.Get('Generic', data=data))



    def ShowWars(self, *args):
        self.toolbarContainer.state = uiconst.UI_HIDDEN
        self.myWars = 1
        self.PopulateView(eve.session.allianceid or eve.session.corpid)



    def ShowAllWars(self, *args):
        self.myWars = 0
        self.toolbarContainer.state = uiconst.UI_NORMAL
        self.sr.scroll.Load(contentList=[], headers=self.sr.headers, noContentHint=mls.UI_CORP_SELECTCORPORALLIANCE)



    def GetFactionWars(self, corpID, *args):
        factionWars = {}
        warFactionID = sm.StartService('facwar').GetCorporationWarFactionID(corpID)
        if warFactionID:
            factions = [ each for each in sm.StartService('facwar').GetWarFactions() ]
            factionWars = util.IndexRowset(['warID',
             'declaredByID',
             'againstID',
             'timeDeclared',
             'timeFinished',
             'retracted',
             'retractedBy',
             'billID',
             'mutual'], [], 'warID')
            for (i, faction,) in enumerate(factions):
                if sm.StartService('facwar').IsEnemyFaction(faction, warFactionID):
                    factionWars[i * -1] = [None,
                     faction,
                     warFactionID,
                     None,
                     None,
                     None,
                     None,
                     None,
                     True]

        return factionWars



    def PopulateView(self, ownerID):
        try:
            sm.GetService('corpui').ShowLoad()
            self.SetHint()
            self.viewingOwnerID = ownerID
            regwars = sm.GetService('war').GetWars(self.viewingOwnerID)
            facwars = {}
            if not util.IsAlliance(self.viewingOwnerID) and util.IsCorporation(self.viewingOwnerID) and sm.StartService('facwar').GetCorporationWarFactionID(self.viewingOwnerID):
                facwars = self.GetFactionWars(self.viewingOwnerID)
            owners = []
            for wars in (regwars, facwars):
                for war in wars.itervalues():
                    if war.declaredByID not in owners:
                        owners.append(war.declaredByID)
                    if war.againstID not in owners:
                        owners.append(war.againstID)


            if len(owners):
                cfg.eveowners.Prime(owners)
            if self.destroyed:
                return 
            scrolllist = []
            for wars in (regwars, facwars):
                for war in wars.itervalues():
                    self._CorpWars__AddToList(war, scrolllist)


            self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers, noContentHint=mls.UI_CORP_SOMEONEISNOTINVOLVED % {'who': cfg.eveowners.Get(self.viewingOwnerID).ownerName})

        finally:
            sm.GetService('corpui').HideLoad()




    def SelectCorpOrAlliance(self, *args):
        dlg = sm.GetService('window').GetWindow('CorporationOrAlliancePickerDailog', 1, warableEntitysOnly=True)
        dlg.ShowModal()
        if dlg.ownerID:
            self.PopulateView(dlg.ownerID)



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def IsInCharge(self):
        if eve.session.allianceid is not None:
            return eve.session.corpid == sm.GetService('alliance').GetAlliance().executorCorpID and eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector
        else:
            return sm.GetService('corp').UserIsActiveCEO()



    def GetWarMenu(self, entry):
        menu = []
        if entry.sr.node.war.warID != -1:
            if entry.sr.node.war.againstID in [eve.session.corpid, eve.session.allianceid] and entry.sr.node.war.retracted == None:
                menu.append((mls.UI_CMD_SURRENDER, self.Surrender, (entry.sr.node.war.declaredByID, entry.sr.node.war.againstID, entry.sr.node.war.warID)))
                if 0 == entry.sr.node.war.mutual:
                    menu.append((mls.UI_CMD_DECLAREMUTUAL, self.ChangeMutualWarFlag, (entry.sr.node.war.warID, 1)))
                else:
                    menu.append((mls.UI_CMD_CANCELMUTUAL, self.ChangeMutualWarFlag, (entry.sr.node.war.warID, 0)))
            if entry.sr.node.war.declaredByID in [eve.session.corpid, eve.session.allianceid] and entry.sr.node.war.retracted == None:
                if self.IsInCharge():
                    menu.append((mls.UI_CORP_RETRACT, self.Retract, (entry.sr.node.war.warID,)))
        return menu



    def Retract(self, warID, *args):
        if not self.IsInCharge():
            if eve.session.allianceid is not None:
                raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED11})
            else:
                raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED12})
        if eve.Message('CrpConfirmRetractWar', {}, uiconst.YESNO) == uiconst.ID_YES:
            if eve.session.allianceid is not None:
                sm.GetService('alliance').RetractWar(warID)
            else:
                sm.GetService('corp').RetractWar(warID)
            self.ShowWars()



    def ChangeMutualWarFlag(self, warID, mutual, *args):
        if not self.IsInCharge():
            if eve.session.allianceid is not None:
                raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED11})
            else:
                raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED12})
        if eve.Message(['CrpConfirmUnmutualWar', 'CrpConfirmMutualWar'][mutual], {}, uiconst.YESNO) == uiconst.ID_YES:
            if eve.session.allianceid is not None:
                sm.GetService('alliance').ChangeMutualWarFlag(warID, mutual)
            else:
                sm.GetService('corp').ChangeMutualWarFlag(warID, mutual)
            self.ShowWars()



    def Surrender(self, declaredByID, againstID, warID, *args):
        ids = [declaredByID, againstID]
        if eve.session.allianceid is not None:
            if eve.session.allianceid not in ids:
                eve.Message('NotYourWarToEnd')
                return 
        elif eve.session.corpid not in ids:
            eve.Message('NotYourWarToEnd')
            return 
        if not self.IsInCharge():
            if eve.session.allianceid is not None:
                eve.Message('MustBeAllianceCEOToEndWar')
            else:
                eve.Message('MustBeActiveCEOToEndWar')
            return 
        if eve.session.stationid:
            sm.GetService('window').StartCEOTradeSession(declaredByID, againstID, warID)
        else:
            eve.Message('MustBeInStationToNegotiate')




