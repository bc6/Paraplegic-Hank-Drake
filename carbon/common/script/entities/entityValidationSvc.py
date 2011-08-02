import cef
import service

class ValidationMessage(object):
    __guid__ = 'cef.ValidationMessage'
    VALID_RECIPE_DESCRIPTION = 'Recipe is valid.'

    def __init__(self, name = None, subPrefix = '  '):
        self.messages = []
        self.isValid = True
        self.name = name
        self.subPrefix = subPrefix



    def AddMessage(self, message):
        if isinstance(message, str):
            self.isValid = False
        elif not message.IsValid():
            self.isValid = False
        self.messages.append(message)



    def IsValid(self):
        return self.isValid



    def GetReport(self):
        if self.IsValid():
            return self.VALID_RECIPE_DESCRIPTION
        reportText = ''
        for message in self.messages:
            if isinstance(message, str):
                reportText += message
                reportText += '\n'
            elif not message.IsValid():
                reportText += message.GetReport()
                reportText += '\n'

        reportText = reportText.strip()
        if self.name is not None:
            reportText = self._AddSubPrefix(reportText)
            reportText = self.name + '\n' + reportText
        return reportText



    def _AddSubPrefix(self, textBlock):
        finishedText = textBlock.replace('\n', '\n' + self.subPrefix)
        finishedText = self.subPrefix + finishedText
        return finishedText




class EntityValidationSvc(service.Service):
    __guid__ = 'svc.entityValidationSvc'
    __dependencies__ = ['entityRecipeSvc']

    def Validate(self, parentID, parentType):
        recipeDict = self._GetRecipeDict(parentID, parentType)
        return self._ValidateRecipeDictionary(parentID, parentType, recipeDict)



    def ValidateCategory(self, categoryID):
        return self.Validate(categoryID, const.cef.PARENT_CATEGORYID)



    def ValidateGroup(self, groupID):
        return self.Validate(groupID, const.cef.PARENT_GROUPID)



    def ValidateType(self, typeID):
        return self.Validate(typeID, const.cef.PARENT_TYPEID)



    def ValidateSpawn(self, spawnID):
        return self.Validate(spawnID, const.cef.PARENT_SPAWNID)



    def _GetRecipeDict(self, parentID, parentType):
        if parentType == const.cef.PARENT_CATEGORYID:
            return self.entityRecipeSvc.GetCategoryRecipe(parentID)
        if parentType == const.cef.PARENT_GROUPID:
            return self.entityRecipeSvc.GetGroupRecipe(parentID)
        if parentType == const.cef.PARENT_TYPEID:
            return self.entityRecipeSvc.GetTypeRecipe(parentID)
        if parentType == const.cef.PARENT_SPAWNID:
            return self.entityRecipeSvc.GetSpawnRecipe(parentID)
        raise TypeError('Parent type is unknown:', parentType)



    def _ValidateRecipeDictionary(self, parentID, parentType, recipeDict):
        result = cef.ValidationMessage()
        self._ValidateEachComponent(result, parentID, parentType, recipeDict)
        return result



    def _ValidateEachComponent(self, result, parentID, parentType, recipeDict):
        for componentID in recipeDict:
            componentView = cef.BaseComponentView.GetComponentViewByID(componentID)
            if componentView is None:
                result.AddMessage('Component is not valid: %s' % componentID)
                continue
            componentResult = cef.ValidationMessage(name=componentView.__COMPONENT_DISPLAY_NAME__)
            self._ValidateSpawnInputs(componentResult, parentID, parentType, recipeDict, componentView)
            componentView.ValidateComponent(componentResult, parentID, parentType, recipeDict)
            result.AddMessage(componentResult)




    def _ValidateSpawnInputs(self, result, parentID, parentType, recipeDict, componentView):
        spawnInputs = set()
        missingInputs = set()
        componentRecipe = recipeDict[componentView.__COMPONENT_ID__]
        spawnInitValueNameTuples = componentView.GetInputs(groupFilter=componentView.ALL_SPAWN)
        for initValueNameTuple in spawnInitValueNameTuples:
            for initialValueName in initValueNameTuple:
                if initialValueName in componentRecipe:
                    spawnInputs.add(initValueNameTuple)
                else:
                    missingInputs.add(initValueNameTuple)


        if parentType == const.cef.PARENT_SPAWNID and len(missingInputs) == 0:
            return 
        if parentType != const.cef.PARENT_SPAWNID and len(spawnInputs) == 0:
            return 
        if parentType == const.cef.PARENT_SPAWNID:
            for initValueNameTuple in missingInputs:
                result.AddMessage('Missing input: %s' % initValueNameTuple)

        if parentType != const.cef.PARENT_SPAWNID:
            for initValueNameTuple in spawnInputs:
                result.AddMessage('Spawn input on non-spawn: %s' % initValueNameTuple)





