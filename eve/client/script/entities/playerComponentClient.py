import util
import svc

class EvePlayerComponentClient(svc.playerComponentClient):
    __guid__ = 'svc.EvePlayerComponentClient'
    __replaceservice__ = 'playerComponentClient'

    def RegisterComponent(self, entity, component):
        if entity.entityID != session.charid:
            ctx = entity.GetComponent('contextMenu')
            if ctx:
                if util.IsCharacter(entity.entityID):
                    ctx.AddMenuEntry(mls.UI_CMD_SHOWINFO, self.ShowInfo)
        if entity.HasComponent('info'):
            if self.entityService.IsClientSideOnly(entity.scene.sceneID):
                infoComponent = entity.GetComponent('info')
                infoComponent.name = cfg.eveowners.Get(entity.entityID).ownerName



    def ShowInfo(self, entityID):
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(entityID).typeID, entityID)




