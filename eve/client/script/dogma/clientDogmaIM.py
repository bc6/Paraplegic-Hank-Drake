import service
import dogmax
import util

class ClientDogmaInstanceManager(service.Service):
    __guid__ = 'svc.clientDogmaIM'
    __startupdependencies__ = ['clientEffectCompiler', 'invCache', 'godma']
    __notifyevents__ = ['ProcessSessionChange']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.dogmaLocation = None
        self.nextKey = 0



    def GetDogmaLocation(self, *args):
        if self.dogmaLocation is None:
            self.dogmaLocation = dogmax.DogmaLocation(self)
        return self.dogmaLocation



    def GodmaItemChanged(self, item, change):
        if self.dogmaLocation is not None:
            shipID = self.dogmaLocation.shipID
            if item.locationID in (shipID, session.charid):
                self.dogmaLocation.OnItemChange(item, change)
            elif change.get(const.ixLocationID, None) in (shipID, session.charid):
                self.dogmaLocation.OnItemChange(item, change)
            elif item.itemID == shipID and session.stationid2 is not None:
                if item.locationID != session.stationid or item.flagID != const.flagHangar:
                    if util.IsWorldSpace(item.locationID) or util.IsSolarSystem(item.locationID):
                        self.LogInfo('ActiveShip moved as we are undocking. Ignoring')
                    elif util.IsStation(item.locationID) and item.flagID == const.flagHangar and item.ownerID == session.charid:
                        self.LogInfo("Active ship moved stations but is still in it's hangar", item, change, session.stationid)
                    else:
                        sm.GetService('station').TryLeaveShip(item)
                        self.LogError('Our active ship got moved', item, change)



    def ProcessSessionChange(self, isRemote, session, change):
        if self.dogmaLocation is None:
            return 
        if 'stationid2' in change or 'solarsystemid' in change:
            self.dogmaLocation.UpdateRemoteDogmaLocation()



    def GetCapacityForItem(self, itemID, attributeID):
        if self.dogmaLocation is None:
            return 
        if not self.dogmaLocation.IsItemLoaded(itemID):
            return 
        return self.dogmaLocation.GetAttributeValue(itemID, attributeID)




