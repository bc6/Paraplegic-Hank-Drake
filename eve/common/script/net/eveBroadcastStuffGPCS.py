import base
import blue
import base
import service
import uthread
import macho
import sys
import gpcs

class BroadcastStuff(gpcs.CoreBroadcastStuff):
    __guid__ = 'gpcs.BroadcastStuff'

    def NarrowcastBySolarSystemIDs(self, solarsystemids, method, *args):
        if not solarsystemids:
            return 
        callTimer = base.CallTimer('NarrowcastBySolarSystemIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='solarsystemid', narrowcast=solarsystemids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastBySolarSystemID(self, solarsystemid, method, *args):
        callTimer = base.CallTimer('SinglecastBySolarSystemID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='solarsystemid', narrowcast=[solarsystemid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastBySolarSystemID2s(self, solarsystemid2s, method, *args):
        if not solarsystemid2s:
            return 
        callTimer = base.CallTimer('NarrowcastBySolarSystemID2s::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='solarsystemid2', narrowcast=solarsystemid2s), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastBySolarSystemID2(self, solarsystemid2, method, *args):
        callTimer = base.CallTimer('SinglecastBySolarSystemID2::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='solarsystemid2', narrowcast=[solarsystemid2]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByCorporationIDs(self, corpids, method, *args):
        if not corpids:
            return 
        callTimer = base.CallTimer('NarrowcastByCorporationIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='corpid', narrowcast=corpids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByCorporationID(self, corpid, method, *args):
        callTimer = base.CallTimer('SinglecastByCorporationID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='corpid', narrowcast=[corpid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByAllianceIDs(self, allianceids, method, *args):
        if not allianceids:
            return 
        callTimer = base.CallTimer('NarrowcastByAllianceIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='allianceid', narrowcast=allianceids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByAllianceID(self, allianceid, method, *args):
        callTimer = base.CallTimer('SinglecastByAllianceID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='allianceid', narrowcast=[allianceid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByFleetIDs(self, fleetids, method, *args):
        if not fleetids:
            return 
        callTimer = base.CallTimer('NarrowcastByFleetIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='fleetid', narrowcast=fleetids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByFleetID(self, fleetid, method, *args):
        callTimer = base.CallTimer('SinglecastByFleetID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='fleetid', narrowcast=[fleetid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByShipIDs(self, shipids, method, *args):
        if not shipids:
            return 
        callTimer = base.CallTimer('NarrowcastByShipIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='shipid', narrowcast=shipids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByShipID(self, shipid, method, *args):
        callTimer = base.CallTimer('SinglecastByShipID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='shipid', narrowcast=[shipid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByStationIDs(self, stationids, method, *args):
        if not stationids:
            return 
        callTimer = base.CallTimer('NarrowcastByStationIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='stationid', narrowcast=stationids), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByStationID(self, stationid, method, *args):
        callTimer = base.CallTimer('SinglecastByStationID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='stationid', narrowcast=[stationid]), payload=(1, args)))

        finally:
            callTimer.Done()




    def NarrowcastByStationID2s(self, stationid2s, method, *args):
        if not stationid2s:
            return 
        callTimer = base.CallTimer('NarrowcastByStationID2s::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='stationid2', narrowcast=stationid2s), payload=(1, args)))

        finally:
            callTimer.Done()




    def SinglecastByStationID2(self, stationid2, method, *args):
        callTimer = base.CallTimer('SinglecastByStationID2::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(macho.Notification(destination=macho.MachoAddress(broadcastID=method, idtype='stationid2', narrowcast=[stationid2]), payload=(1, args)))

        finally:
            callTimer.Done()





