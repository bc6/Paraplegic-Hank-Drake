import cef
import copy
import entityCommon
import inspect
import service
import weakref

class EntityRecipeService(service.Service):
    __guid__ = 'svc.entityRecipeSvc'
    __exportedcalls__ = {'GetRecipe': [service.ROLE_ANY]}
    __notifyevents__ = ['OnCfgRevisionChange']

    def __init__(self):
        service.Service.__init__(self)
        self._cfgDataCallbacks = {}
        self._recipeClearCallbacks = weakref.WeakValueDictionary()



    def Run(self, *args):
        service.Service.Run(self, *args)
        self.recipes = {}
        self._RegisterCfgDataCallback('ingredients', lambda ingredientRow: self._ClearIngredientParent(ingredientRow.parentID, ingredientRow.parentType))
        self._RegisterCfgDataCallback('entityIngredientInitialValues', lambda initRow: self._ClearIngredientInit(initRow.ingredientID))
        self._RegisterCfgDataCallback('cefIngredients', lambda ingredientRow: self._ClearIngredientInit(ingredientRow.ingredientID))
        self._RegisterForBSDChanges()



    def _RegisterForBSDChanges(self):
        pass



    def _DoRegisterForBSDChanges(self):
        bsdTable = sm.GetService('bsdTable')
        bsdTable.RegisterForTableCacheChanges(const.cef.RECIPES_TABLE_FULL_NAME, self._HandleRecipeTableChange)
        bsdTable.RegisterForTableCacheChanges(const.cef.INGREDIENTS_TABLE_FULL_NAME, self._HandleIngredientTableChange)
        bsdTable.RegisterForTableCacheChanges(const.cef.INGREDIENT_INITS_TABLE_FULL_NAME, self._HandleIngredientInitTableChange)



    def GetRecipe(self, recipeID, overrideDict = None):
        recipe = self.recipes.get(recipeID, None)
        if recipe is None:
            recipe = self._LoadRecipe(recipeID)
        recipe = copy.deepcopy(recipe)
        if overrideDict is not None:
            self._IntegrateDicts(recipe, overrideDict)
        return recipe



    def _LoadRecipe(self, recipeID):
        recipeRow = cfg.recipes.GetIfExists(recipeID)
        if recipeRow is None:
            return {}
        if recipeRow.parentRecipeID:
            recipe = self.GetRecipe(recipeRow.parentRecipeID)
        else:
            recipe = {}
        ingredients = cfg.entityIngredientsByRecipeID.get(recipeID, [])
        for row in ingredients:
            if row.componentID not in recipe:
                recipe[row.componentID] = cef.BaseComponentView.GetDefaultRecipe(row.componentID)
            self._LoadInitValues(recipe[row.componentID], row.ingredientID)

        spawn = cfg.entitySpawnsByRecipeID.get(recipeID, None)
        if spawn:
            spawn = spawn[0]
            recipeWithDefaults = {}
            for (componentID, componentRecipe,) in recipe.iteritems():
                componentRecipe['_spawnID'] = spawn.spawnID
                defaultsDict = cef.BaseComponentView.GetDefaultRecipe(componentID, groupFilter=cef.BaseComponentView.ALL_STATIC)
                recipeWithDefaults[componentID] = defaultsDict

            self._IntegrateDicts(recipeWithDefaults, recipe)
            recipe = recipeWithDefaults
        for componentState in recipe.itervalues():
            componentState['_recipeID'] = recipeID

        self.recipes[recipeID] = recipe
        return recipe



    def GetSpawnRecipe(self, spawnID, overrideDict = None):
        spawnRow = cfg.entitySpawns.GetIfExists(spawnID)
        if spawnRow is None or spawnRow.recipeID is None:
            self.LogError('spawnID', spawnID, 'has no recipe set')
            return {}
        return self.GetRecipe(spawnRow.recipeID, overrideDict=overrideDict)



    def GetIngredient(self, ingredientID):
        return cfg.ingredients.GetIfExists(ingredientID)



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
            self._AddInitToRecipeDict(recipeComponent, row)




    def _AddInitToRecipeDict(self, recipeComponent, row):
        val = entityCommon.GetIngredientInitialValue(row)
        if row.keyName is None:
            recipeComponent[row.initialValueName] = val
        elif 'keyedData' not in recipeComponent:
            recipeComponent['keyedData'] = {}
        if row.keyName not in recipeComponent['keyedData']:
            recipeComponent['keyedData'][row.keyName] = {}
        recipeComponent['keyedData'][row.keyName][row.initialValueName] = val



    def _HandleRecipeTableChange(self, tableChanges):
        for ((recipeID,), (oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            self._ClearRecipe(recipeID)




    def _HandleIngredientTableChange(self, tableChanges):
        for ((ingredientID,), (oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            validKeyVal = oldDataKeyVal or newDataKeyVal
            self._ClearRecipe(validKeyVal.recipeID)




    def _HandleIngredientInitTableChange(self, tableChanges):
        for ((ingredientInitialValueID,), (oldDataKeyVal, newDataKeyVal,),) in tableChanges.iteritems():
            validKeyVal = oldDataKeyVal or newDataKeyVal
            self._ClearIngredientInit(validKeyVal.ingredientID)




    def OnCfgRevisionChange(self, uniqueRefName, cfgEntryName, cacheID, keyIDs, keyCols, oldRow, newRow):
        if newRow:
            self._HandleBsdCfgChange(uniqueRefName, newRow)
        else:
            self._HandleBsdCfgChange(uniqueRefName, oldRow)



    def _HandleBsdCfgChange(self, uniqueRefName, updatedRow):
        if uniqueRefName not in self._cfgDataCallbacks:
            return 
        self._cfgDataCallbacks[uniqueRefName](updatedRow)



    def _RegisterCfgDataCallback(self, uniqueRefName, callbackFunc):
        self._cfgDataCallbacks[uniqueRefName] = callbackFunc



    def _ClearIngredientInit(self, ingredientID):
        ingredientRow = self.GetIngredient(ingredientID)
        if ingredientRow is not None:
            self._ClearRecipe(ingredientRow.recipeID)



    def _ClearRecipe(self, recipeID):
        if recipeID in self.recipes:
            del self.recipes[recipeID]
            for childRecipeRow in cfg.recipesByParentRecipeID.get(recipeID, []):
                self._ClearRecipe(childRecipeRow.recipeID)

            weakSetCallbacks = self._recipeClearCallbacks.get(recipeID, [])
            for callback in weakSetCallbacks:
                callback(recipeID)




    def RegisterForRecipeClear(self, recipeID, callback):
        weakSet = self._recipeClearCallbacks.get(recipeID, None)
        if weakSet is None:
            weakSet = weakref.WeakSet()
            self._recipeClearCallbacks[recipeID] = weakSet
        weakSet.add(callback)
        if inspect.ismethod(callback):
            callback = callback.im_self
        else:
            callback
        recipeClearWeakSet = getattr(callback, 'recipeClearWeakSet', None)
        if recipeClearWeakSet is None:
            recipeClearWeakSet = []
            callback.recipeClearWeakSet = recipeClearWeakSet
        recipeClearWeakSet.append(weakSet)




