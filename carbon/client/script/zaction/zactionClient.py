import blue
import GameWorld
import log
import service
import stackless
import sys
import util
import uicls
import uiutil
import uthread
import zaction

class ClientActionComponent:
    __guid__ = 'zaction.ClientActionComponent'

    def __init__(self, state):
        self.rootID = 0
        self.treeState = None
        self.stepState = None
        self.treeInstance = None
        self.TreeInstanceID = const.ztree.GENERATE_TREE_INSTANCE_ID
        self.defaultAction = int(state.get(const.zaction.ACTIONTREE_RECIPE_DEFAULT_ACTION_NAME, sm.GetService('zactionClient').defaultAction))



    def GetDefaultAction(self):
        return self.defaultAction




class zactionClient(zaction.zactionCommon):
    __guid__ = 'svc.zactionClient'
    __notifyevents__ = zaction.zactionCommon.__notifyevents__[:]
    __notifyevents__.extend(['ProcessSessionChange',
     'OnEntityActionStart',
     'OnActionStepUpdate',
     'OnActionForce',
     'OnPropertyUpdate'])
    __componentTypes__ = ['action']

    def __init__(self):
        self.zactionServer = None
        self.clientProperties = {}
        treeManager = GameWorld.ActionTreeManagerClient()
        treeManager.Initialize()
        treeManager.EnableBlueNet()
        zaction.zactionCommon.__init__(self, treeManager)



    def Run(self, *etc):
        zaction.zactionCommon.Run(self, etc)



    def GetClientProperties(self):
        return self.clientProperties



    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            if not self.zactionServer:
                self.zactionServer = sm.RemoteSvc('zactionServer')
                self.defaultAction = self.zactionServer.GetDefaultStartingAction()
                self.SetupActionTree(self.GetTreeSystemID())



    def PackUpForClientTransfer(self, component):
        treeNode = component.treeInstance.GetCurrentTreeNode()
        if treeNode is not None:
            action = treeNode.ID
        else:
            action = component.rootID
        state = {'rootID': component.rootID,
         'actionID': action,
         'TreeInstance': component.treeInstance,
         const.zaction.ACTIONTREE_RECIPE_DEFAULT_ACTION_NAME: component.defaultAction}
        return state



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return self.PackUpForClientTransfer(component)



    def UnPackFromSceneTransfer(self, component, entity, state):
        return component



    def CreateComponent(self, name, state):
        component = ClientActionComponent(state)
        if state is not None:
            component.rootID = state.get('rootID', component.rootID)
            if 'TreeInstance' in state:
                component.treeInstance = state['TreeInstance']
            elif 'TreeState' in state:
                component.treeState = state.get('TreeState')
                component.stepState = state.get('StepState')
                component.TreeInstanceID = state.get('TreeInstanceID', const.ztree.GENERATE_TREE_INSTANCE_ID)
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if not self.actionTickManager:
            self.LogError('ActionTickManager was not present at zaction prepare component, things will now crash')
        if component.treeInstance is None:
            if self.entityService.IsClientSideOnly(sceneID):
                component.treeInstance = GameWorld.ActionTreeInstance(entityID, component.TreeInstanceID)
            else:
                component.treeInstance = GameWorld.ActionTreeInstanceClient(entityID, component.TreeInstanceID)
        component.rootNode = self.treeManager.GetTreeNodeByID(component.rootID)



    def SetupComponent(self, entity, component):
        pass



    def RegisterComponent(self, entity, component):
        self.treeManager.AddTreeInstance(component.treeInstance)
        if component.treeState is not None and component.stepState is not None:
            component.treeInstance.SetTreeState(*component.treeState)
            component.treeInstance.SetStepState(*component.stepState)
            component.treeState = None
            component.stepState = None
        elif component.treeInstance.IsActionEnded():
            treeNode = self.treeManager.GetTreeNodeByID(component.GetDefaultAction())
            if treeNode is not None:
                component.treeInstance.ForceAction(treeNode)



    def UnRegisterComponent(self, entity, component):
        self.treeManager.RemoveTreeInstance(component.treeInstance)



    def TearDownComponent(self, entity, component):
        component.treeInstance = None



    def StartAction(self, entID, actionID, clientProps = None, interrupt = True):
        if actionID == None:
            return 
        actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
        if actionTreeInst is not None:
            if clientProps is None:
                clientProps = self.GetClientProperties()
            entity = self.entityService.FindEntityByID(entID)
            if not self.entityService.IsClientSideOnly(entity.scene.sceneID):
                uthread.new(self.zactionServer.RequestActionStart, entID, actionID, interrupt, self.GetClientProperties())
            actionTreeInst.DoActionByID(actionID, interrupt, clientProps)
        else:
            self.LogError('StartAction called with ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')



    def QA_RequestForceAction(self, entID, actionID):
        actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
        if actionTreeInst is not None:
            uthread.new(self.zactionServer.QA_RequestForceActionStart, entID, actionID)
        else:
            self.LogError('StartAction called with ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')



    def OnEntityActionStart(self, entID, actionID, actionStack, propList):
        actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
        if actionTreeInst is not None:
            actionTreeInst.ActionUpdate(actionID, actionStack, propList, False)
        else:
            self.LogError('Received OnEntityActionStart ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')



    def OnActionStepUpdate(self, entID, actionID, stepStack):
        actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
        if actionTreeInst is not None:
            actionTreeInst.ActionStepUpdate(actionID, stepStack)
        else:
            self.LogError('Received OnActionStepUpdate ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')



    def OnActionForce(self, entID, actionID, actionStack, propList):
        entity = self.entityService.FindEntityByID(entID)
        if entity is not None:
            actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
            if actionTreeInst is not None:
                actionTreeInst.ActionUpdate(actionID, actionStack, propList, True)
            else:
                self.LogError('Received OnActionFail ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')



    def OnPropertyUpdate(self, entID, actionID, propList):
        entity = self.entityService.FindEntityByID(entID)
        if entity is not None:
            actionTreeInst = self.treeManager.GetTreeInstanceByEntID(entID)
            if actionTreeInst is not None:
                actionTreeInst.UpdateProperty(actionID, propList)
            else:
                self.LogError('Received OnPropertyUpdate ' + str(entID) + ', ' + str(actionID) + ', but could not find entity tree instance.')




