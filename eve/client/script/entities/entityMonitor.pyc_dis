#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/entities/entityMonitor.py
import uicls
import util

class EveEntityBrowser(uicls.EntityBrowserCore):
    __guid__ = 'uicls.EntityBrowser'

    def GetSceneName(self, sceneID):
        return cfg.evelocations.Get(sceneID).name

    def GetEntityName(self, entity):
        if entity.HasComponent('info'):
            return entity.GetComponent('info').name
        try:
            if util.IsCharacter(entity.entityID):
                return cfg.eveowners.Get(entity.entityID).name
        except:
            pass

        return 'Entity %s' % entity.entityID

    def GetEntitySpawnID(self, entity):
        if entity.HasComponent('info') and entity.info.spawnID:
            return entity.info.spawnID
        return 'UNKNOWN'

    def GetEntityRecipeID(self, entity):
        if entity.HasComponent('info') and entity.info.recipeID:
            return entity.info.recipeID
        return 'UNKNOWN'