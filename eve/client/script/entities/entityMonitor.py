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




