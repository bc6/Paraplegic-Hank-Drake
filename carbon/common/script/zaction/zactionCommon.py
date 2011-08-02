import GameWorld
import log
import service
import collections
import zaction
import inspect
import ztree
import uthread

class zactionCommonBase(service.Service):
    __guid__ = 'zaction.zactionCommonBase'
    __notifyevents__ = ['OnPostCfgDataChanged']

    def __init__(self, treeManager):
        self.treeManager = treeManager
        service.Service.__init__(self)



    def SetupActionTree(self, mySystemID):
        self.rootNode = GameWorld.ActionTreeNode()
        self.rootNode.ID = 0
        self.rootNode.name = 'Root'
        self.rootNode.CreateMyPropertyList()
        self.treeManager.AddTreeNode(self.rootNode)
        for treeNode in cfg.treeNodes:
            if mySystemID == treeNode.systemID:
                node = GameWorld.ActionTreeNode()
                node.ID = treeNode.treeNodeID
                node.name = str(treeNode.treeNodeName)
                node.actionType = treeNode.treeNodeType or 0
                node.CreateMyPropertyList()
                if not self.treeManager.AddTreeNode(node):
                    log.LogError('Failed to add tree node to ActionTree', node.treeNodeName)

        for linkRowSet in cfg.treeLinks.itervalues():
            for link in linkRowSet:
                if mySystemID == link.systemID:
                    if link.linkType is not None:
                        linkType = link.linkType & const.zaction._ACTION_LINK_TYPE_BIT_FILTER
                        exposureType = link.linkType >> const.zaction._ACTION_LINK_BIT_ORDER_SPLIT
                    else:
                        linkType = 0
                        exposureType = 0
                    if not self.treeManager.AddTreeLink(linkType, exposureType, link.parentTreeNodeID, link.childTreeNodeID):
                        log.LogError('Failed to add tree link to ActionTree', link.parentTreeNodeID, link.childTreeNodeID)


        import actionProcTypes
        procList = inspect.getmembers(actionProcTypes)
        for (procName, procDef,) in procList:
            if isinstance(procDef, zaction.ProcTypeDef):
                for entry in procDef.properties:
                    if isinstance(entry, zaction.ProcPropertyTypeDef):
                        GameWorld.AddActionProcNameMappingInfo(procName, entry.name, entry.isPrivate)

                if procDef.pythonProc is not None:
                    GameWorld.RegisterPythonActionProc(procName, procDef.pythonProc[0], procDef.pythonProc[1])

        for prop in cfg.treeNodeProperties:
            treeNode = self.treeManager.GetTreeNodeByID(prop.treeNodeID)
            if treeNode is not None:
                if prop.procID is None or 0 == prop.procID:
                    propertyName = prop.propertyName
                else:

                    def GetMangledName(propName, procInstanceID):
                        nameLen = len(propName)
                        mangleName = '___' + str(procInstanceID)
                        mangleNameLen = len(mangleName)
                        if nameLen + mangleNameLen > const.zaction.MAX_PROP_NAME_LEN:
                            baseLen = const.zaction.MAX_PROP_NAME_LEN - mangleNameLen
                            propName = propName[:baseLen]
                        finalName = propName + mangleName
                        return finalName


                    propertyName = GetMangledName(prop.propertyName, prop.procID)
                if False == treeNode.AddProperty(propertyName, prop.propertyBaseType, prop.propertyValue):
                    log.LogError('Failed to add ' + str(propertyName) + ' to node ' + str(treeNode.name) + ' ID ' + str(prop.treeNodeID))

        for stepList in cfg.actionTreeSteps.itervalues():
            for step in stepList:
                treeNode = self.treeManager.GetTreeNodeByID(step.actionID)
                if treeNode is not None:
                    type = step.stepType or const.zaction.ACTIONSTEP_TYPEID_NORMAL
                    loc = step.stepLocation or const.zaction.ACTIONSTEP_LOCID_CLIENTSERVER
                    treeNode.AddActionStep(str(step.stepName), step.stepID, type, loc)


        for stepList in cfg.actionTreeSteps.itervalues():
            for step in stepList:
                treeNode = self.treeManager.GetTreeNodeByID(step.actionID)
                if treeNode is not None:
                    if step.stepParent is not None:
                        treeNode.ConnectActionStepChildren(step.stepParent, step.stepID)
                    if step.stepSibling is not None:
                        treeNode.ConnectActionStepSiblings(step.stepSibling, step.stepID)


        for procList in cfg.actionTreeProcs.itervalues():
            for proc in procList:
                treeNode = self.treeManager.GetTreeNodeByID(proc.actionID)
                if treeNode is not None:
                    if proc.stepID is not None and proc.stepID != 0:
                        stepNode = treeNode.GetActionStepByID(proc.stepID)
                        if stepNode is None:
                            log.LogError('Failed to find step node referenced by ActionProc: ', proc.actionID, proc.stepID, proc.procType)
                        else:
                            stepNode.AddActionProcRecord(str(proc.procType), proc.procID, proc.isMaster)
                    else:
                        treeNode.AddActionProcRecord(str(proc.procType), proc.procID, proc.isMaster)





    def GetActionTree(self):
        return self.treeManager



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Current Action'] = '?'
        actionTreeNode = component.treeInstance.GetCurrentTreeNode()
        if actionTreeNode and component.treeInstance.debugItem:
            report['Current Action'] = '%s  duration: %f' % (actionTreeNode.name, component.treeInstance.debugItem.duration)
        return report



    def OnPostCfgDataChanged(self, part, updatedRow):
        if part == 'treeNodes':
            if updatedRow.systemID == self.GetTreeSystemID():
                self.ResetTree()
        if part == 'treeLinks':
            if updatedRow.systemID == self.GetTreeSystemID():
                self.ResetTree()
        if part == 'treeNodeProperties':
            for node in cfg.treeNodes:
                if node.treeNodeID == updatedRow.treeNodeID:
                    if node.systemID == self.GetTreeSystemID():
                        self.ResetTree()




    def ResetTree(self):
        self.treeManager.PrepareForReload()
        self.SetupActionTree(self.GetTreeSystemID())
        self.treeManager.EnableTreeInstances(self.defaultAction)




class zactionCommon(zactionCommonBase):
    __guid__ = 'zaction.zactionCommon'

    def __init__(self, treeManager):
        zactionCommonBase.__init__(self, treeManager)
        GameWorld.SetBasePythonActionProcMethod(ZactionCommonBasePythonProcMethod)
        self.actionTickManager = GameWorld.ActionTickManager()
        self.defaultAction = 0



    @classmethod
    def GetTreeSystemID(cls):
        return const.ztree.TREE_SYSTEM_ID_DICT[const.zaction.ACTION_SCHEMA]



    def ProcessAnimationDictionary(self, animationDict):
        GameWorld.processAnimInfoYAML(animationDict)




def ZactionCommonBasePythonProcMethod(method, args):
    with uthread.BlockTrapSection():
        result = method(*args)
    return result



class ProcTypeDef(object):
    __guid__ = 'zaction.ProcTypeDef'

    def __init__(self, procCategory = None, isMaster = True, isConditional = False, properties = [], displayName = None, pythonProc = None, description = None, stepLocationRequirements = [const.zaction.ACTIONSTEP_LOC_SERVERONLY, const.zaction.ACTIONSTEP_LOC_CLIENTSERVER, const.zaction.ACTIONSTEP_LOC_CLIENTONLY]):
        self.isMaster = isMaster
        self.isConditional = isConditional
        self.properties = properties
        self.procCategory = procCategory
        self.displayName = displayName
        self.pythonProc = pythonProc
        self.stepLocationRequirements = stepLocationRequirements
        self.description = description




class ProcPropertyTypeDef(object):
    __guid__ = 'zaction.ProcPropertyTypeDef'

    def __init__(self, name, dataType, userDataType = None, isPrivate = True, displayName = None, default = None, show = True):
        self.name = name
        self.dataType = dataType
        self.userDataType = userDataType
        self.isPrivate = isPrivate
        self.displayName = displayName
        self.default = default
        self.show = show




def _ProcNameHelper(displayName, procRow):
    import actionProperties
    import actionProcTypes
    import re
    import types
    propDict = actionProperties.GetPropertyValueDict(procRow)
    procDef = actionProcTypes.GetProcDef(procRow.procType)
    propDefs = procDef.properties

    def InterpretSub(match):
        name = re.search('\\((.*?)\\)', match.group(0))
        propName = name.group(1)
        if propName not in propDict:
            return '(ERR: ' + propName + ')'
        propRows = ztree.NodeProperty.GetAllPropertiesByTreeNodeID(procRow.actionID)
        for propRow in propRows:
            if propRow.propertyName == propName:
                for propDef in propDefs:
                    if propDef.name == propName:
                        dictVal = propDict[propName]
                        subString = str(dictVal)
                        if propDef.userDataType != None:
                            typeInfo = getattr(actionProperties, propDef.userDataType, None)
                            if typeInfo is not None and types.TupleType == type(typeInfo):
                                if 'listMethod' == typeInfo[0]:
                                    list = typeInfo[1](propRow)
                                elif 'list' == typeInfo[0]:
                                    list = typeInfo[1]
                                else:
                                    list = None
                                for tuple in list:
                                    (name, val, desc,) = tuple[:3]
                                    if val == dictVal:
                                        subString = str(name)
                                        break

                        return subString

                break

        return '(ERR: ' + propName + ')'


    return re.sub('(%\\(.*?\\).)', InterpretSub, displayName)



def ProcNameHelper(displayName):
    return lambda procRow: _ProcNameHelper(displayName, procRow)


exports = {'zaction.ProcNameHelper': ProcNameHelper}

