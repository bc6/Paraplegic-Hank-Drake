import service
import GameWorld
import re
from catma import catmaDB

class attributeSvc(service.Service):
    __guid__ = 'svc.attributeSvc'
    __notifyevents__ = ['OnSessionChanged']

    def GetDB(self):
        raise NotImplementedError("attributeSvc doesn't implement GetDB()")



    def RegisterClientCallback(self):
        raise NotImplementedError("attributeSvc doesn't implement RegisterClientCallback()")



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.attributeTable = GameWorld.AttributeTable()
        self.attributeCache = GameWorld.AttributeCache()
        self.attributeGroupTable = GameWorld.AttributeGroupTable()
        self.savedAttributes = set()
        self.loadedAttributes = set()
        self._attributeNameDict = {}
        self._attributeDescriptionDict = {}
        self.catmaDataInitialized = False
        GameWorld.RegisterPythonActionProc('ExpressionProc', self.ExpressionProc, ('ENTID', 'ExpressionString', 'OutputPropertyName'))
        self.RegisterClientCallback()



    def _InitializeCatmaDataIfNeeded(self):
        if not self.catmaDataInitialized:
            self.catmaDataInitialized = True
            self.SetCatmaData(self.GetDB())



    def OnSessionChanged(self, isRemote, sess, change):
        if 'userid' in change and change['userid'][0] is None:
            self._InitializeCatmaDataIfNeeded()



    def SetCatmaData(self, cDB):
        attributeTypes = cDB.GetTypeNamesOfClass('BatmaAttribute')
        self._attributeNameDict = {}
        for attributeTypeName in attributeTypes:
            attributeType = cDB.GetType(attributeTypeName)
            attributeID = attributeType.GetTypeID()
            self._attributeNameDict[attributeTypeName] = attributeID


        def ParseVariableNames(varString):
            if not varString:
                return 

            def GetAttributeSubstr(name):
                str = name.group(0).strip('{}')
                if str in self._attributeNameDict:
                    return 'getAttribute(%d, entID_hi, entID_lo)' % self._attributeNameDict[str]
                else:
                    self.LogError('AttributeSvc: invalid attribute %s referenced in value by %s ' % (str, attributeTypeName))
                    return '0'


            regEx = '({.*?})'
            return re.sub(regEx, GetAttributeSubstr, varString, flags=re.IGNORECASE)


        for (attributeTypeName, attributeID,) in self._attributeNameDict.iteritems():
            try:
                attributeType = cDB.GetType(attributeTypeName)
                settings = attributeType.GetValue('settings', 0)
                defaultValue = ParseVariableNames(attributeType.GetValue('defaultValue'))
                minValue = ParseVariableNames(attributeType.GetValue('minValue', None))
                maxValue = ParseVariableNames(attributeType.GetValue('maxValue', None))
                iconPath = attributeType.GetValue('uiIcon', 'NULL')
                name = attributeType.GetValue('uiName.textString', 'NULL')
                description = attributeType.GetValue('uiDescription.textString', 'NULL')
                directlyModifiable = attributeType.GetValue('modifiable', False)
            except catmaDB.CatmaDBError as e:
                self.LogError('AttributeSvc: CatmaDB error: %s from %s' % (e, attributeTypeName))
                continue
            self.attributeTable.AddAttributeFromPython(attributeID, settings, defaultValue, minValue, maxValue)
            self._attributeDescriptionDict[attributeID] = (iconPath, name, description)
            if self.attributeTable.IsAttributeSavedToDatabase(attributeID):
                self.savedAttributes.add(attributeID)
            if self.attributeTable.IsAttributeLoadedFromDatabase(attributeID):
                self.loadedAttributes.add(attributeID)

        self.attributeTable.EvaluateAttributeDependencies()
        self.LoadAttributeGroupsFromCatma(cDB)



    def LoadAttributeGroupsFromCatma(self, cDB):
        attributeGroupTypes = cDB.GetTypeNamesOfClass('BatmaAttributeGroup')
        for attributeGroupTypeName in attributeGroupTypes:
            attributeGroupType = cDB.GetType(attributeGroupTypeName)
            attributeGroupID = attributeGroupType.GetTypeID()
            attributeIDList = attributeGroupType.GetValue('attributeIDs', '')
            self.attributeGroupTable.AddAttributeGroupFromPython(attributeGroupID, attributeIDList)




    def GetAttributeNameToIDDict(self):
        self._InitializeCatmaDataIfNeeded()
        return self._attributeNameDict



    def GetAttributeIDToDescriptionDict(self):
        self._InitializeCatmaDataIfNeeded()
        return self._attributeDescriptionDict



    def GetAttributeIDFromName(self, attributeName):
        attributeID = self.GetAttributeNameToIDDict().get(attributeName, None)
        return attributeID



    def GetAttributeFromEntity(self, attributeName, entid):
        attributeID = self.GetAttributeIDFromName(attributeName)
        if attributeID is None:
            return 
        attributeValue = self.attributeCache.GetAttributeValueFromEntity(attributeID, entid)
        changePerSecond = self.attributeCache.GetAttributeChangeFromEntity(attributeID, entid)
        attributeMinValue = self.attributeCache.GetAttributeMinFromEntity(attributeID, entid)
        attributeMaxValue = self.attributeCache.GetAttributeMaxFromEntity(attributeID, entid)
        return [attributeValue,
         changePerSecond,
         attributeMinValue,
         attributeMaxValue]



    def GetAttributeValueFromEntity(self, attributeName, entid):
        attributeID = self.GetAttributeIDFromName(attributeName)
        if attributeID is None:
            return 
        return self.GetAttributeValueFromEntityByID(attributeID, entid)



    def GetAttributeValueFromEntityByID(self, attributeID, entid):
        attributeValue = self.attributeCache.GetAttributeValueFromEntity(attributeID, entid)
        change = self.attributeCache.GetAttributeChangeFromEntity(attributeID, entid)
        return attributeValue



    def GetAttributeMinFromEntity(self, attributeName, entid):
        attributeID = self.GetAttributeIDFromName(attributeName)
        if attributeID is None:
            return 
        return self.GetAttributeMinFromEntityByID(attributeID, entid)



    def GetAttributeMinFromEntityByID(self, attributeID, entid):
        attributeValue = self.attributeCache.GetAttributeMinFromEntity(attributeID, entid)
        return attributeValue



    def GetAttributeMaxFromEntity(self, attributeName, entid):
        attributeID = self.GetAttributeIDFromName(attributeName)
        if attributeID is None:
            return 
        return self.GetAttributeMaxFromEntityByID(attributeID, entid)



    def GetAttributeMaxFromEntityByID(self, attributeID, entid):
        attributeValue = self.attributeCache.GetAttributeMaxFromEntity(attributeID, entid)
        return attributeValue



    def DeleteAttributes(self, charID):
        self.attributeCache.RemoveAttributeList(charID)



    def ExpressionProc(self, entID, expressionString, outputPropertyName):
        (success, targetID,) = GameWorld.GetTargetIDForCurrentPythonProc('TargetType')
        if not success:
            return False

        def AttributeSubstr(name):
            nameGroup = name.group(0).strip('{}')
            parts = re.split('\\.', nameGroup)
            testEntityID = entID
            if parts[0] == 'target':
                testEntityID = targetID
                attrName = parts[1]
            elif parts[0] == 'self':
                attrName = parts[1]
            else:
                attrName = parts[0]
            if attrName in self.GetAttributeNameToIDDict():
                return str(self.GetAttributeValueFromEntity(attrName, testEntityID))
            self.LogError('AttributeSvc: invlaid attribute %s referenced in value by ExpressionProc' % nameGroup)
            return '0'


        regEx = '({.*?})'
        subbedExpression = re.sub(regEx, AttributeSubstr, expressionString, flags=re.IGNORECASE)
        expressionValue = eval(subbedExpression)
        GameWorld.AddPropertyForCurrentPythonProc({outputPropertyName: expressionValue})
        return True




