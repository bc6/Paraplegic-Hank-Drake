import copy
import entityCommon
import service

class EntityRecipeService(service.Service):
    __guid__ = 'svc.entityRecipeSvc'
    __exportedcalls__ = {'GetTypeRecipe': [service.ROLE_ANY],
     'GetGroupRecipe': [service.ROLE_SERVICE],
     'GetCategoryRecipe': [service.ROLE_SERVICE]}
    __notifyevents__ = ['OnBSDTablesChanged2',
     'OnBsdCfgRowChangePending',
     'OnBsdCfgRowDeletePending',
     'OnBsdCfgRowListChangePending']

    def __init__(self):
        service.Service.__init__(self)
        self._cfgDataCallbacks = {}



    def Run(self, *args):
        service.Service.Run(self, *args)
        self.spawnRecipes = {}
        self.typeRecipes = {}
        self.groupRecipes = {}
        self.categoryRecipes = {}
        self._RegisterCfgDataCallback('cefIngredients', lambda ingredientRow: self._ClearIngredientParent(ingredientRow.parentID, ingredientRow.parentType))
        self._RegisterCfgDataCallback('cefIngredientInits', lambda initRow: self._ClearIngredientInit(initRow.ingredientID))



    def GetInventoryGroup(self, groupID):
        return cfg.invgroups.Get(groupID)



    def GetInventoryType(self, typeID):
        return cfg.invtypes.Get(typeID)



    def GetSpawn(self, spawnID):
        return cfg.entitySpawns.Get(spawnID)



    def GetIngredient(self, ingredientID):
        return cfg.ingredients.Get(ingredientID)



    def GetSpawnRecipe(self, spawnID):
        if spawnID not in self.spawnRecipes:
            recipe = self._LoadSpawnRecipe(spawnID)
        else:
            recipe = copy.deepcopy(self.spawnRecipes[spawnID])
        return recipe



    def GetTypeRecipe(self, typeID, overrideDict = None):
        if typeID not in self.typeRecipes:
            recipe = self._LoadTypeRecipe(typeID)
        else:
            recipe = copy.deepcopy(self.typeRecipes[typeID])
        if overrideDict is not None:
            self._IntegrateDicts(recipe, overrideDict)
        return recipe



    def GetGroupRecipe(self, groupID, overrideDict = None):
        if groupID not in self.groupRecipes:
            recipe = self._LoadGroupRecipe(groupID)
        else:
            recipe = copy.deepcopy(self.groupRecipes[groupID])
        if overrideDict is not None:
            self._IntegrateDicts(recipe, overrideDict)
        return recipe



    def GetCategoryRecipe(self, categoryID, overrideDict = None):
        if categoryID not in self.categoryRecipes:
            recipe = self._LoadCategoryRecipe(categoryID)
        else:
            recipe = copy.deepcopy(self.categoryRecipes[categoryID])
        if overrideDict is not None:
            self._IntegrateDicts(recipe, overrideDict)
        return recipe



    def _IntegrateDicts(self, recipe, overrideDict):
        for (componentID, overrides,) in overrideDict.iteritems():
            componentRecipe = recipe.get(componentID)
            if componentRecipe is None:
                recipe[componentID] = overrides
            else:
                for (overrideKey, overrideValue,) in overrides.iteritems():
                    if overrideKey != 'keyedData':
                        componentRecipe[overrideKey] = overrideValue
                    else:
                        componentKeyedDict = componentRecipe.get(overrideKey)
                        if componentKeyedDict is None:
                            componentRecipe['keyedData'] = overrideValue
                        else:
                            for (keyName, valueDict,) in overrideValue.iteritems():
                                keyNameDict = componentKeyedDict.get(keyName)
                                if keyNameDict is None:
                                    componentKeyedDict[keyName] = valueDict
                                else:
                                    keyNameDict.update(valueDict)






    def _LoadInitValues(self, recipeComponent, ingredientID):
        cachedInitVals = cfg.entityIngredientInitialValues
        if ingredientID not in cachedInitVals:
            return 
        initvals = cachedInitVals[ingredientID]
        for row in initvals:
            val = entityCommon.GetIngredientInitialValue(row)
            if row.keyName is None:
                recipeComponent[row.initialValueName] = val
            else:
                if 'keyedData' not in recipeComponent:
                    recipeComponent['keyedData'] = {}
                if row.keyName not in recipeComponent['keyedData']:
                    recipeComponent['keyedData'][row.keyName] = {}
                recipeComponent['keyedData'][row.keyName][row.initialValueName] = val




    def _LoadCategoryRecipe(self, categoryID):
        recipe = {}
        ingredientCache = cfg.entityIngredientsByParentID
        if categoryID not in ingredientCache:
            return recipe
        ingredients = ingredientCache[categoryID]
        for row in ingredients:
            if row.parentType != const.cef.PARENT_CATEGORYID:
                continue
            recipe[row.componentID] = {}
            self._LoadInitValues(recipe[row.componentID], row.ingredientID)

        self.categoryRecipes[categoryID] = copy.deepcopy(recipe)
        return recipe



    def _LoadGroupRecipe(self, groupID):
        groupObj = self.GetInventoryGroup(groupID)
        if groupObj.categoryID not in self.categoryRecipes:
            recipe = self._LoadCategoryRecipe(groupObj.categoryID)
        else:
            recipe = copy.deepcopy(self.categoryRecipes[groupObj.categoryID])
        ingredientCache = cfg.entityIngredientsByParentID
        if groupID not in ingredientCache:
            return recipe
        ingredients = ingredientCache[groupID]
        for row in ingredients:
            if row.parentType != const.cef.PARENT_GROUPID:
                continue
            if row.componentID not in recipe:
                recipe[row.componentID] = {}
            self._LoadInitValues(recipe[row.componentID], row.ingredientID)

        self.groupRecipes[groupID] = copy.deepcopy(recipe)
        return recipe



    def _LoadTypeRecipe(self, typeID):
        recipe = {}
        typeObj = self.GetInventoryType(typeID)
        if typeObj.groupID not in self.groupRecipes:
            recipe = self._LoadGroupRecipe(typeObj.groupID)
        else:
            recipe = copy.deepcopy(self.groupRecipes[typeObj.groupID])
        ingredientCache = cfg.entityIngredientsByParentID
        if typeID in ingredientCache:
            ingredients = ingredientCache[typeID]
            for row in ingredients:
                if row.parentType != const.cef.PARENT_TYPEID:
                    continue
                if row.componentID not in recipe:
                    recipe[row.componentID] = {}
                self._LoadInitValues(recipe[row.componentID], row.ingredientID)

        for (componentID, initValues,) in recipe.iteritems():
            initValues['_typeID'] = typeID

        self.typeRecipes[typeID] = recipe
        return recipe



    def _LoadSpawnRecipe(self, spawnID):
        recipe = {}
        spawnObj = self.GetSpawn(spawnID)
        if spawnObj.typeID not in self.typeRecipes:
            recipe = self._LoadTypeRecipe(spawnObj.typeID)
        else:
            recipe = copy.deepcopy(self.typeRecipes[spawnObj.typeID])
        overridesCache = cfg.entitySpawnInitsBySpawn
        if spawnID in overridesCache:
            overrides = overridesCache[spawnID]
            for row in overrides:
                if row.componentID not in recipe:
                    recipe[row.componentID] = {}
                recipe[row.componentID][row.initialValueName] = entityCommon.GetIngredientInitialValue(row)

        self.spawnRecipes[spawnID] = recipe
        return recipe



    def OnBSDTablesChanged2(self, allTablesChanged):
        import inventory
        categoryTableName = inventory.Category.GetCategoryClass().__primaryTable__.tableName
        groupTableName = inventory.Group.GetGroupClass().__primaryTable__.tableName
        typeTableName = inventory.Type.GetTypeClass().__primaryTable__.tableName
        ingredientTableName = const.cef.INGREDIENTS_TABLE_FULL_NAME
        ingredientInitTableName = const.cef.INGREDIENT_INITS_TABLE_FULL_NAME
        tableCallbacksList = [(categoryTableName, self._HandleCategoryTableChange),
         (groupTableName, self._HandleGroupTableChange),
         (typeTableName, self._HandleTypeTableChange),
         (ingredientTableName, self._HandleIngredientTableChange),
         (ingredientInitTableName, self._HandleIngredientInitTableChange)]
        for (tableName, callback,) in tableCallbacksList:
            if tableName in allTablesChanged:
                callback(allTablesChanged[tableName])




    def _HandleCategoryTableChange(self, tableChanges):
        for ((categoryID, trash, trash,), (revisionID, oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            self._ClearCategoryRecipe(categoryID)




    def _HandleGroupTableChange(self, tableChanges):
        for ((groupID, trash, trash,), (revisionID, oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            self._ClearGroupRecipe(groupID)




    def _HandleTypeTableChange(self, tableChanges):
        for ((typeID, trash, trash,), (revisionID, oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            self._ClearTypeRecipe(typeID)




    def _HandleIngredientTableChange(self, tableChanges):
        for ((ingredientID, trash, trash,), (revisionID, oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            validKeyVal = oldDataKeyVal or newDataKeyVal
            self._ClearIngredientParent(validKeyVal.parentID, validKeyVal.parentType)




    def _HandleIngredientInitTableChange(self, tableChanges):
        for ((ingredientInitialValueID, trash, trash,), (revisionID, oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            validKeyVal = oldDataKeyVal or newDataKeyVal
            self._ClearIngredientInit(validKeyVal.ingredientID)




    def OnBsdCfgRowChangePending(self, uniqueRefName, cfgEntryName, updatedRow):
        self._HandleBsdCfgChange(uniqueRefName, updatedRow)



    def OnBsdCfgRowDeletePending(self, uniqueRefName, cfgEntryName, deletedRow):
        self._HandleBsdCfgChange(uniqueRefName, deletedRow)



    def OnBsdCfgRowListChangePending(self, uniqueRefName, cfgEntryName, updatedRow, newCRowset):
        self._HandleBsdCfgChange(uniqueRefName, updatedRow)



    def _HandleBsdCfgChange(self, uniqueRefName, updatedRow):
        if uniqueRefName not in self._cfgDataCallbacks:
            return 
        self._cfgDataCallbacks[uniqueRefName](updatedRow)



    def _RegisterCfgDataCallback(self, uniqueRefName, callbackFunc):
        self._cfgDataCallbacks[uniqueRefName] = callbackFunc



    def _ClearIngredientInit(self, ingredientID):
        ingredientRow = self.GetIngredient(ingredientID)
        if ingredientRow is not None:
            self._ClearIngredientParent(ingredientRow.parentID, ingredientRow.parentType)



    def _ClearIngredientParent(self, parentID, parentType):
        if parentType == const.cef.PARENT_CATEGORYID:
            self._ClearCategoryRecipe(parentID)
        elif parentType == const.cef.PARENT_GROUPID:
            self._ClearGroupRecipe(parentID)
        elif parentType == const.cef.PARENT_TYPEID:
            self._ClearTypeRecipe(parentID)
        elif parentType == const.cef.PARENT_SPAWNID:
            self._ClearSpawnRecipe(parentID)



    def _ClearSpawnRecipe(self, spawnID):
        if spawnID in self.spawnRecipes:
            del self.spawnRecipes[spawnID]



    def _ClearTypeRecipe(self, typeID):
        if typeID in self.typeRecipes:
            del self.typeRecipes[typeID]
        try:
            import cef
            allSpawns = cef.Spawn.GetAllByType(typeID)
            for spawnObj in allSpawns:
                self._ClearTypeRecipe(spawnObj.spawnID)

        except:
            import sys
            sys.exc_clear()
            self.spawnRecipes = {}



    def _ClearGroupRecipe(self, groupID):
        if groupID in self.groupRecipes:
            del self.groupRecipes[groupID]
        try:
            import inventory
            allTypes = inventory.Type.GetAllByGroup(groupID)
            for typeObj in allTypes:
                self._ClearTypeRecipe(typeObj.typeID)

        except:
            import sys
            sys.exc_clear()
            self.typeRecipes = {}
            self.spawnRecipes = {}



    def _ClearCategoryRecipe(self, categoryID):
        if categoryID in self.categoryRecipes:
            del self.categoryRecipes[categoryID]
        try:
            import inventory
            allGroups = inventory.Group.GetAllByCategory(categoryID)
            for groupObj in allGroups:
                self._ClearGroupRecipe(groupObj.groupID)

        except:
            import sys
            sys.exc_clear()
            self.groupRecipes = {}
            self.typeRecipes = {}
            self.spawnRecipes = {}




