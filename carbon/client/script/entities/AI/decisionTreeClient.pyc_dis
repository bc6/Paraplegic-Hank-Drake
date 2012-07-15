#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/AI/decisionTreeClient.py
import blue
import GameWorld
import log
import service
import stackless
import sys
import util
import zaction
import decisionProcs
import ai

class DecisionTreeClient(ai.decisionTreeCommon):
    __guid__ = 'svc.decisionTreeClient'
    __notifyevents__ = zaction.zactionCommonBase.__notifyevents__[:]
    __notifyevents__.extend(['ProcessSessionChange'])
    __dependencies__ = ['zactionClient']

    def __init__(self):
        ai.decisionTreeCommon.__init__(self)
        self.decisionTreeIsSetup = False

    def Run(self, *etc):
        zaction.zactionCommonBase.Run(self, etc)

    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change:
            if not self.decisionTreeIsSetup:
                self.decisionTreeIsSetup = True
                self.SetupActionTree(self.GetTreeSystemID())

    def CreateComponent(self, name, state):
        component = ai.DecisionComponent(state)
        component.rootIDs = [None] * const.ai.DECISION_MAX_INSTANCES
        component.rootIDs[const.ai.DECISION_BRAIN_INDEX] = state.get('DecisionTreeClientRoot', None)
        component.rootIDs[const.ai.DECISION_HATE_INDEX] = None
        component.instances = [None] * const.ai.DECISION_MAX_INSTANCES
        return component

    def PrepareComponent(self, sceneID, entityID, component):
        if component.rootIDs[const.ai.DECISION_BRAIN_INDEX] == None:
            return
        component.instances[const.ai.DECISION_BRAIN_INDEX] = GameWorld.DecisionTreeInstance(entityID, const.ztree.GENERATE_TREE_INSTANCE_ID)
        component.rootIDs[const.ai.DECISION_BRAIN_INDEX] = int(component.rootIDs[const.ai.DECISION_BRAIN_INDEX])