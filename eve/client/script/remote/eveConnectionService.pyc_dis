#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/remote/eveConnectionService.py
import svc

class EveConnectionService(svc.connection):
    __guid__ = 'svc.eveConnection'
    __replaceservice__ = 'connection'
    __notifyevents__ = svc.connection.__notifyevents__ + ['OnStationOwnerChanged', 'ProcessSessionChange', 'OnStationInformationUpdated']

    def __init__(self):
        svc.connection.__init__(self)

    def ProcessSessionChange(self, isRemote, session, change):
        if 'stationid' in change and not session.stationid:
            eve.ClearStationItem()

    def OnStationOwnerChanged(self, ownerID):
        eve.SetStationItemBits((eve.stationItem.hangarGraphicID,
         ownerID,
         eve.stationItem.itemID,
         eve.stationItem.serviceMask,
         eve.stationItem.stationTypeID))

    def OnStationInformationUpdated(self, stationID):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('stationSvc', 'GetStation', stationID)