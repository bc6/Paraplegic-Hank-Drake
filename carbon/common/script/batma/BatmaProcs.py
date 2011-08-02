import actionProcTypes
import actionProperties
import batma
import re
import types
import zaction
import ztree
ModifierDataTypes = {0: [('Value', 'F', None)],
 1: [('Attribute', 'I', 'AttributeList'), ('AttrSource', 'I', 'TargetTypeList')],
 2: [('Property', 'S', None)]}

def BuildBatmaPropertyList(propertyDefs):
    todo = []
    for propDef in propertyDefs:
        if propDef.userDataType == 'Modifier':
            propDef.dataType = 'I'
            todo.append(propDef)

    for propDef in todo:
        for modTypes in ModifierDataTypes.itervalues():
            for modType in modTypes:
                propertyDefs.append(zaction.ProcPropertyTypeDef(propDef.name + ' ' + modType[0], modType[1], userDataType=modType[2], show=False, isPrivate=propDef.isPrivate))



    return propertyDefs



def ModifierWrapperMethod(aobj, label, filterList, propRow, editFlags):
    import attrFilter
    import app.Config as Config
    import app.Select as Select

    def PanelRefresh():
        panel = Jessica['AttributesPanel']
        panel.Freeze()
        Select.SetSelection(Select.GetSelection(), panel.GetId())
        panel.Thaw()


    aobj.StartGroup(label + str(propRow.procID))
    index = len(filterList)
    filterList.append(attrFilter.DataTypeConversionFilter(propRow, 'propertyBaseType', 'propertyValue'))
    aobj.AddMember('filterList[%d].viewedValue' % index, label=label + ' Type', editflags=editFlags, database=True, types=Config.COMBOBOX, enumerations=[ (modTypes[0][0], id, '') for (id, modTypes,) in ModifierDataTypes.iteritems() ], func=PanelRefresh)
    if propRow.propertyValue == None:
        propRow.propertyValue = 0
    modTypes = ModifierDataTypes[int(propRow.propertyValue)]
    for modType in modTypes:
        propName = propRow.propertyName + ' ' + modType[0]
        properties = ztree.NodeProperty.GetAllPropertiesByTreeNodeID(propRow.treeNodeID)
        for prop in properties:
            if propName == prop.propertyName and prop.procID == propRow.procID:
                actionProperties.AddWrapperComponents(aobj, filterList, prop, editFlags, displayName=propName)
                break


    aobj.EndGroup()



def _BatmaProcNameHelper(displayName, procRow):
    propDict = actionProperties.GetPropertyValueDict(procRow)
    procDef = actionProcTypes.GetProcDef(procRow.procType)
    propDefs = procDef.properties

    def ModifierSub(match):
        name = re.search('\\((.*?)\\)', match.group(0))
        propName = name.group(1)
        if propName not in propDict:
            return '(ERR: ' + propName + ')'
        typeIdx = propDict[propName]
        if typeIdx is None:
            typeIdx = 0
        modDataType = ModifierDataTypes[int(typeIdx)]
        modData = modDataType[0]
        propName += ' ' + modData[0]
        return '%(' + propName + ')s'


    demodifiedString = re.sub('(%\\([^\\)]*?\\)m)', ModifierSub, displayName)

    def InterpretSub(match):
        name = re.search('\\((.*?)\\)', match.group(0))
        propName = name.group(1)
        if propName not in propDict:
            return '(ERR: ' + propName + ')'
        for propDef in propDefs:
            if propDef.name == propName:
                dictVal = propDict[propName]
                subString = str(dictVal)
                if propDef.userDataType != None:
                    typeInfo = getattr(actionProperties, propDef.userDataType, None)
                    if typeInfo is not None and types.TupleType == type(typeInfo):
                        if 'listMethod' == typeInfo[0]:
                            list = typeInfo[1](None)
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

        return '(ERR: ' + propName + ')'


    return re.sub('(%\\(.*?\\).)', InterpretSub, demodifiedString)



def BatmaProcNameHelper(displayName):
    return lambda procRow: _BatmaProcNameHelper(displayName, procRow)



def GetBuffList(propRow):
    buffList = batma.Buff.GetActionNameIDMappingList()
    retList = [ (buff[0], buff[1], '') for buff in buffList ]
    retList.insert(0, (' None', None, ''))
    return retList



def GetCatmaClassList(className):

    def _getClassList(className):
        catmaSvc = sm.GetService('catma')
        ax2 = catmaSvc.GetAX2()
        catmaTypes = ax2.GetNodeByClassName(className, True)
        enumList = [(' None', 'None', '')]
        enumList.extend([ (catmaNode.GetNodeName(), catmaNode.GetFolderID(), '') for catmaNode in catmaTypes ])
        return enumList


    return lambda x: _getClassList(className)



def GetBuffIDByName(name):
    buffDict = {name:id for (name, id,) in batma.Buff.GetActionNameIDMappingList()}
    return buffDict.get(name, 0)


OperationList = [('Add', 0, 'Adds a value to an attribute'),
 ('Subtract', 1, 'Subtracts a value from an attribute'),
 ('Multiply', 2, 'Multiplies a value with an attribute'),
 ('Divide', 3, 'Divides an attribute by a value'),
 ('Add Change Per Second', 4, 'Changes an attribute by a value every second'),
 ('Sub Change Per Second', 5, 'Changes an attribute by a negative value every second')]
GroupOperationList = [('Add', 0, 'Adds a value to an attribute'),
 ('Subtract', 1, 'Subtracts a value from an attribute'),
 ('Add Change Per Second', 4, 'Changes an attribute by a value every second'),
 ('Sub Change Per Second', 5, 'Changes an attribute by a negative value every second')]
DamageTypeList = [('Default Damage Type', 0, '')]
ChallengeTypeList = [('Default Challenge Type', 0, '')]
TargetTypeList = [('Me', 0, ''), ('My Target', 1, ''), ('Buff Source', 2, '')]
ComparisonTypeList = [('GreaterThan', 0, ''),
 ('LessThan', 1, ''),
 ('GreaterThanOrEqual', 2, ''),
 ('LessThanOrEqual', 3, '')]
exports = {'batma.BatmaProcNameHelper': BatmaProcNameHelper,
 'batma.BuildBatmaPropertyList': BuildBatmaPropertyList,
 'actionProperties.Modifier': ('method', ModifierWrapperMethod),
 'actionProperties.BuffList': ('listMethod', GetBuffList),
 'actionProperties.EffectList': ('listMethod', GetCatmaClassList('BatmaEffect')),
 'actionProperties.AttributeList': ('listMethod', GetCatmaClassList('BatmaAttribute')),
 'actionProperties.AttributeGroupList': ('listMethod', GetCatmaClassList('BatmaAttributeGroup')),
 'actionProperties.EntityStateList': ('listMethod', GetCatmaClassList('BatmaEntityState')),
 'actionProperties.OperationList': ('list', OperationList),
 'actionProperties.GroupOperationList': ('list', GroupOperationList),
 'actionProperties.DamageTypeList': ('list', DamageTypeList),
 'actionProperties.ChallengeTypeList': ('list', ChallengeTypeList),
 'actionProperties.TargetTypeList': ('list', TargetTypeList),
 'actionProperties.ComparisonTypeList': ('list', ComparisonTypeList),
 'actionProcTypes.DoBuff': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('DoBuff %(BuffID)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('BuffID', 'I', userDataType='BuffList', isPrivate=True), zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True)]), description='Attempts to apply the buff specified by BuffID to the desired TargetType.'),
 'actionProcTypes.ApplyEffect': zaction.ProcTypeDef(isMaster=False, procCategory='Batma', displayName=BatmaProcNameHelper('ApplyEffect %(EffectType)i(%(EffectValue)m)'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('EffectType', 'I', userDataType='EffectList', isPrivate=True), zaction.ProcPropertyTypeDef('EffectValue', 'M', userDataType='Modifier', isPrivate=True)]), description='For the lifetime of the proc, apply the specified effect of EffectType with the desired ModifierValue to the owner of the action.'),
 'actionProcTypes.WaitForBatmaTime': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('Wait %(BatmaDuration)m sec'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('BatmaDuration', 'M', userDataType='Modifier', isPrivate=True)]), description='Waits for an amount of time specified by the ModifierValue BatmaDuration.'),
 'actionProcTypes.WaitForBatmaEvent': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper("Wait for '%(EventName)s'"), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('EventName', 'S', isPrivate=True)]), description='Only useful in Try Steps.\nWill wait until the BatmaEvent EventName is triggered to break out of a try block.\n\nPairs with SendBatmaEvent.'),
 'actionProcTypes.SendBatmaEvent': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper("SendBatmaEvent '%(EventName)s'"), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('EventName', 'S', isPrivate=True), zaction.ProcPropertyTypeDef('EventTargetType', 'I', userDataType='TargetTypeList', isPrivate=True)]), description='Signals the BatmaEvent EventName on the EventTargetType.\n\nPairs with WaitForBatmaEvent.'),
 'actionProcTypes.AttributeCheck': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Batma', displayName=BatmaProcNameHelper('%(AttributeID)s %(AttributeComparisonType)s %(AttributeValue)m on %(AttrSource)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('AttributeID', 'I', userDataType='AttributeList', isPrivate=True),
                                    zaction.ProcPropertyTypeDef('AttrSource', 'I', userDataType='TargetTypeList', isPrivate=True),
                                    zaction.ProcPropertyTypeDef('AttributeComparisonType', 'I', userDataType='ComparisonTypeList', isPrivate=True),
                                    zaction.ProcPropertyTypeDef('AttributeValue', 'M', userDataType='Modifier', isPrivate=True)]), description='Used in conditional or try steps and either tests whether or not the specified AttributeID from AttrSource satisfies the AttributeComparisonType when compared against another ModifierValue.\n\nWhen used on a try step, attribute watches will test whether or not the attribute changes to no longer satisfy the comparison.'),
 'actionProcTypes.ModifyAttribute': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('%(Operation)s %(ModifierValue)m to %(AttributeID)s on %(AttrSource)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('AttributeID', 'I', userDataType='AttributeList', isPrivate=True),
                                     zaction.ProcPropertyTypeDef('AttrSource', 'I', userDataType='TargetTypeList', isPrivate=True),
                                     zaction.ProcPropertyTypeDef('Operation', 'I', userDataType='OperationList', isPrivate=True),
                                     zaction.ProcPropertyTypeDef('ModifierValue', 'M', userDataType='Modifier', isPrivate=True)]), description='Applies a ModifierValue with the desired operation to the specified AttributeID on the Attribute source.\n\nFor change over time modifier types, the change is applied for the lifetime of the proc. In order to keep the proc alive, pair it with a wait, or any other master proc with duration.'),
 'actionProcTypes.ModifyAttributeGroup': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('%(Operation)s %(ModifierValue)m to %(AttributeGroupID)s on %(AttrSource)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('AttributeGroupID', 'I', userDataType='AttributeGroupList', isPrivate=True),
                                          zaction.ProcPropertyTypeDef('AttrSource', 'I', userDataType='TargetTypeList', isPrivate=True),
                                          zaction.ProcPropertyTypeDef('Operation', 'I', userDataType='GroupOperationList', isPrivate=True),
                                          zaction.ProcPropertyTypeDef('ModifierValue', 'M', userDataType='Modifier', isPrivate=True),
                                          zaction.ProcPropertyTypeDef('Reverse', 'B', isPrivate=True)]), description='Applies a ModifierValue with the desired operation to the specified Attribute group on the Attribute source. Modifiers will overflow from one attribute in the group to the next if the effect hits a min or max value. Use the reverse option to apply the modifiers to attributes in the group in reverse order.\n\nFor change over time modifier types, the change is applied for the lifetime of the proc.In order to keep the proc alive, pair it with a wait, or any other master proc with duration.'),
 'actionProcTypes.DealDamage': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('Deal %(DamageValue)m to %(TargetType)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('BuffID', 'I', userDataType='BuffList', default=lambda : GetBuffIDByName('DealDamage'), isPrivate=True),
                                zaction.ProcPropertyTypeDef('DamageValue', 'M', userDataType='Modifier', isPrivate=True),
                                zaction.ProcPropertyTypeDef('DamageType', 'I', userDataType='DamageTypeList', isPrivate=True),
                                zaction.ProcPropertyTypeDef('ChallengeType', 'I', userDataType='ChallengeTypeList', isPrivate=True),
                                zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True)]), description='Places the DealDamage buff on the desired TargetType, with special properties added to the DealDamage buff for DamageValue and Type.'),
 'actionProcTypes.IsTargetInBatmaRange': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Batma', displayName=BatmaProcNameHelper('Target in (%(MinRange)m to %(MaxRange)m) meters'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('MinRange', 'M', userDataType='Modifier', isPrivate=True), zaction.ProcPropertyTypeDef('MaxRange', 'M', userDataType='Modifier', isPrivate=True)]), description='Tests whether the currently selected target is between the min and max distances specified.'),
 'actionProcTypes.CheckEntityState': zaction.ProcTypeDef(isMaster=True, isConditional=True, procCategory='Batma', displayName=BatmaProcNameHelper('Is %(TargetType)s %(EntityState)s?'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True), zaction.ProcPropertyTypeDef('EntityState', 'I', userDataType='EntityStateList', isPrivate=True)]), description='Compares the TargetTypes current entity state found in the entities shared property list with the specified EntityState.\n\nPairs with SetEntityState.'),
 'actionProcTypes.SetEntityState': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', stepLocationRequirements=[const.zaction.ACTIONSTEP_LOC_CLIENTSERVER], displayName=BatmaProcNameHelper('Set %(TargetType)s %(EntityState)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True), zaction.ProcPropertyTypeDef('EntityState', 'I', userDataType='EntityStateList', isPrivate=True)]), description="Sets the TargetType's state in the entities shared property list to the specified EntityState.\n\nPairs with CheckEntityState."),
 'actionProcTypes.ExpressionProc': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', stepLocationRequirements=[const.zaction.ACTIONSTEP_LOC_CLIENTSERVER], displayName=BatmaProcNameHelper('%(OutputPropertyName)s = %(ExpressionString)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True), zaction.ProcPropertyTypeDef('ExpressionString', 'S', isPrivate=True), zaction.ProcPropertyTypeDef('OutputPropertyName', 'S', isPrivate=True)]), description="This proc evaluates a python string of python code and is super fucking dangerous. Pretty sure we can't ship with it... but... It will evaluate the ExpressionString and place the output in a property specified by OutputPropertyName.\n\nThe syntax for the expression string allows you to access attributes on yourself or the desired TargetType by using {self.attr_name} or {target.attr_name}"),
 'actionProcTypes.ChatBubble': zaction.ProcTypeDef(isMaster=True, procCategory='Batma', displayName=BatmaProcNameHelper('%(TargetType)s says %(ChatString)s'), properties=BuildBatmaPropertyList([zaction.ProcPropertyTypeDef('TargetType', 'I', userDataType='TargetTypeList', isPrivate=True), zaction.ProcPropertyTypeDef('ChatString', 'S', isPrivate=True)]), description="The name is a little misleading, it won't actually make a chat bubble.\nIt will, however, make the TargetType character speak in local chat.")}

