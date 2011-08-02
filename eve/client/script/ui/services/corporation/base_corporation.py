from service import SERVICE_START_PENDING, SERVICE_RUNNING, Service, ROLE_IGB, ROLE_ANY
import uix
import blue
import uthread
import util
import moniker
import corpObject
import uiconst

def ReturnNone():
    return None


MAX_NUM_BULLETINS = 10

class Corporation(Service):
    __exportedcalls__ = {'AddCorporation': [],
     'GetCorporation': [],
     'GetDivisionNames': [],
     'GetCostForCreatingACorporation': [],
     'UpdateCorporationAbilities': [],
     'UpdateLogo': [],
     'UpdateCorporation': [],
     'GetSuggestedTickerNames': [],
     'GetSuggestedAllianceShortNames': [],
     'CreateAlliance': [],
     'ApplyToJoinAlliance': [],
     'GetAllianceApplications': [],
     'GetMemberIDs': [],
     'GetMembers': [],
     'GetMember': [],
     'GetMembersAsEveOwners': [],
     'GetMyGrantableRoles': [],
     'GetRoles': [],
     'GetRoleGroups': [],
     'GetLocationalRoles': [],
     'UpdateMember': [],
     'UpdateMembers': [],
     'UserIsActiveCEO': [],
     'UserIsCEO': [],
     'MemberCanCreateCorporation': [],
     'MemberCanRunForCEO': [],
     'CanKickOut': [],
     'KickOut': [],
     'RemoveAllRoles': [],
     'UserBlocksRoles': [],
     'GetMemberIDsWithMoreThanAvgShares': [],
     'GetMemberIDsByQuery': [],
     'ExecuteActions': [],
     'GetTitles': [],
     'UpdateTitle': [],
     'UpdateTitles': [],
     'DeleteTitle': [],
     'GetVoteCaseOptions': [],
     'CanViewVotes': [],
     'GetVoteCasesByCorporation': [],
     'GetSanctionedActionsByCorporation': [],
     'UpdateSanctionedAction': [],
     'InsertVoteCase': [],
     'GetVotes': [],
     'InsertVote': [],
     'CanVote': [],
     'RetractWar': [],
     'ChangeMutualWarFlag': [],
     'GetRecentKills': [],
     'GetRecentLosses': [],
     'GetCorporationsWithOfficesAtStation': [],
     'GetOffices': [],
     'GetOffice': [],
     'GetOffice_NoWireTrip': [],
     'GetOfficeFolderIDForOfficeID': [],
     'RemoveOffice': [],
     'GetPublicStationInfo': [],
     'GetDivisionalRoles': [],
     'GetHierarchicalRoles': [],
     'GetApplications': [],
     'GetApplicationsWithStatus': [],
     'GetMyApplications': [],
     'GetMyApplicationsWithStatus': [],
     'DeleteApplication': [],
     'InsertApplication': [],
     'ApplyForMembership': [],
     'UpdateApplicationOffer': [],
     'DoesCharactersCorpOwnThisStation': [],
     'MoveCompanyShares': [],
     'MovePrivateShares': [],
     'PayoutDividend': [],
     'UpdateDivisionNames': [],
     'ResignFromCEO': [],
     'GetInfoWindowDataForChar': [],
     'GetMemberTrackingInfo': [],
     'GetRentalDetailsPlayer': [],
     'GetRentalDetailsCorp': [],
     'GetLockedItemsByLocation': [],
     'GetLockedItemLocations': [],
     'IsItemLocked': [],
     'IsItemIDLocked': [],
     'GetCorpStationManager': [],
     'SetAccountKey': [],
     'GetMyCorpAccountName': [],
     'GetRecruitmentAdTypes': [],
     'EditBulletin': [ROLE_IGB | ROLE_ANY],
     'DeleteBulletin': [ROLE_IGB],
     'GetContactList': []}
    __guid__ = 'svc.corp'
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnCorporationChanged',
     'OnOfficeRentalChanged',
     'OnCorporationMemberChanged',
     'OnCorporationVoteCaseChanged',
     'OnCorporationVoteCaseOptionChanged',
     'OnCorporationVoteChanged',
     'OnSanctionedActionChanged',
     'OnCorporationApplicationChanged',
     'OnCorporationRecruitmentAdChanged',
     'OnShareChange',
     'OnGodmaSkillTrained',
     'OnAttribute',
     'OnTitleChanged',
     'OnAllianceApplicationChanged',
     'OnLockedItemChange']
    __servicename__ = 'corp'
    __displayname__ = 'Corporation Client Service'
    __dependencies__ = []
    __functionalobjects__ = ['corporations',
     'members',
     'applications',
     'shares',
     'voting',
     'sanctionedActions',
     'alliance',
     'locations',
     'titles',
     'itemLocking',
     'wars',
     'recruitment']

    def __init__(self):
        Service.__init__(self)
        self._Corporation__roles = None
        self._Corporation__roleGroups = None
        self._Corporation__roleGroupings = None
        self._Corporation__roleGroupingsForTitles = None
        self._Corporation__divisionalRoles = None
        self._Corporation__hierarchicalRoles = None
        self._Corporation__locationalRoles = [const.corpRoleHangarCanTake1,
         const.corpRoleHangarCanTake2,
         const.corpRoleHangarCanTake3,
         const.corpRoleHangarCanTake4,
         const.corpRoleHangarCanTake5,
         const.corpRoleHangarCanTake6,
         const.corpRoleHangarCanTake7,
         const.corpRoleHangarCanQuery1,
         const.corpRoleHangarCanQuery2,
         const.corpRoleHangarCanQuery3,
         const.corpRoleHangarCanQuery4,
         const.corpRoleHangarCanQuery5,
         const.corpRoleHangarCanQuery6,
         const.corpRoleHangarCanQuery7,
         const.corpRoleContainerCanTake1,
         const.corpRoleContainerCanTake2,
         const.corpRoleContainerCanTake3,
         const.corpRoleContainerCanTake4,
         const.corpRoleContainerCanTake5,
         const.corpRoleContainerCanTake6,
         const.corpRoleContainerCanTake7]
        self._Corporation__recruitmentAdTypes = None
        self._Corporation__recruitmentAdGroups = None
        self.resigning = False



    def GetDependencies(self):
        return self.__dependencies__



    def GetObjectNames(self):
        return self.__functionalobjects__



    def Run(self, memStream = None):
        self.LogInfo('Starting Corporation')
        self.state = SERVICE_START_PENDING
        sm.FavourMe(self.OnSessionChanged)
        sm.FavourMe(self.OnOfficeRentalChanged)
        sm.FavourMe(self.OnCorporationMemberChanged)
        self._Corporation__corpRegistry = None
        self._Corporation__corpRegistryCorpID = None
        self._Corporation__corpStationManager = None
        self._Corporation__corpStationManagerStationID = None
        items = corpObject.__dict__.items()
        for objectName in self.__functionalobjects__:
            if objectName == 'base':
                continue
            object = None
            classType = 'corpObject.%s' % objectName
            for i in range(0, len(corpObject.__dict__)):
                self.LogInfo('Processing', items[i])
                if len(items[i][0]) > 1:
                    if items[i][0][:2] == '__':
                        continue
                if items[i][1].__guid__ == classType:
                    object = CreateInstance(classType, (self,))
                    break

            if object is None:
                raise RuntimeError('FunctionalObject not found %s' % classType)
            setattr(self, objectName, object)

        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            object.DoObjectWeakRefConnections()

        self.state = SERVICE_RUNNING
        if eve.session.corpid:
            uthread.new(self.members.PrimeCorpInformation)
            if not util.IsNPC(eve.session.corpid):
                uthread.new(self.GetMyCorporationsOffices)
        self.bulletins = None
        self.bulletinsTimestamp = 0



    def Stop(self, memStream = None):
        self._Corporation__corpRegistry = None
        self._Corporation__corpRegistryCorpID = None
        self._Corporation__corpStationManager = None
        self._Corporation__corpStationManagerStationID = None



    def RefreshMoniker(self):
        if self._Corporation__corpRegistry is not None:
            self._Corporation__corpRegistry.UnBind()



    def GetCorpRegistry(self):
        if self._Corporation__corpRegistry is None:
            self._Corporation__corpRegistry = moniker.GetCorpRegistry()
            self._Corporation__corpRegistryCorpID = eve.session.corpid
        if self._Corporation__corpRegistryCorpID != eve.session.corpid:
            if self._Corporation__corpRegistry is not None:
                self._Corporation__corpRegistry.Unbind()
            self._Corporation__corpRegistry = moniker.GetCorpRegistry()
            self._Corporation__corpRegistryCorpID = eve.session.corpid
        return self._Corporation__corpRegistry



    def GetCorpStationManager(self):
        if not eve.session.stationid:
            if self._Corporation__corpStationManager is not None:
                self._Corporation__corpStationManager.Unbind()
            raise RuntimeError('InvalidCallee due to state')
        elif self._Corporation__corpStationManager is None:
            self._Corporation__corpStationManager = moniker.GetCorpStationManager()
            self._Corporation__corpStationManagerStationID = eve.session.stationid
        if self._Corporation__corpStationManagerStationID != eve.session.stationid:
            if self._Corporation__corpStationManager is not None:
                self._Corporation__corpStationManager.Unbind()
            self._Corporation__corpStationManager = moniker.GetCorpStationManager()
            self._Corporation__corpStationManagerStationID = eve.session.stationid
        return self._Corporation__corpStationManager



    def PerformSelectiveSessionChange(self, reason, func, *args, **keywords):
        violateSafetyTimer = 0
        if session.nextSessionChange is not None and session.nextSessionChange > blue.os.GetTime():
            if session.sessionChangeReason == reason:
                violateSafetyTimer = 1
        if violateSafetyTimer > 0:
            print 'I will perform a session change even though I should wait %d more seconds' % ((session.nextSessionChange - blue.os.GetTime()) / SEC)
        import copy
        kw2 = copy.copy(keywords)
        kw2['violateSafetyTimer'] = violateSafetyTimer
        kw2['wait'] = 1
        sm.StartService('sessionMgr').PerformSessionChange(reason, func, *args, **kw2)



    def SetAccountKey(self, accountKey):
        self.PerformSelectiveSessionChange('corp.setaccountkey', self.members.SetAccountKey, accountKey)



    def GetCorpAccountName(self, acctID):
        if acctID is None:
            return 
        return self.GetDivisionNames()[(acctID - 1000 + 8)]



    def GetMyCorpAccountName(self):
        return eve.session.corpAccountKey and self.GetCorpAccountName(eve.session.corpAccountKey)



    def CallDelegates(self, functionName, *args):
        for objectName in self.__functionalobjects__:
            object = getattr(self, objectName)
            function = getattr(object, functionName, None)
            if function is not None:
                function(*args)




    def DoSessionChanging(self, isRemote, session, change):
        if 'stationid' in change:
            (oldID, newID,) = change['stationid']
            if self._Corporation__corpStationManager is not None:
                self._Corporation__corpStationManager = None
                self._Corporation__corpStationManagerStationID = None
        if 'corpid' in change:
            self._Corporation__hierarchicalRoles = None
            self._Corporation__divisionalRoles = None
            self._Corporation__roleGroupings = None
            self._Corporation__roleGroupingsForTitles = None
        self.CallDelegates('DoSessionChanging', isRemote, session, change)
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            sm.StopService(self.__guid__[4:])



    def OnSessionChanged(self, isRemote, session, change):
        self.CallDelegates('OnSessionChanged', isRemote, session, change)
        if 'corpid' in change:
            self.bulletins = None
            self.bulletinsTimestamp = 0



    def GetCorporation(self, corpid = None, new = 0):
        return self.corporations.GetCorporation(corpid, new)



    def GetCostForCreatingACorporation(self):
        return self.corporations.GetCostForCreatingACorporation()



    def UpdateCorporationAbilities(self):
        return self.corporations.UpdateCorporationAbilities()



    def UpdateLogo(self, shape1, shape2, shape3, color1, color2, color3, typeface):
        return self.corporations.UpdateLogo(shape1, shape2, shape3, color1, color2, color3, typeface)



    def UpdateCorporation(self, description, url, taxRate, acceptApplications):
        return self.corporations.UpdateCorporation(description, url, taxRate, acceptApplications)



    def GetSuggestedTickerNames(self, corporationName):
        return self.corporations.GetSuggestedTickerNames(corporationName)



    def AddCorporation(self, corporationName, tickerName, description, url = '', taxRate = 0.0, shape1 = None, shape2 = None, shape3 = None, color1 = None, color2 = None, color3 = None, typeface = None, applicationsEnabled = 1):
        return self.corporations.AddCorporation(corporationName, tickerName, description, url, taxRate, shape1, shape2, shape3, color1, color2, color3, typeface, applicationsEnabled)



    def OnCorporationChanged(self, corpID, change):
        self.corporations.OnCorporationChanged(corpID, change)



    def GetDivisionNames(self, new = 0):
        names = self.corporations.GetDivisionNames(new)
        return names



    def GetSuggestedAllianceShortNames(self, allianceName):
        return self.alliance.GetSuggestedAllianceShortNames(allianceName)



    def CreateAlliance(self, allianceName, shortName, description, url):
        return self.alliance.CreateAlliance(allianceName, shortName, description, url)



    def ApplyToJoinAlliance(self, allianceID, applicationText):
        return self.alliance.ApplyToJoinAlliance(allianceID, applicationText)



    def GetAllianceApplications(self):
        return self.alliance.GetAllianceApplications()



    def DeleteAllianceApplication(self, allianceID):
        return self.alliance.DeleteAllianceApplication(allianceID)



    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if corpID == eve.session.corpid:
            self.alliance.OnAllianceApplicationChanged(allianceID, corpID, change)



    def GetMemberIDs(self):
        return self.members.GetMemberIDs()



    def GetMembers(self):
        return self.members.GetMembers()



    def GetMember(self, charID):
        return self.members.GetMember(charID)



    def GetMembersAsEveOwners(self):
        return self.members.GetMembersAsEveOwners()



    def UpdateMember(self, charIDToUpdate, title = None, divisionID = None, squadronID = None, roles = None, grantableRoles = None, rolesAtHQ = None, grantableRolesAtHQ = None, rolesAtBase = None, grantableRolesAtBase = None, rolesAtOther = None, grantableRolesAtOther = None, baseID = None, titleMask = None, blockRoles = None):
        return self.members.UpdateMember(charIDToUpdate, title, divisionID, squadronID, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther, baseID, titleMask, blockRoles)



    def UpdateMembers(self, rows):
        return self.members.UpdateMembers(rows)



    def OnCorporationMemberChanged(self, memberID, change):
        self.members.OnCorporationMemberChanged(memberID, change)



    def UserIsCEO(self):
        return self.GetCorporation().ceoID == eve.session.charid



    def UserIsActiveCEO(self):
        if eve.session.corprole & const.corpRoleDirector:
            if self.UserIsCEO():
                return 1
        return 0



    def MemberCanRunForCEO(self):
        return self.members.MemberCanRunForCEO()



    def MemberCanCreateCorporation(self):
        return self.members.MemberCanCreateCorporation()



    def GetMyGrantableRoles(self):
        return self.members.GetMyGrantableRoles()



    def CanLeaveCurrentCorporation(self):
        return self.GetCorpRegistry().CanLeaveCurrentCorporation()



    def CanKickOut(self, charID):
        if eve.session.charid != charID and const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
            return 0
        return self.GetCorpRegistry().CanBeKickedOut(charID)



    def KickOut(self, charID, confirm = True):
        if not self.CanKickOut(charID):
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_ACCESSDENIED4})
        if self.resigning:
            return 
        try:
            self.resigning = True
            if confirm:
                if charID == eve.session.charid:
                    if eve.Message('ConfirmQuitCorporation', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                        return 
                elif eve.Message('ConfirmKickCorpMember', {'name': cfg.eveowners.Get(charID).name}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return 

        finally:
            self.resigning = False

        res = None
        if charID == eve.session.charid:
            sm.GetService('sessionMgr').PerformSessionChange('corp.kickself', self.GetCorpRegistry().KickOutMember, charID)
        else:
            res = self.GetCorpRegistry().KickOutMember(charID)
        return res



    def RemoveAllRoles(self, silent = False):
        if not silent and eve.Message('ConfirmRemoveAllRoles', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        self.UpdateMember(eve.session.charid, None, None, None, 0, 0, 0, 0, 0, 0, 0, 0, None, 0, 1)



    def GetMemberIDsWithMoreThanAvgShares(self):
        return self.GetCorpRegistry().GetMemberIDsWithMoreThanAvgShares()



    def GetMemberIDsByQuery(self, query, includeImplied, searchTitles):
        return self.GetCorpRegistry().GetMemberIDsByQuery(query, includeImplied, searchTitles)



    def ExecuteActions(self, targetIDs, actions):
        return self.members.ExecuteActions(targetIDs, actions)



    def OnGodmaSkillTrained(self, skillID):
        self.members.OnGodmaSkillTrained(skillID)



    def OnAttribute(self, attributeName, item, value):
        self.members.OnAttribute(attributeName, item, value)



    def OnAttributes(self, changes):
        self.members.OnAttributes(changes)



    def UserBlocksRoles(self):
        return self.members.MemberBlocksRoles()



    def GetTitles(self, titleID = None):
        return self.titles.GetTitles(titleID)



    def UpdateTitle(self, titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther):
        self.titles.UpdateTitle(titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther)



    def UpdateTitles(self, titles):
        self.titles.UpdateTitles(titles)



    def DeleteTitle(self, titleID):
        self.titles.DeleteTitle(titleID)



    def OnTitleChanged(self, corpID, titleID, change):
        self.titles.OnTitleChanged(corpID, titleID, change)



    def GetSharesByShareholder(self, corpShares = 0):
        return self.shares.GetSharesByShareholder(corpShares)



    def GetShareholders(self):
        return self.shares.GetShareholders()



    def MoveCompanyShares(self, corporationID, toShareholderID, numberOfShares):
        return self.shares.MoveCompanyShares(corporationID, toShareholderID, numberOfShares)



    def MovePrivateShares(self, corporationID, toShareholderID, numberOfShares):
        return self.shares.MovePrivateShares(corporationID, toShareholderID, numberOfShares)



    def OnShareChange(self, shareholderID, corporationID, change):
        self.shares.OnShareChange(shareholderID, corporationID, change)
        self.members.OnShareChange(shareholderID, corporationID, change)
        self.voting.OnShareChange(shareholderID, corporationID, change)



    def GetVoteCasesByCorporation(self, corpid, new = 0, maxLen = 0):
        return self.voting.GetVoteCasesByCorporation(corpid, new, maxLen)



    def GetVoteCaseOptions(self, voteID, corpID = None, new = 0):
        return self.voting.GetVoteCaseOptions(voteID, corpID, new)



    def OnCorporationVoteCaseChanged(self, corporationID, voteCaseID, change):
        self.voting.OnCorporationVoteCaseChanged(corporationID, voteCaseID, change)



    def OnCorporationVoteCaseOptionChanged(self, corporationID, voteCaseID, optionID, change):
        self.voting.OnCorporationVoteCaseOptionChanged(corporationID, voteCaseID, optionID, change)



    def OnCorporationVoteChanged(self, corporationID, voteCaseID, characterID, change):
        self.voting.OnCorporationVoteChanged(corporationID, voteCaseID, characterID, change)



    def CanViewVotes(self, corpid, new = 0):
        return self.voting.CanViewVotes(corpid, new)



    def GetSanctionedActionsByCorporation(self, corporationID, state):
        return self.sanctionedActions.GetSanctionedActionsByCorporation(corporationID, state)



    def UpdateSanctionedAction(self, voteCaseID, inEffect, reason = ''):
        return self.sanctionedActions.UpdateSanctionedAction(voteCaseID, inEffect, reason)



    def OnSanctionedActionChanged(self, corpID, voteCaseID, change):
        return self.sanctionedActions.OnSanctionedActionChanged(corpID, voteCaseID, change)



    def InsertVoteCase(self, voteCaseText, description, corporationID, voteType, voteCaseOptions, startDateTime = None, endDateTime = None):
        return self.voting.InsertVoteCase(voteCaseText, description, corporationID, voteType, voteCaseOptions, startDateTime, endDateTime)



    def GetVotes(self, corporationID, voteCaseID):
        return self.voting.GetVotes(corporationID, voteCaseID)



    def InsertVote(self, corporationID, voteCaseID, voteValue):
        return self.voting.InsertVote(corporationID, voteCaseID, voteValue)



    def CanVote(self, corporationID):
        return self.voting.CanVote(corporationID)



    def RetractWar(self, againstID):
        return self.wars.RetractWar(againstID)



    def ChangeMutualWarFlag(self, warID, mutual):
        return self.wars.ChangeMutualWarFlag(warID, mutual)



    def GetRecentKills(self, num, offset):
        return self.wars.GetRecentKills(num, offset)



    def GetRecentLosses(self, num, offset):
        return self.wars.GetRecentLosses(num, offset)



    def OnCorporationApplicationChanged(self, applicantID, corporationID, change):
        self.applications.OnCorporationApplicationChanged(applicantID, corporationID, change)



    def GetApplications(self, characterID = -1, forceUpdate = False):
        return self.applications.GetApplications(characterID, forceUpdate)



    def GetApplicationsWithStatus(self, status):
        return self.applications.GetApplicationsWithStatus(status)



    def GetMyApplications(self, corporationID = -1, forceUpdate = False):
        return self.applications.GetMyApplications(corporationID, forceUpdate)



    def GetMyApplicationsWithStatus(self, status):
        return self.applications.GetMyApplicationsWithStatus(status)



    def DeleteApplication(self, corporationID, characterID):
        return self.applications.DeleteApplication(corporationID, characterID)



    def InsertApplication(self, corporationID, applicationText):
        return self.applications.InsertApplication(corporationID, applicationText)



    def UpdateApplicationOffer(self, characterID, applicationText, status, applicationDateTime = None):
        return self.applications.UpdateApplicationOffer(characterID, applicationText, status, applicationDateTime)



    def ApplyForMembership(self, corpid):
        if not eve.session.stationid2:
            raise UserError('CanNotApplyToCorpUnlessDocked')
        if eve.session.corpid == corpid:
            raise UserError('CanNotJoinCorpAlreadyAMember', {'corporation': cfg.eveowners.Get(eve.session.corpid).name})
        if self.UserIsCEO():
            raise UserError('CeoCanNotJoinACorp', {'CEOsCorporation': cfg.eveowners.Get(eve.session.corpid).name,
             'otherCorporation': cfg.eveowners.Get(corpid).name})
        applications = self.GetMyApplications(corpid)
        if len(applications) != 0:
            sm.GetService('corpui').ViewApplication(corpid)
            return 
        corporation = self.GetCorporation(corpid)
        corpName = cfg.eveowners.Get(corpid).name
        tax = corporation.taxRate * 100
        format = [{'type': 'header',
          'text': mls.UI_STATION_APPLYFORMEMBERSHIPTO % {'corp': corpName}},
         {'type': 'push'},
         {'type': 'btline'},
         {'type': 'textedit',
          'key': 'appltext',
          'label': mls.UI_CORP_APPLICATIONTEXT,
          'maxLength': 1000},
         {'type': 'btline'},
         {'type': 'push'},
         {'type': 'header',
          'text': mls.UI_STATION_CURRENTTAXRATEFOR % {'corp': '<b>%s</b>' % corpName,
                   'taxrate': tax}}]
        if not corporation.isRecruiting:
            format.append({'type': 'header',
             'text': '<color=yellow>%s</color>' % mls.UI_CORP_RECRUITMAYBECLOSED})
        format.append({'type': 'errorcheck',
         'errorcheck': self.CheckApplication})
        retval = uix.HybridWnd(format, mls.UI_STATION_JOINCORPORATION, 1, None, uiconst.OKCANCEL, None, 400, 200, icon='ui_7_64_6', blockconfirm=True, unresizeAble=True)
        if retval is not None:
            self.InsertApplication(corpid, retval['appltext'])



    def CheckApplication(self, retval):
        if retval.has_key('appltext'):
            applicationText = retval['appltext']
            if len(applicationText) > 1000:
                return mls.UI_CORP_HINT4 % {'len': len(applicationText)}
        return ''



    def GetPublicStationInfo(self):
        return self.locations.GetPublicStationInfo()



    def GetCorporationsWithOfficesAtStation(self):
        return self.locations.GetCorporationsWithOfficesAtStation()



    def GetOffices(self):
        return self.locations.GetOffices()



    def GetOffice(self, corpID = None):
        return self.locations.GetOffice(corpID)



    def GetOffice_NoWireTrip(self):
        return self.locations.GetOffice_NoWireTrip()



    def GetOfficeFolderIDForOfficeID(self, officeID):
        return self.locations.GetOfficeFolderIDForOfficeID(officeID)



    def AddOffice(self, corporationID, officeID, folderID):
        return self.locations.AddOffice(corporationID, officeID, folderID)



    def RemoveOffice(self, corporationID, officeID, folderID):
        return self.locations.RemoveOffice(corporationID, officeID, folderID)



    def OnOfficeRentalChanged(self, corporationID, officeID, folderID):
        self.locations.OnOfficeRentalChanged(corporationID, officeID, folderID)



    def DoesCharactersCorpOwnThisStation(self):
        return self.locations.DoesCharactersCorpOwnThisStation()



    def GetMyCorporationsOffices(self):
        return self.locations.GetMyCorporationsOffices()



    def GetMyCorporationsStations(self):
        return self.locations.GetMyCorporationsStations()



    def OnCorporationRecruitmentAdChanged(self, corporationID, adID, change):
        self.recruitment.OnCorporationRecruitmentAdChanged(corporationID, adID, change)



    def CreateRecruitmentAd(self, days, typeMask, allianceID, description = None, channelID = None, recruiters = (), title = None):
        return self.recruitment.CreateRecruitmentAd(days, typeMask, allianceID, description, channelID, recruiters, title)



    def UpdateRecruitmentAd(self, adID, typeMask, description = None, channelID = None, recruiters = (), title = None, addedDays = 0):
        return self.recruitment.UpdateRecruitmentAd(adID, typeMask, description, channelID, recruiters, title, addedDays)



    def DeleteRecruitmentAd(self, adID):
        return self.recruitment.DeleteRecruitmentAd(adID)



    def GetRecruitmentAdsForCorporation(self):
        return self.recruitment.GetRecruitmentAdsForCorporation()



    def GetRecruiters(self, corpID, adID):
        return self.recruitment.GetRecruiters(corpID, adID)



    def GetRecruitmentAdsByCriteria(self, typeMask, isInAlliance, minMembers, maxMembers):
        return sm.RemoteSvc('corporationSvc').GetRecruitmentAdsByCriteria(typeMask, isInAlliance, minMembers, maxMembers)



    def GetDivisionalRoles(self):
        if self._Corporation__divisionalRoles is None:
            roles = self.GetHierarchicalRoles()
            divisions = roles.divisions
            self._Corporation__divisionalRoles = []
            for (divisionNumber, division,) in divisions.iteritems():
                for role in division.roles.itervalues():
                    self._Corporation__divisionalRoles.append(role.roleID)


        return self._Corporation__divisionalRoles



    def GetHierarchicalRoles(self):
        if self._Corporation__hierarchicalRoles is None:
            divisionNames = self.GetDivisionNames()
            roles = self.GetRoles()
            divisions = {}
            general = util.Rowset(roles.header)
            digits = ('1', '2', '3', '4', '5', '6', '7')
            for role in roles:
                lastCharacter = role.roleName[-1:]
                if lastCharacter not in digits:
                    general.append(util.Row(roles.header, role))
                else:
                    divisionID = int(lastCharacter)
                    if not divisions.has_key(divisionID):
                        divisions[divisionID] = util.Row(['name', 'roles'], [divisionNames[divisionID], {}])
                    divisions[divisionID].roles[role.roleName[:-1]] = role

            self._Corporation__hierarchicalRoles = util.Row(['general', 'divisions'], [general, divisions])
        return self._Corporation__hierarchicalRoles



    def GetRoles(self):
        if self._Corporation__roles is None:
            self._Corporation__roles = self.GetCorpRegistry().GetRoles()
            if prefs.languageID != 'EN':
                for row in self._Corporation__roles:
                    row.shortDescription = Tr(row.shortDescription, 'dbo.crpRoles.shortDescription', row.roleIID)
                    row.description = Tr(row.description, 'dbo.crpRoles.description', row.roleIID)

        return self._Corporation__roles



    def GetRoleGroups(self):
        if self._Corporation__roleGroups is None:
            self._Corporation__roleGroups = self.GetCorpRegistry().GetRoleGroups()
        return self._Corporation__roleGroups



    def GetRoleGroupings(self, forTitles = 0):
        roleGroups = self.GetRoleGroups()
        divisionNames = self.GetDivisionNames()
        roles = self.GetRoles()
        header = None
        lines = []
        for roleGroup in roleGroups:
            line = []
            if header is None:
                header = []
                for columnName in roleGroup.header:
                    header.append(columnName)

                header.append('columns')
            for columnName in header:
                if columnName == 'columns':
                    continue
                s = getattr(roleGroup, columnName)
                line.append(s)

            columns = []
            if roleGroup.isDivisional:
                rolesByDivisions = {}
                isAccount = False
                for role in roles:
                    if role.roleID & roleGroup.roleMask == role.roleID:
                        divisionID = int(role.roleName[-1:])
                        if not rolesByDivisions.has_key(divisionID):
                            rolesByDivisions[divisionID] = []
                        desc = ''
                        if -1 != role.roleName.find('CanTake'):
                            desc = mls.UI_GENERIC_TAKE
                        elif -1 != role.roleName.find('CanQuery'):
                            desc = mls.UI_GENERIC_QUERY
                        if role.roleName.startswith('roleAccount'):
                            isAccount = True
                            desc = ''
                        rolesByDivisions[divisionID].append([role.roleName, [desc, role]])

                for divisionID in (1, 2, 3, 4, 5, 6, 7):
                    subcolumns = []
                    rolesByDivision = rolesByDivisions[divisionID]
                    rolesByDivision.sort(lambda a, b: -(a[1][0].upper() < b[1][0].upper()))
                    for (roleName, descAndRole,) in rolesByDivision:
                        subcolumns.append(descAndRole)

                    add = [0, 7][isAccount]
                    name = divisionNames.get(divisionID + add, None)
                    columns.append([name, subcolumns])

            else:

                def SortKey(a, b):
                    return -(a.shortDescription.upper() < b.shortDescription.upper())


                roles.sort(SortKey)
                for role in roles:
                    if forTitles and role.roleID == const.corpRoleDirector:
                        continue
                    if role.roleID & roleGroup.roleMask == role.roleID:
                        columns.append([role.shortDescription, [['', role]]])

            line.append(columns)
            lines.append(line)

        if forTitles:
            self._Corporation__roleGroupingsForTitles = util.IndexRowset(header, lines, 'roleGroupID')
            return self._Corporation__roleGroupingsForTitles
        else:
            self._Corporation__roleGroupings = util.IndexRowset(header, lines, 'roleGroupID')
            return self._Corporation__roleGroupings



    def GetLocationalRoles(self):
        return self._Corporation__locationalRoles



    def PayoutDividend(self, payShareholders, payoutAmount):
        return self.GetCorpRegistry().PayoutDividend(payShareholders, payoutAmount)



    def UpdateDivisionNames(self, divisions1, divisions2, divisions3, divisions4, divisions5, divisions6, divisions7, walletDivision1, walletDivision2, walletDivision3, walletDivision4, walletDivision5, walletDivision6, walletDivision7):
        res = self.GetCorpRegistry().UpdateDivisionNames(divisions1, divisions2, divisions3, divisions4, divisions5, divisions6, divisions7, walletDivision1, walletDivision2, walletDivision3, walletDivision4, walletDivision5, walletDivision6, walletDivision7)
        self._Corporation__hierarchicalRoles = None
        self._Corporation__roleGroupings = None
        self._Corporation__roleGroupingsForTitles = None
        return res



    def __ResignFromCEO(self, newCeoID = None):
        if newCeoID is None and eve.session.allianceid is not None and len(self.members.GetMembers()) < 2:
            raise UserError('CanNotDestroyCorpInAlliance')
        return self.GetCorpRegistry().ResignFromCEO(newCeoID)



    def ResignFromCEO(self):
        if not eve.session.stationid:
            eve.Message('CrpCanNotChangeCorpInSpace')
            return 
        if not self.UserIsCEO():
            eve.Message('OnlyCEOCanResign')
            return 
        memberCount = len(self.GetMembers())
        if memberCount <= 1:
            if eve.Message('CrpDestroyCorpWarning', {}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
                return 
        elif eve.Message('AskResignAsCEO', {'memberCount': memberCount - 1}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
            return 
        res = sm.GetService('sessionMgr').PerformSessionChange('corp.resignceo', self._Corporation__ResignFromCEO)
        if res is None:
            return 
        owners = []
        for charID in res:
            if charID not in owners:
                owners.append(charID)

        if len(owners):
            cfg.eveowners.Prime(owners)
        tmplist = []
        for charID in res:
            owner = cfg.eveowners.Get(charID)
            tmplist.append((owner.name, charID, owner.typeID))

        newCEO = uix.ListWnd(tmplist, 'character', mls.UI_CORP_SELECTREPLACEMENTCEO, mls.UI_CORP_SELECTREPLACEMENTCEOTEXT, 1)
        if newCEO:
            newCeoID = newCEO[1]
            eve.session.ResetSessionChangeTimer('Retrying with selected alternate CEO')
            sm.GetService('sessionMgr').PerformSessionChange('corp.resignceo', self._Corporation__ResignFromCEO, newCeoID)



    def GetInfoWindowDataForChar(self, charID, acceptBlank = 0):
        data = self.GetCorpRegistry().GetInfoWindowDataForChar(charID)
        if not acceptBlank:
            if data.title1 is not None and len(data.title1) == 0:
                data.title1 = mls.UI_CORP_TITLES_UNTITLED1
            if data.title2 is not None and len(data.title2) == 0:
                data.title2 = mls.UI_CORP_TITLES_UNTITLED2
            if data.title3 is not None and len(data.title3) == 0:
                data.title3 = mls.UI_CORP_TITLES_UNTITLED3
            if data.title4 is not None and len(data.title4) == 0:
                data.title4 = mls.UI_CORP_TITLES_UNTITLED4
            if data.title5 is not None and len(data.title5) == 0:
                data.title5 = mls.UI_CORP_TITLES_UNTITLED5
            if data.title6 is not None and len(data.title6) == 0:
                data.title6 = mls.UI_CORP_TITLES_UNTITLED6
            if data.title7 is not None and len(data.title7) == 0:
                data.title7 = mls.UI_CORP_TITLES_UNTITLED7
            if data.title8 is not None and len(data.title8) == 0:
                data.title8 = mls.UI_CORP_TITLES_UNTITLED8
            if data.title9 is not None and len(data.title9) == 0:
                data.title9 = mls.UI_CORP_TITLES_UNTITLED9
            if data.title10 is not None and len(data.title10) == 0:
                data.title10 = mls.UI_CORP_TITLES_UNTITLED10
            if data.title11 is not None and len(data.title11) == 0:
                data.title11 = mls.UI_CORP_TITLES_UNTITLED11
            if data.title12 is not None and len(data.title12) == 0:
                data.title12 = mls.UI_CORP_TITLES_UNTITLED12
            if data.title13 is not None and len(data.title13) == 0:
                data.title13 = mls.UI_CORP_TITLES_UNTITLED13
            if data.title14 is not None and len(data.title14) == 0:
                data.title14 = mls.UI_CORP_TITLES_UNTITLED14
            if data.title15 is not None and len(data.title15) == 0:
                data.title15 = mls.UI_CORP_TITLES_UNTITLED15
            if data.title16 is not None and len(data.title16) == 0:
                data.title16 = mls.UI_CORP_TITLES_UNTITLED16
        return data



    def GetMemberTrackingInfo(self):
        if eve.session.corprole & const.corpRoleDirector:
            return self.GetCorpRegistry().GetMemberTrackingInfo()
        else:
            return self.GetCorpRegistry().GetMemberTrackingInfoSimple()



    def GetRentalDetailsPlayer(self):
        return self.GetCorpRegistry().GetRentalDetailsPlayer()



    def GetRentalDetailsCorp(self):
        return self.GetCorpRegistry().GetRentalDetailsCorp()



    def GetBulletins(self, isAlliance = False):
        if isAlliance:
            bulletins = sm.GetService('alliance').GetAllianceBulletins()
        else:
            bulletins = self.GetCorpBulletins()
        bulletinsList = []
        for dbrow in bulletins:
            b = util.KeyVal(dbrow)
            bulletinsList.append(b)

        bulletinsList.sort(lambda x, y: cmp(y.editDateTime, x.editDateTime))
        return bulletinsList



    def GetCorpBulletins(self):
        if self.bulletins is None or self.bulletinsTimestamp < blue.os.GetTime():
            self.bulletins = self.GetCorpRegistry().GetBulletins()
            self.bulletinsTimestamp = blue.os.GetTime() + 15 * MIN
        return self.bulletins



    def GetFormattedBulletins(self, isAlliance = False):
        canEditCorp = const.corpRoleChatManager & session.corprole == const.corpRoleChatManager
        bulletins = self.GetBulletins(isAlliance)
        txt = ''
        for b in bulletins:
            postedBy = mls.UI_CORP_BULLETINPOSTEDBY % {'id': b.editCharacterID,
             'name': cfg.eveowners.Get(b.editCharacterID).name,
             'date': util.FmtDate(b.editDateTime, 'ls')}
            editLinks = ''
            if canEditCorp:
                editLinks = mls.UI_CORP_BULLETINEDITLINKS % {'id': b.bulletinID}
            txt += "\n                <h3>%s</h3>\n                <p style='padding-right:10px'>%s</p>\n                <div align=right style='padding-right:10px; color:white'>%s%s</div>\n                <hr style='margin-top: 5px; margin-bottom: 14px'>\n                " % (b.title,
             b.body,
             postedBy,
             editLinks)

        if txt == '':
            txt = '<h3>%s</h3>' % mls.UI_CORP_NOBULLETINS
        return '<html><body>%s</body></html>' % txt



    def GetBulletin(self, bulletinID):

        def FindBulletin(id, bulletins):
            bulletin = None
            for b in bulletins:
                if b.bulletinID == id:
                    bulletin = b
                    break

            return bulletin


        bulletin = None
        if bulletinID is not None:
            ownerID = session.corpid
            bulletins = self.GetBulletins()
            bulletin = FindBulletin(bulletinID, bulletins)
            if bulletin is None and session.allianceid:
                bulletins = self.GetBulletins(isAlliance=True)
                bulletin = FindBulletin(bulletinID, bulletins)
                ownerID = session.allianceid
            if bulletin is None:
                raise UserError('CorpBulletinNotFound')
        return bulletin



    def EditBulletin(self, id, isAlliance = False):
        if not const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_DO_NOT_HAVE_ROLE_CHATMANAGER})
        bulletin = self.GetBulletin(id)
        if bulletin and bulletin.ownerID == session.allianceid:
            isAlliance = True
        wnd = sm.GetService('window').GetWindow('EditCorpBulletin')
        if wnd:
            wnd.SelfDestruct()
        sm.GetService('window').GetWindow('EditCorpBulletin', 1, isAlliance=isAlliance, bulletin=bulletin)



    def DeleteBulletin(self, id):
        if not const.corpRoleChatManager & eve.session.corprole == const.corpRoleChatManager:
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_DO_NOT_HAVE_ROLE_CHATMANAGER})
        if uicore.Message('ConfirmDeleteBulletin', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return 
        bulletin = self.GetBulletin(id)
        if bulletin.ownerID == session.allianceid:
            sm.GetService('alliance').GetMoniker().DeleteBulletin(id)
        else:
            self.GetCorpRegistry().DeleteBulletin(id)
        self.RefreshBulletins()



    def AddBulletin(self, title, body, isAlliance):
        if len(self.GetBulletins(isAlliance)) >= MAX_NUM_BULLETINS:
            eve.Message('CorpTooManyBulletins')
            return 
        if isAlliance:
            sm.GetService('alliance').GetMoniker().AddBulletin(title, body)
        else:
            self.GetCorpRegistry().AddBulletin(title, body)
        self.RefreshBulletins()



    def UpdateBulletin(self, bulletinID, title, body, isAlliance, editDateTime = None):
        try:
            if isAlliance:
                sm.GetService('alliance').GetMoniker().AddBulletin(title, body, bulletinID=bulletinID, editDateTime=editDateTime)
            else:
                self.GetCorpRegistry().AddBulletin(title, body, bulletinID=bulletinID, editDateTime=editDateTime)
        except UserError as e:
            eve.Message(e.msg, e.dict)
        self.RefreshBulletins()



    def RefreshBulletins(self):
        self.bulletins = None
        sm.GetService('alliance').bulletins = None
        sm.GetService('corpui').ResetWindow(1)



    def OnLockedItemChange(self, itemID, ownerID, locationID, change):
        self.itemLocking.OnLockedItemChange(itemID, ownerID, locationID, change)



    def GetLockedItemsByLocation(self, locationID):
        return self.itemLocking.GetLockedItemsByLocation(locationID)



    def GetLockedItemLocations(self):
        return self.itemLocking.GetLockedItemLocations()



    def IsItemLocked(self, item):
        return self.itemLocking.IsItemLocked(item)



    def IsItemIDLocked(self, itemID):
        return self.itemLocking.IsItemIDLocked(itemID)



    def GetRecruitmentAdTypes(self):
        if self._Corporation__recruitmentAdTypes is None:
            self._GetRecruitmentAdRegistryData()
        return self._Corporation__recruitmentAdTypes



    def GetRecruitmentAdGroups(self):
        if self._Corporation__recruitmentAdGroups is None:
            self._GetRecruitmentAdRegistryData()
        return self._Corporation__recruitmentAdGroups



    def _GetRecruitmentAdRegistryData(self):
        data = sm.RemoteSvc('corporationSvc').GetRecruitmentAdRegistryData()
        for row in data.types:
            row.typeName = Tr(row.typeName, 'corporation.recruitmentTypes.typeName', row.dataID)
            row.description = Tr(row.description, 'corporation.recruitmentTypes.description', row.dataID)
            row.groupName = Tr(row.groupName, 'corporation.recruitmentGroups.groupName', row.groupDataID)

        for row in data.groups:
            row.groupName = Tr(row.groupName, 'corporation.recruitmentGroups.groupName', row.dataID)
            row.description = Tr(row.description, 'corporation.recruitmentGroups.description', row.dataID)

        self._Corporation__recruitmentAdTypes = data.types
        self._Corporation__recruitmentAdGroups = data.groups



    def GetContactList(self):
        if util.IsNPC(session.corpid):
            return {}
        return self.GetCorpRegistry().GetCorporateContacts()



    def AddCorporateContact(self, contactID, relationshipID):
        self.GetCorpRegistry().AddCorporateContact(contactID, relationshipID)



    def EditCorporateContact(self, contactID, relationshipID):
        self.GetCorpRegistry().EditCorporateContact(contactID, relationshipID)



    def RemoveCorporateContacts(self, contactIDs):
        self.GetCorpRegistry().RemoveCorporateContacts(contactIDs)



    def EditContactsRelationshipID(self, contactIDs, relationshipID):
        self.GetCorpRegistry().EditContactsRelationshipID(contactIDs, relationshipID)



    def GetLabels(self):
        return self.GetCorpRegistry().GetLabels()



    def CreateLabel(self, name, color = 0):
        return self.GetCorpRegistry().CreateLabel(name, color)



    def DeleteLabel(self, labelID):
        self.GetCorpRegistry().DeleteLabel(labelID)



    def EditLabel(self, labelID, name = None, color = None):
        self.GetCorpRegistry().EditLabel(labelID, name, color)



    def AssignLabels(self, contactIDs, labelMask):
        self.GetCorpRegistry().AssignLabels(contactIDs, labelMask)



    def RemoveLabels(self, contactIDs, labelMask):
        self.GetCorpRegistry().RemoveLabels(contactIDs, labelMask)




