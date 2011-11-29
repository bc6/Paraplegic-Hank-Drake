import zaction
import GameWorld

def ForceDecisionTreeToRoot(entID):
    decisionService = sm.GetService('decisionTreeClient')
    treeManager = decisionService.treeManager
    if treeManager:
        entity = sm.GetService('entityClient').FindEntityByID(entID)
        if entity:
            component = entity.GetComponent('decision')
            treeInstance = component.instances[const.ai.DECISION_BRAIN_INDEX]
            if treeInstance:
                treeNode = treeManager.GetTreeNodeByID(component.rootIDs[const.ai.DECISION_BRAIN_INDEX])
                treeInstance.ForceAction(treeNode)
                return True
    return False



def ActionPopupMenu(entID):
    entity = sm.GetService('entityClient').FindEntityByID(entID)
    if entity:
        perceptionComponent = entity.GetComponent('perception')
        if perceptionComponent:
            clientManager = sm.GetService('perceptionClient').GetPerceptionManager(session.worldspaceid)
            if clientManager:
                if clientManager.DropOneStimulusSimple('Interact', entID, session.charid, -1.0):
                    ForceDecisionTreeToRoot(session.charid)


exports = {'actionProcTypes.ForceDecisionTreeToRoot': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[], description='Forces the AI decision tree evaluate from the root node. Will interrupt any waitfor procs'),
 'decisionProcs.ForceDecisionTreeToRoot': ForceDecisionTreeToRoot,
 'decisionProcs.ActionPopupMenu': ActionPopupMenu,
 'actionProcTypes.AttemptAction': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('NewAction', 'I', userDataType='ActionList', isPrivate=True)], description="Attempt to change the entity's ZAction to the selected action"),
 'actionProcTypes.AttemptActionOnTarget': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('NewAction', 'I', userDataType='ActionList', isPrivate=True, displayName='Attempt Action'), zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='On Target')], description="Attempt to change the entity's ZAction to the selected action using the current target"),
 'actionProcTypes.IsActionAvailable': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('NewAction', 'I', userDataType='ActionList', isPrivate=True)], description='Check if the Action is available'),
 'actionProcTypes.IsActionAvailableOnTarget': zaction.ProcTypeDef(isMaster=False, isConditional=True, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('NewAction', 'I', userDataType='ActionList', isPrivate=True, displayName='Attempt Action'), zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='On Target')], description='Check if the action is available on the target'),
 'actionProcTypes.PathSetTarget': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('Target', 'I', userDataType='AITarget', isPrivate=True, displayName='Path to Target')], description="Path to a target entity's location. Will not follow the target")}

