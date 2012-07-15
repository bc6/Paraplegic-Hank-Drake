#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/entities/ActionObjectClient.py
import svc
import localization

class EveActionObjectClientSvc(svc.actionObjectClientSvc):
    __guid__ = 'svc.eveActionObjectClientSvc'
    __replaceservice__ = 'actionObjectClientSvc'

    def SetupComponent(self, entity, component):
        infoComponent = entity.GetComponent('info')
        if infoComponent and not infoComponent.name and component in self.preservedStates:
            recipeRow = cfg.recipes.Get(self.preservedStates[component]['_recipeID'])
            infoComponent.name = recipeRow.recipeName
        svc.actionObjectClientSvc.SetupComponent(self, entity, component)

    def Run(self, *args):
        svc.actionObjectClientSvc.Run(self, *args)

    def GetActionNodeTranslatedText(self, actionID, fallbackText):
        treeNodeNameID = cfg.treeNodes.Get(actionID).treeNodeNameID
        return localization.GetByMessageID(treeNodeNameID)