from service import Service, SERVICE_START_PENDING, SERVICE_RUNNING
import blue
import moniker
import allianceObject

def ReturnNone():
    return None



class Alliances(Service):
    __exportedcalls__ = {'GetAlliance': [],
     'UpdateAlliance': [],
     'GetRankedAlliances': [],
     'GetApplications': [],
     'UpdateApplication': [],
     'GetMembers': [],
     'DeclareExecutorSupport': [],
     'DeleteMember': [],
     'GetRelationships': [],
     'SetRelationship': [],
     'DeleteRelationship': [],
     'RetractWar': [],
     'DeclareWarAgainst': [],
     'ChangeMutualWarFlag': [],
     'PayBill': [],
     'GetBillBalance': [],
     'GetBills': [],
     'GetBillsReceivable': [],
     'GetContactList': []}
    __guid__ = 'svc.alliance'
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnAllianceChanged',
     'OnAllianceApplicationChanged',
     'OnAllianceMemberChanged',
     'OnAllianceRelationshipChanged']
    __servicename__ = 'alliance'
    __displayname__ = 'Alliance Client Service'
    __dependencies__ = []
    __functionalobjects__ = ['alliance',
     'members',
     'applications',
     'relationships']

    def __init__(self):
        Service.__init__(self)



    def GetDependencies(self):
        return self.__dependencies__



    def GetObjectNames(self):
        return self.__functionalobjects__



    def Run(self, memStream = None):
        self.LogInfo('Starting Alliances')
        self.bulletins = None
        self.bulletinsTimestamp = 0
        self.state = SERVICE_START_PENDING
        self._Alliances__allianceMoniker = None
        self._Alliances__allianceMonikerAllianceID = None
        items = allianceObject.__dict__.items()
        for objectName in self.__functionalobjects__:
            if objectName == 'base':
                continue
            object = None
            classType = 'allianceObject.%s' % objectName
            for i in range(0, len(allianceObject.__dict__)):
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
        if eve.session.allianceid is not None:
            self.GetMoniker()



    def Stop(self, memStream = None):
        self._Alliances__allianceMoniker = None
        self._Alliances__allianceMonikerAllianceID = None



    def RefreshMoniker(self):
        if self._Alliances__allianceMoniker is not None:
            self._Alliances__allianceMoniker = None
            self._Alliances__allianceMonikerAllianceID = None



    def GetMoniker(self):
        if self._Alliances__allianceMoniker is None:
            self._Alliances__allianceMoniker = moniker.GetAlliance()
            self._Alliances__allianceMonikerAllianceID = eve.session.allianceid
            self._Alliances__allianceMoniker.Bind()
        if self._Alliances__allianceMonikerAllianceID != eve.session.allianceid:
            if self._Alliances__allianceMoniker is not None:
                self._Alliances__allianceMoniker = None
            self._Alliances__allianceMoniker = moniker.GetAlliance()
            self._Alliances__allianceMonikerAllianceID = eve.session.allianceid
            self._Alliances__allianceMoniker.Bind()
        return self._Alliances__allianceMoniker



    def DoSessionChanging(self, isRemote, session, change):
        if 'corprole' in change:
            (old, new,) = change['corprole']
            if old & const.corpRoleDirector != new & const.corpRoleDirector:
                self.members.members = None
        for objectname in self.__functionalobjects__:
            function = getattr(objectname, 'DoSessionChanging', None)
            if function is None:
                self.LogInfo(objectname, 'DOES NOT PROCESS DoSessionChanging')
            else:
                function(isRemote, session, change)

        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            sm.StopService(self.__guid__[4:])



    def OnSessionChanged(self, isremote, sess, change):
        if 'allianceid' in change:
            (oldID, newID,) = change['allianceid']
            self.bulletins = None
            self.bulletinsTimestamp = 0
            if newID is not None:
                self.GetMoniker()
            else:
                self.RefreshMoniker()



    def OnAllianceChanged(self, allianceID, change):
        self.alliance.OnAllianceChanged(allianceID, change)
        self.members.ResetMembers()



    def GetAlliance(self, allianceID = None):
        return self.alliance.GetAlliance(allianceID)



    def UpdateAlliance(self, description, url):
        return self.alliance.UpdateAlliance(description, url)



    def GetRankedAlliances(self, maxLen = 100):
        return self.alliance.GetRankedAlliances(maxLen)



    def GetApplications(self, showRejected = False):
        return self.applications.GetApplications(showRejected)



    def UpdateApplication(self, corpID, applicationText, state):
        return self.applications.UpdateApplication(corpID, applicationText, state)



    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if allianceID == eve.session.allianceid:
            self.applications.OnAllianceApplicationChanged(allianceID, corpID, change)



    def GetMembers(self):
        return self.members.GetMembers()



    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        if allianceID == eve.session.allianceid:
            self.members.OnAllianceMemberChanged(allianceID, corpID, change)



    def DeclareExecutorSupport(self, corpID):
        self.members.DeclareExecutorSupport(corpID)



    def DeleteMember(self, corpID):
        self.members.DeleteMember(corpID)



    def GetRelationships(self):
        return self.relationships.Get()



    def SetRelationship(self, relationship, toID):
        return self.relationships.Set(relationship, toID)



    def DeleteRelationship(self, toID):
        return self.relationships.Delete(toID)



    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        if allianceID == eve.session.allianceid:
            self.relationships.OnAllianceRelationshipChanged(allianceID, toID, change)
            sm.ChainEvent('ProcessOnUIAllianceRelationshipChanged', allianceID, toID, change)



    def RetractWar(self, againstID):
        return self.GetMoniker().RetractWar(againstID)



    def DeclareWarAgainst(self, againstID):
        return self.GetMoniker().DeclareWarAgainst(againstID)



    def ChangeMutualWarFlag(self, warID, mutual):
        return self.GetMoniker().ChangeMutualWarFlag(warID, mutual)



    def PayBill(self, billID, fromAccountKey):
        if not const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToPayBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().PayBill(billID, fromAccountKey)



    def GetBillBalance(self, billID):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBillBalance')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBillBalance(billID)



    def GetBills(self):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBills()



    def GetBillsReceivable(self):
        if const.corpRoleAccountant & eve.session.corprole == const.corpRoleAccountant:
            pass
        elif const.corpRoleJuniorAccountant & eve.session.corprole == const.corpRoleJuniorAccountant:
            pass
        else:
            reason = localization.GetByLabel('UI/Corporations/AccessRestrictions/AccountantToViewBills')
            raise UserError('CrpAccessDenied', {'reason': reason})
        return self.GetMoniker().GetBillsReceivable()



    def GetAllianceBulletins(self):
        if self.bulletins is None or self.bulletinsTimestamp < blue.os.GetWallclockTime():
            self.bulletins = self.GetMoniker().GetBulletins()
            self.bulletinsTimestamp = blue.os.GetWallclockTime() + 15 * MIN
        return self.bulletins



    def GetContactList(self):
        if not session.allianceid:
            return {}
        return self.GetMoniker().GetAllianceContacts()



    def AddAllianceContact(self, contactID, relationshipID):
        self.GetMoniker().AddAllianceContact(contactID, relationshipID)



    def EditAllianceContact(self, contactID, relationshipID):
        self.GetMoniker().EditAllianceContact(contactID, relationshipID)



    def RemoveAllianceContacts(self, contactIDs):
        self.GetMoniker().RemoveAllianceContacts(contactIDs)



    def EditContactsRelationshipID(self, contactIDs, relationshipID):
        self.GetMoniker().EditContactsRelationshipID(contactIDs, relationshipID)



    def GetLabels(self):
        return self.GetMoniker().GetLabels()



    def CreateLabel(self, name, color = 0):
        return self.GetMoniker().CreateLabel(name, color)



    def DeleteLabel(self, labelID):
        self.GetMoniker().DeleteLabel(labelID)



    def EditLabel(self, labelID, name = None, color = None):
        self.GetMoniker().EditLabel(labelID, name, color)



    def AssignLabels(self, contactIDs, labelMask):
        self.GetMoniker().AssignLabels(contactIDs, labelMask)



    def RemoveLabels(self, contactIDs, labelMask):
        self.GetMoniker().RemoveLabels(contactIDs, labelMask)




