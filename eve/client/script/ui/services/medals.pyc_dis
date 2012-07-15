#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/medals.py
import service
import util
import types
import uix
import listentry
import uiconst
import localization
import uiutil

class Medals(service.Service):
    __exportedcalls__ = {'CreateMedal': [],
     'SetMedalStatus': [],
     'GetMedalStatuses': [],
     'GetAllCorpMedals': [],
     'GetRecipientsOfMedal': [],
     'GetMedalsReceived': [],
     'GetMedalDetails': [],
     'GiveMedalToCharacters': []}
    __guid__ = 'svc.medals'
    __servicename__ = 'medals'
    __displayname__ = 'Medals'
    __dependencies__ = ['objectCaching']
    __notifyevents__ = ['OnCorporationMedalAdded', 'OnMedalIssued', 'OnMedalStatusChanged']

    def __init__(self):
        service.Service.__init__(self)

    def Run(self, memStream = None):
        self.LogInfo('Starting Medal Svc')

    def CreateMedal(self, title, description, graphics):
        roles = const.corpRoleDirector | const.corpRolePersonnelManager
        if session.corprole & roles == 0:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CreateDecorationWindow/NeedRolesError')})
        if len(title) > const.medalMaxNameLength:
            raise UserError('MedalNameTooLong', {'maxLength': str(const.medalMaxNameLength)})
        if len(description) > const.medalMaxDescriptionLength:
            raise UserError('MedalDescriptionTooLong', {'maxLength': str(const.medalMaxDescriptionLength)})
        closeParent = True
        try:
            sm.RemoteSvc('corporationSvc').CreateMedal(title, description, graphics)
        except UserError as e:
            if e.args[0] == 'ConfirmCreatingMedal':
                d = dict(cost=localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=util.FmtISK(e.dict.get('cost', 0))))
                ret = eve.Message(e.msg, d, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret == uiconst.ID_YES:
                    try:
                        sm.RemoteSvc('corporationSvc').CreateMedal(title, description, graphics, True)
                    except UserError as e:
                        if e.args[0] in ['MedalNameInvalid2', 'MedalDescriptionInvalid2']:
                            eve.Message(e.msg, e.args[1])
                            closeParent = False
                        else:
                            eve.Message(e.msg)
                            closeParent = False

            elif e.args[0] == 'NotEnoughMoney':
                eve.Message(e.msg, e.dict)
                closeParent = False
            elif e.args[0] in ['MedalNameInvalid']:
                eve.Message(e.msg)
                closeParent = False
            elif e.args[0] in ['MedalNameTooLong', 'MedalDescriptionTooLong', 'MedalDescriptionTooShort']:
                eve.Message(e.msg, e.args[1])
                closeParent = False
            else:
                raise 
        finally:
            return closeParent

    def SetMedalStatus(self, statusdict = None):
        if statusdict is None:
            return
        sm.RemoteSvc('corporationSvc').SetMedalStatus(statusdict)

    def GetMedalStatuses(self):
        return sm.RemoteSvc('corporationSvc').GetMedalStatuses()

    def GetAllCorpMedals(self, corpID):
        medals, medalDetails = sm.RemoteSvc('corporationSvc').GetAllCorpMedals(corpID)
        return [medals, medalDetails]

    def GetRecipientsOfMedal(self, medalID):
        recipients = sm.RemoteSvc('corporationSvc').GetRecipientsOfMedal(medalID)
        for recipient in recipients:
            recipient.reason = recipient.reason

        return recipients

    def GetMedalsReceivedWithFlag(self, characterID, status = None):
        if status is None:
            status = [2, 3]
        ret = {}
        medals = self.GetMedalsReceived(characterID)
        medalInfo, medalGraphics = medals
        for medal in medalInfo:
            if medal.status in status:
                if ret.has_key(medal.medalID):
                    ret[medal.medalID].append(medal)
                else:
                    ret[medal.medalID] = [medal]

        return ret

    def GetMedalsReceived(self, characterID):
        return sm.RemoteSvc('corporationSvc').GetMedalsReceived(characterID)

    def GetMedalDetails(self, medalID):
        return sm.RemoteSvc('corporationSvc').GetMedalDetails(medalID)

    def GiveMedalToCharacters(self, medalID, recipientID, reason = ''):
        roles = const.corpRoleDirector | const.corpRolePersonnelManager
        if session.corprole & roles == 0:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CreateDecorationWindow/NeedRolesError')})
        if reason == '':
            ret = uiutil.NamePopup(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/AwardReasonTitle'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/PromptForReason'), reason, maxLength=200)
            if ret:
                reason = ret
            else:
                return
        if type(recipientID) == types.IntType:
            recipientID = [recipientID]
        try:
            sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason)
        except UserError as e:
            if e.args[0].startswith('ConfirmGivingMedal'):
                d = dict(amount=len(recipientID), members=localization.GetByLabel('UI/Corporations/MedalsToUsers', numMembers=len(recipientID)), cost=util.FmtISK(e.dict.get('cost', 0)))
                ret = eve.Message(e.msg, d, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret == uiconst.ID_YES:
                    sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason, True)
            elif e.args[0] == 'NotEnoughMoney':
                eve.Message(e.msg, e.dict)
            else:
                raise 

    def OnCorporationMedalAdded(self, *args):
        invalidate = [('corporationSvc', 'GetAllCorpMedals', (session.corpid,)), ('corporationSvc', 'GetRecipientsOfMedal', (args[0],))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        sm.StartService('corpui').OnCorporationMedalAdded()

    def OnMedalIssued(self, *args):
        invalidate = [('corporationSvc', 'GetMedalsReceived', (session.charid,))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        sm.ScatterEvent('OnUpdatedMedalsAvailable')

    def OnMedalStatusChanged(self, *args):
        invalidate = [('corporationSvc', 'GetMedalsReceived', (session.charid,))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        sm.ScatterEvent('OnUpdatedMedalStatusAvailable')


class DecorationPermissionsEntry(listentry.PermissionEntry):
    __guid__ = 'listentry.DecorationPermissions'
    __params__ = ['label', 'itemID']

    def ApplyAttributes(self, attributes):
        listentry.PermissionEntry.ApplyAttributes(self, attributes)
        self.columns = [2, 3, 1]

    def Startup(self, *args):
        listentry.PermissionEntry.Startup(self)

    def Load(self, node):
        listentry.PermissionEntry.Load(self, node)