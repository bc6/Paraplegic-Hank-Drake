import uthread
import util
import corpObject
import blue

class CorporationsO(corpObject.base):
    __guid__ = 'corpObject.corporations'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.corporationByCorporationID = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change:
            self.corporationByCorporationID = None
        if 'corpid' in change:
            (oldID, newID,) = change['corpid']
            if newID is not None:
                if self.corporationByCorporationID is not None and self.corporationByCorporationID.has_key(newID):
                    del self.corporationByCorporationID[newID]



    def Reset(self):
        if self.has_key(eve.session.corpid):
            del self.corporationByCorporationID[eve.session.corpid]



    def has_key(self, corpID):
        if self.corporationByCorporationID is not None:
            return self.corporationByCorporationID.has_key(corpID)



    def GetCorporation(self, corpid = None, new = 0):
        if corpid is None:
            corpid = eve.session.corpid
        if self.corporationByCorporationID is not None and self.corporationByCorporationID.has_key(corpid) and not new:
            return self.corporationByCorporationID[corpid]
        corporation = None
        if corpid == eve.session.corpid:
            corporation = self.GetCorpRegistry().GetCorporation()
        else:
            corporation = sm.RemoteSvc('corpmgr').GetCorporations(corpid)
        self.LoadCorporation(corporation)
        return self.corporationByCorporationID[corpid]



    def LoadCorporation(self, corporation):
        if self.corporationByCorporationID is None:
            if type(corporation) == blue.DBRow:
                self.corporationByCorporationID = util.IndexRowset(corporation.__columns__, [list(corporation)], 'corporationID')
            else:
                self.corporationByCorporationID = util.IndexRowset(corporation.header, [corporation.line], 'corporationID')
        else:
            line = []
            for columnName in self.corporationByCorporationID.header:
                line.append(getattr(corporation, columnName))

            self.corporationByCorporationID[corporation.corporationID] = line



    def OnCorporationChanged(self, corpID, change):
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        if self.corporationByCorporationID is not None:
            if bAdd:
                if len(change) != len(self.corporationByCorporationID.header):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return 
                line = []
                for columnName in self.corporationByCorporationID.header:
                    line.append(change[columnName][1])

                self.corporationByCorporationID[corpID] = line
            elif not self.corporationByCorporationID.has_key(corpID):
                return 
            if bRemove:
                del self.corporationByCorporationID[corpID]
            else:
                corporation = self.corporationByCorporationID[corpID]
                for columnName in corporation.header:
                    if not change.has_key(columnName):
                        continue
                    setattr(corporation, columnName, change[columnName][1])

                if cfg.corptickernames.data.has_key(corpID):
                    header = cfg.corptickernames.header
                    line = cfg.corptickernames.data[corpID]
                    i = -1
                    for columnName in header:
                        i = i + 1
                        if not change.has_key(columnName):
                            continue
                        line[i] = change[columnName][1]

            updateDivisionNames = 0
            loadLogo = 0
            showOffices = 0
            loadButtons = 0
            resetCorpWindow = 0
            if eve.session.corpid == corpID:
                if 'division1' in change or 'division2' in change or 'division3' in change or 'division4' in change or 'division5' in change or 'division6' in change or 'division7' in change:
                    updateDivisionNames = 1
            if 'shape1' in change or 'shape2' in change or 'shape3' in change or 'color1' in change or 'color2' in change or 'color3' in change or 'typeface' in change:
                if eve.session.corpid == corpID:
                    loadLogo = 1
            if self.corp__locations.HasCorporationOffice(corpID):
                showOffices = 1
            if 'ceoID' in change and eve.session.corpid == corpID:
                (oldCeoID, newCeoID,) = change['ceoID']
                if eve.session.charid in change['ceoID']:
                    loadButtons = 1
                self.corp__members.MemberCanRunForCEO_ = None
                resetCorpWindow = 1
                showOffices = 1
            lobby = None
            if resetCorpWindow:
                sm.GetService('corpui').ResetWindow(1)
            if loadLogo:
                sm.GetService('corpui').LoadLogo(corpID)
            if updateDivisionNames:
                uthread.new(self._CorporationsO__UpdateDivisionNamesInTheUI).context = 'svc.corp.OnCorporationChanged'
            if showOffices:
                if lobby is None:
                    lobby = sm.GetService('station').GetLobby()
                if lobby is not None:
                    if lobby.sr and lobby.sr.lobbytabs:
                        if lobby.sr.lobbytabs.GetSelectedArgs() == 'lobby_offices':
                            lobby.ShowOffices()
            if loadButtons:
                if lobby is None:
                    lobby = sm.GetService('station').GetLobby()
                if lobby is not None:
                    lobby.LoadButtons()



    def GetDivisionNames(self, new = 0):
        corp = self.GetCorporation()
        return {1: corp.division1 or mls.UI_CORP_DIVISION_FIRSTDIVISION,
         2: corp.division2 or mls.UI_CORP_DIVISION_SECONDDIVISION,
         3: corp.division3 or mls.UI_CORP_DIVISION_THIRDDIVISION,
         4: corp.division4 or mls.UI_CORP_DIVISION_FOURTHDIVISION,
         5: corp.division5 or mls.UI_CORP_DIVISION_FIFTHDIVISION,
         6: corp.division6 or mls.UI_CORP_DIVISION_SIXTHDIVISION,
         7: corp.division7 or mls.UI_CORP_DIVISION_SEVENTHDIVISION,
         8: mls.UI_CORP_MASTERWALLET,
         9: corp.walletDivision2 or mls.UI_CORP_DIVISION_SECONDWALLETDIVISION,
         10: corp.walletDivision3 or mls.UI_CORP_DIVISION_THIRDWALLETDIVISION,
         11: corp.walletDivision4 or mls.UI_CORP_DIVISION_FOURTHWALLETDIVISION,
         12: corp.walletDivision5 or mls.UI_CORP_DIVISION_FIFTHWALLETDIVISION,
         13: corp.walletDivision6 or mls.UI_CORP_DIVISION_SIXTHWALLETDIVISION,
         14: corp.walletDivision7 or mls.UI_CORP_DIVISION_SEVENTHWALLETDIVISION}



    def __UpdateDivisionNamesInTheUI(self):
        wndid = None
        office = self.corp__locations.GetOffice()
        if office is not None:
            wndid = 'corpHangar_%s' % office.itemID
        if wndid is None:
            self.LogInfo('There are no offices here.')
            return 
        self.LogInfo("Char's corp has a hangar wndid", wndid)
        wnd = sm.GetService('window').GetWindow(wndid)
        if not wnd:
            self.LogInfo("Can't find char's corp hangar window")
        else:
            divisions = self.GetDivisionNames()
            self.LogInfo("Found char's corp hangar window, applying new division names", divisions)
            wnd.SetDivisionalHangarNames(divisions)



    def GetCostForCreatingACorporation(self):
        return const.corporationStartupCost



    def UpdateCorporationAbilities(self):
        return self.GetCorpRegistry().UpdateCorporationAbilities()



    def UpdateLogo(self, shape1, shape2, shape3, color1, color2, color3, typeface):
        return self.GetCorpRegistry().UpdateLogo(shape1, shape2, shape3, color1, color2, color3, typeface)



    def UpdateCorporation(self, description, url, taxRate, acceptApplications):
        return self.GetCorpRegistry().UpdateCorporation(description, url, taxRate, acceptApplications)



    def GetSuggestedTickerNames(self, corporationName):
        return self.GetCorpRegistry().GetSuggestedTickerNames(corporationName)



    def AddCorporation(self, corporationName, tickerName, description, url = '', taxRate = 0.0, shape1 = None, shape2 = None, shape3 = None, color1 = None, color2 = None, color3 = None, typeface = None, applicationsEnabled = 1):
        return self.GetCorpRegistry().AddCorporation(corporationName, tickerName, description, url, taxRate, shape1, shape2, shape3, color1, color2, color3, typeface, applicationsEnabled)




