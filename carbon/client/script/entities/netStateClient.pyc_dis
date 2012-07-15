#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/client/script/entities/netStateClient.py
import service

class NetStateClient(service.Service):
    __guid__ = 'svc.netStateClient'
    __notifyevents__ = ['OnReceiveNetState']

    def Run(self, *etc):
        self.IsVerboseMode = True

    def _LogVerbose(self, *args, **keywords):
        if self.IsVerboseMode:
            self.LogInfo(args, keywords)

    def _ApplyEntityUpdates(self, ent, entityUpdates):
        for compName, componentUpdates in entityUpdates:
            component = getattr(ent, compName)
            self._ApplyComponentUpdates(component, componentUpdates)

    def _ApplyComponentUpdates(self, component, componentUpdates):
        for attrName, val in componentUpdates.iteritems():
            setattr(component, attrName, val)

    def OnReceiveNetState(self, entityID, entityUpdates):
        receivingEntity = self.entityService.FindEntityByID(entityID)
        self._LogVerbose('OnReceiveNetState for', receivingEntity, 'ID:', entityID, 'with:', entityUpdates)
        self._ApplyEntityUpdates(receivingEntity, entityUpdates)