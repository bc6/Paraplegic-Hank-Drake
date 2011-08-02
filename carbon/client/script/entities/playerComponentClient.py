import service
import collections
import uthread

class PlayerClientComponent(object):
    __guid__ = 'entities.PlayerClientComponent'


class PlayerComponentClient(service.Service):
    __guid__ = 'svc.playerComponentClient'
    __exportedcalls__ = {}
    __notifyevents__ = []
    __componentTypes__ = ['player']

    def CreateComponent(self, name, state):
        component = PlayerClientComponent()
        return component



    def RegisterComponent(self, entity, component):
        pass



    def UnRegisterComponent(self, entity, component):
        pass



    def NetworkSyncComponent(self, entity, component):
        if self.entityService.IsClientSideOnly(entity.scene.sceneID):
            return 
        if entity.entityID == session.charid:
            self.LogInfo('PlayerClientComponent tearing down, will send a PlayerComponentRegistered to server now')
            uthread.new(sm.RemoteSvc('playerComponentServer').PlayerComponentRegistered, entity.scene.sceneID)



    def TearDownComponent(self, entity, component):
        if self.entityService.IsClientSideOnly(entity.scene.sceneID):
            return 
        if entity.entityID == session.charid:
            self.LogInfo('PlayerClientComponent Registering, will send a PlayerComponentRegistered to server now')
            uthread.new(sm.RemoteSvc('playerComponentServer').PlayerComponentRegistered, entity.scene.sceneID)



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        return report




