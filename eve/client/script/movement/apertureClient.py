import service
import util
import uthread

class ApertureClient(service.Service):
    __guid__ = 'svc.apertureClient'
    __notifyevents__ = ['ProcessEntityVisibility']
    __dependencies__ = []
    __componentTypes__ = ['aperture', 'apertureSubject']

    def Run(self, *etc):
        service.Service.Run(self)



    def CreateComponent(self, name, state):
        return None



    def _CreateEntity(self, sceneID, entityID, initialState):
        self.LogInfo('ApertureClient Creating entity', entityID, 'in scene', sceneID)
        self.entityService.CreateEntityFromServer(entityID, sceneID, initialState)



    def _RemoveEntity(self, entityID):
        self.LogInfo('ApertureClient Deleting entity', entityID)
        self.entityService.UnregisterAndDestroyEntityByID(entityID)



    def ProcessEntityVisibility(self, eventList):
        charid = session.charid
        playerEntityCreateIdx = None
        charactersCreated = []
        for (i, event,) in enumerate(eventList):
            if event[0] == 'OnEntityCreate' and event[2] == charid:
                eventList[i] = eventList[0]
                eventList[0] = event
                break

        callsToMake = []
        for t in eventList:
            if t[0] == 'OnEntityCreate':
                (eventName, sceneID, entityID, initialState,) = t
                callsToMake.append((self._CreateEntity, (sceneID, entityID, initialState)))
                if util.IsCharacter(entityID):
                    charactersCreated.append(entityID)
            elif t[0] == 'OnEntityDestroy':
                (eventName, entityID,) = t
                callsToMake.append((self._RemoveEntity, (entityID,)))
            else:
                self.LogError('Aperture Client received a unknown event type %s', str(t[0]))

        if charactersCreated:
            uthread.new(cfg.eveowners.Prime, charactersCreated)
        uthread.parallel(callsToMake)




