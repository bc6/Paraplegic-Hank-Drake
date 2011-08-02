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
import decisionProcs

class ClientDecisionTreeComponent(zaction.ClientActionComponent):
    __guid__ = 'ai.ClientDecisionComponent'


class DecisionTreeClient(zaction.zactionCommonBase):
    __guid__ = 'svc.decisionTreeClient'
    __notifyevents__ = zaction.zactionCommonBase.__notifyevents__[:]
    __notifyevents__.extend(['ProcessSessionChange'])
    __dependencies__ = ['zactionClient']
    __componentTypes__ = ['decision']

    @classmethod
    def GetTreeSystemID(cls):
        return const.ztree.TREE_SYSTEM_ID_DICT[const.ai.AI_SCHEMA]



    def __init__(self):
        self.decisionTreeServer = None
        treeManager = GameWorld.DecisionTreeManager()
        treeManager.Initialize()
        zaction.zactionCommon.__init__(self, treeManager)
        GameWorld.RegisterPythonActionProc('ForceDecisionTreeToRoot', decisionProcs.ForceDecisionTreeToRoot, ('ENTID',))



    def Run(self, *etc):
        zaction.zactionCommonBase.Run(self, etc)



    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            if not self.decisionTreeServer:
                self.decisionTreeServer = sm.RemoteSvc('decisionTreeServer')
                self.SetupActionTree(self.GetTreeSystemID())



    def PackUpForClientTransfer(self, component):
        treeNode = component.treeInstance.GetCurrentTreeNode()
        if treeNode is not None:
            action = treeNode.ID
        else:
            action = component.rootID
        state = {'rootID': component.rootID,
         'TreeInstance': component.treeInstance}
        return state



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        pass



    def UnPackFromSceneTransfer(self, component, entity, state):
        if state is not None:
            component.rootID = state['rootID']
            if 'TreeInstance' in state:
                component.treeInstance = state['TreeInstance']
            elif 'TreeState' in state:
                component.treeState = state.get('TreeState')
                component.stepState = state.get('StepState')



    def CreateComponent(self, name, state):
        component = ClientDecisionTreeComponent(state)
        component.rootID = state.get('rootID', None)
        component.TreeInstanceID = state.get('TreeInstanceID', const.ztree.GENERATE_TREE_INSTANCE_ID)
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        if not self.actionTickManager:
            self.LogError('ActionTickManager was not present at buff prepare component, things will now crash')
        if component.rootID == None:
            return 
        if component.treeInstance is None:
            component.treeInstance = GameWorld.DecisionTreeInstance(entityID, component.TreeInstanceID)
        component.rootNode = self.treeManager.GetTreeNodeByID(component.rootID)



    def SetupComponent(self, entity, component):
        pass



    def RegisterComponent(self, entity, component):
        if component.rootID == None:
            list = self.rootNode.GetChildren()
            component.rootID = list[0][1].ID
            component.treeInstance = GameWorld.DecisionTreeInstance(entity.entityID, component.TreeInstanceID)
        self.treeManager.AddTreeInstance(component.treeInstance)
        if component.treeState is not None and component.stepState is not None:
            component.treeInstance.SetTreeState(*component.treeState)
            component.treeInstance.SetStepState(*component.stepState)
            component.treeState = None
            component.stepState = None
        elif component.treeInstance.IsActionEnded():
            treeNode = self.treeManager.GetTreeNodeByID(component.rootID)
            if treeNode is not None:
                component.treeInstance.ForceAction(treeNode)



    def UnRegisterComponent(self, entity, component):
        self.treeManager.RemoveTreeInstance(component.treeInstance)



    def TearDownComponent(self, entity, component):
        pass




