import service
import blue
import util
import types
import uix
import listentry
import uiconst

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
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_NEED_ROLE_PERS_MAN_OR_DIRECT})
        if len(title) > const.medalMaxNameLength:
            raise UserError('MedalNameTooLong', {'maxLength': str(const.medalMaxNameLength)})
        if len(description) > const.medalMaxDescriptionLength:
            raise UserError('MedalDescriptionTooLong', {'maxLength': str(const.medalMaxDescriptionLength)})
        closeParent = True
        try:
            try:
                sm.RemoteSvc('corporationSvc').CreateMedal(title, description, graphics)
            except UserError as e:
                if e.args[0] == 'ConfirmCreatingMedal':
                    d = dict(cost='<b>%s</b>' % util.FmtISK(e.dict.get('cost', 0)))
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
                    b = e.dict.get('balance', (0, 0))
                    a = e.dict.get('amount', (0, 0))
                    d = dict(balance='<b>%s</b>' % util.FmtISK(b[1]), amount='<b>%s</b>' % util.FmtISK(a[1]))
                    ret = eve.Message(e.msg, d)
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
        return sm.RemoteSvc('corporationSvc').GetAllCorpMedals(corpID)



    def GetRecipientsOfMedal(self, medalID):
        return sm.RemoteSvc('corporationSvc').GetRecipientsOfMedal(medalID)



    def GetMedalsReceivedWithFlag(self, characterID, status = None):
        if status is None:
            status = [2, 3]
        ret = {}
        medals = self.GetMedalsReceived(characterID)
        (medalInfo, medalGraphics,) = medals
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
            raise UserError('CrpAccessDenied', {'reason': mls.UI_CORP_NEED_ROLE_PERS_MAN_OR_DIRECT})
        if reason == '':
            ret = uix.NamePopup(mls.UI_GENERIC_AWARDREASON, mls.UI_GENERIC_ENTERREASON, reason, maxLength=200)
            if ret:
                reason = ret['name']
            else:
                return 
        if type(recipientID) == types.IntType:
            recipientID = [recipientID]
        try:
            sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason)
        except UserError as e:
            if e.args[0].startswith('ConfirmGivingMedal'):
                d = dict(amount=len(recipientID), members=uix.Plural(len(recipientID), 'UI_GENERIC_MEMBER').lower(), cost='<b>%s</b>' % util.FmtISK(e.dict.get('cost', 0)))
                ret = eve.Message(e.msg, d, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret == uiconst.ID_YES:
                    sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason, True)
            elif e.args[0] == 'NotEnoughMoney':
                b = e.dict.get('balance', (0, 0))
                a = e.dict.get('amount', (0, 0))
                d = dict(balance='<b>%s</b>' % util.FmtISK(b[1]), amount='<b>%s</b>' % util.FmtISK(a[1]))
                ret = eve.Message(e.msg, d)
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




