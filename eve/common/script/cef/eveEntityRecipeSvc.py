import svc

class EveEntityRecipeService(svc.entityRecipeSvc):
    __guid__ = 'svc.EveEntityRecipeService'
    __replaceservice__ = 'entityRecipeSvc'

    def Run(self, *args):
        svc.entityRecipeSvc.Run(self, *args)
        self._RegisterCfgDataCallback('invtypes', lambda typeRow: self._ClearTypeRecipe(typeRow.typeID))
        self._RegisterCfgDataCallback('invgroups', lambda groupRow: self._ClearGroupRecipe(groupRow.groupID))
        self._RegisterCfgDataCallback('invcategories', lambda categoryRow: self._ClearCategoryRecipe(categoryRow.categoryID))




