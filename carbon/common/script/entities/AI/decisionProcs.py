import zaction
import GameWorld

def ForceDecisionTreeToRoot(entID):
    decisionService = sm.GetService('decisionTreeClient')
    treeManager = decisionService.treeManager
    if treeManager:
        treeInstanceList = treeManager.GetTreeInstanceList(entID)
        if treeInstanceList:
            entity = sm.GetService('entityClient').FindEntityByID(entID)
            if entity:
                component = entity.GetComponent('decision')
                treeNode = treeManager.GetTreeNodeByID(component.rootID)
                treeInstance = treeInstanceList[0]
                if treeInstance:
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


exports = {'actionProcTypes.DecisionTest': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[zaction.ProcPropertyTypeDef('teststring', 'S', userDataType='AI test', isPrivate=True, displayName='test string')]),
 'actionProcTypes.ForceDecisionTreeToRoot': zaction.ProcTypeDef(isMaster=False, procCategory='AI', properties=[]),
 'decisionProcs.ForceDecisionTreeToRoot': ForceDecisionTreeToRoot,
 'decisionProcs.ActionPopupMenu': ActionPopupMenu}

