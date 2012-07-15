#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/mail/mailingListsSvc.py
import service
import blue
import util
import uix
import uiutil

class MailingLists(service.Service):
    __exportedcalls__ = {'GetDisplayName': [],
     'GetMyMailingLists': [],
     'CreateMailingList': [],
     'JoinMailingList': [],
     'LeaveMaillist': [],
     'DeleteMaillist': [],
     'GetMembers': [],
     'KickMembers': [],
     'SetEntityAccess': [],
     'ClearEntityAccess': [],
     'SetMembersMuted': [],
     'SetMembersOperator': [],
     'SetMembersClear': [],
     'SetDefaultAccess': [],
     'GetSettings': [],
     'GetWelcomeMail': [],
     'SaveWelcomeMail': [],
     'SaveAndSendWelcomeMail': [],
     'ClearWelcomeMail': []}
    __guid__ = 'svc.mailinglists'
    __servicename__ = 'mailinglists'
    __displayname__ = 'Mailing Lists'
    __notifyevents__ = ['OnMailingListSetOperator',
     'OnMailingListSetMuted',
     'OnMailingListSetClear',
     'OnMailingListLeave',
     'OnMailingListDeleted']

    def __init__(self):
        service.Service.__init__(self)
        self.myMailingLists = None

    def Run(self, memStream = None):
        self.state = service.SERVICE_START_PENDING
        self.LogInfo('Starting Mailing Lists Svc')
        self.objectCaching = sm.services['objectCaching']
        self.mailingListsMgr = sm.RemoteSvc('mailingListsMgr')
        self.myMailingLists = self.mailingListsMgr.GetJoinedLists()
        self.externalLists = {}
        self.state = service.SERVICE_RUNNING

    def GetMyMailingLists(self):
        return self.myMailingLists

    def GetDisplayName(self, listID):
        if listID in self.myMailingLists:
            return self.myMailingLists[listID].displayName
        if listID in self.externalLists:
            return self.externalLists[listID].displayName
        info = self.mailingListsMgr.GetInfo(listID)
        if info is None:
            raise UserError('MailingListNoSuchList')
        self.externalLists[listID] = info
        return info.displayName

    def CreateMailingList(self, name, defaultAccess = const.mailingListAllowed, defaultMemberAccess = const.mailingListMemberDefault, cost = 0):
        ret = sm.RemoteSvc('mailingListsMgr').Create(name, defaultAccess, defaultMemberAccess, cost)
        key, displayName = util.GetKeyAndNormalize(name)
        self.myMailingLists[ret] = util.KeyVal(name=key, displayName=displayName, isMuted=False, isOperator=False, isOwner=True)
        sm.ScatterEvent('OnMyMaillistChanged')
        return ret

    def JoinMailingList(self, name):
        ret = self.mailingListsMgr.Join(name)
        self.myMailingLists[ret.id] = ret
        sm.ScatterEvent('OnMyMaillistChanged')
        return ret.id

    def LeaveMaillist(self, listID):
        self.mailingListsMgr.Leave(listID)
        try:
            del self.myMailingLists[listID]
        except KeyError:
            pass

        sm.ScatterEvent('OnMyMaillistChanged')

    def DeleteMaillist(self, listID):
        self.mailingListsMgr.Delete(listID)
        try:
            del self.myMailingLists[listID]
        except KeyError:
            pass

        sm.ScatterEvent('OnMyMaillistChanged')

    def KickMembers(self, listID, memberIDs):
        self.mailingListsMgr.KickMembers(listID, memberIDs)
        self.objectCaching.InvalidateCachedMethodCall('mailingListsMgr', 'GetMembers', listID)

    def GetMembers(self, listID):
        members = self.mailingListsMgr.GetMembers(listID)
        sm.GetService('mailSvc').PrimeOwners(members.keys())
        return members

    def SetEntityAccess(self, listID, entityID, access):
        self.mailingListsMgr.SetEntityAccess(listID, entityID, access)

    def ClearEntityAccess(self, listID, entityID):
        self.mailingListsMgr.ClearEntityAccess(listID, entityID)

    def SetMembersMuted(self, listID, memberIDs):
        self.mailingListsMgr.SetMembersMuted(listID, memberIDs)
        self.objectCaching.InvalidateCachedMethodCall('mailingListsMgr', 'GetMembers', listID)

    def SetMembersOperator(self, listID, memberIDs):
        self.mailingListsMgr.SetMembersOperator(listID, memberIDs)
        self.objectCaching.InvalidateCachedMethodCall('mailingListsMgr', 'GetMembers', listID)

    def SetMembersClear(self, listID, memberIDs):
        self.mailingListsMgr.SetMembersClear(listID, memberIDs)
        self.objectCaching.InvalidateCachedMethodCall('mailingListsMgr', 'GetMembers', listID)

    def SetDefaultAccess(self, listID, defaultAccess, defaultMemberAccess, mailCost = 0):
        self.mailingListsMgr.SetDefaultAccess(listID, defaultAccess, defaultMemberAccess, mailCost)

    def GetSettings(self, listID):
        return self.mailingListsMgr.GetSettings(listID)

    def OnMailingListSetOperator(self, listID):
        if listID in self.myMailingLists:
            self.myMailingLists[listID].isOperator = True
            self.myMailingLists[listID].isMuted = False

    def OnMailingListSetMuted(self, listID):
        if listID in self.myMailingLists:
            self.myMailingLists[listID].isMuted = True
            self.myMailingLists[listID].isOperator = False

    def OnMailingListSetClear(self, listID):
        if listID in self.myMailingLists:
            self.myMailingLists[listID].isMuted = False
            self.myMailingLists[listID].isOperator = False

    def OnMailingListLeave(self, listID, characterID):
        if characterID == session.charid and listID in self.myMailingLists:
            try:
                del self.myMailingLists[listID]
            except KeyError:
                pass

            sm.ScatterEvent('OnMyMaillistChanged')

    def OnMailingListDeleted(self, listID):
        if listID in self.myMailingLists:
            try:
                del self.myMailingLists[listID]
            except KeyError:
                pass

            sm.ScatterEvent('OnMyMaillistChanged')

    def GetWelcomeMail(self, listID):
        return self.mailingListsMgr.GetWelcomeMail(listID)

    def SaveWelcomeMail(self, listID, title, body):
        return self.mailingListsMgr.SaveWelcomeMail(listID, title, body)

    def SaveAndSendWelcomeMail(self, listID, title, body):
        return self.mailingListsMgr.SendWelcomeMail(listID, title, body)

    def ClearWelcomeMail(self, listID):
        self.mailingListsMgr.ClearWelcomeMail(listID)