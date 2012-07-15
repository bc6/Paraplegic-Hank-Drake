#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/ActionObjectClient.py
import svc

class ActionObjectClientSvc(svc.actionObjectSvc):
    __guid__ = 'svc.actionObjectClientSvc'
    __displayname__ = 'ActionObject Service'
    __machoresolve__ = 'location'
    __notifyevents__ = svc.actionObjectSvc.__notifyevents__[:]
    __notifyevents__.extend(['ProcessSessionChange'])

    def __init__(self):
        svc.actionObjectSvc.__init__(self)

    def Run(self, *args):
        self.actionObjectServer = None
        svc.actionObjectSvc.Run(self, *args)
        self.zactionClient = sm.GetService('zactionClient')

    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            if self.actionObjectServer is None:
                self.actionObjectServer = sm.RemoteSvc('actionObjectServerSvc')

    def GetActionList(self, entID, objectID):
        returnDict = {}
        actionList = self.manager.GetAllAvailableActions(objectID)
        if actionList is not None and len(actionList) > 0:
            tree = self.zactionClient.GetActionTree()
            entity = self.entityService.FindEntityByID(entID)
            treeInst = entity.GetComponent('action').treeInstance
            for action in actionList:
                returnDict[action] = []
                actionNodeName = tree.GetTreeNodeByID(action).name
                translatedName = self.GetActionNodeTranslatedText(action, actionNodeName)
                returnDict[action].append(translatedName)
                returnDict[action].append(treeInst.IsActionAvailable(action, {'TargetList': [objectID]}))
                returnDict[action].append(actionNodeName)

        return returnDict

    def IsEntityUsingActionObject(self, entID):
        return self.manager.IsEntityUsingActionObject(entID)

    def ExitActionObject(self, entID):
        aoEntID = self.manager.GetAOEntIDUsedByEntity(entID)
        if aoEntID:
            self.TriggerDefaultActionOnObject(entID, aoEntID)

    def TriggerActionOnObject(self, entID, targetID, actionID):
        self.zactionClient.StartAction(entID, actionID, {'TargetList': [targetID]})

    def GetDefaultActionID(self, entID, targetID):
        actionList = self.GetActionList(entID, targetID)
        if not actionList:
            return
        isEnabled = False
        defaultActionID = None
        for actionID, actionData in actionList.items():
            if actionData[1] is True:
                isEnabled = True
                defaultActionID = actionID
                break

        return (isEnabled, defaultActionID)

    def TriggerDefaultActionOnObject(self, entID, targetID):
        isEnabled, actionID = self.GetDefaultActionID(entID, targetID)
        if isEnabled:
            self.TriggerActionOnObject(entID, targetID, actionID)