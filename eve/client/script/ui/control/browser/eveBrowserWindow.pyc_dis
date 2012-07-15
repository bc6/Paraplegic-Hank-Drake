#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/control/browser/eveBrowserWindow.py
import uix
import uiutil
import xtriui
import form
import uthread
import blue
import urlparse
import browser
import log
import uiconst
import cgi
import uicls
import localization
import util

class BrowserWindow(uicls.BrowserWindowCore):
    __guid__ = 'uicls.BrowserWindow'
    __notifyevents__ = uicls.BrowserWindowCore.__notifyevents__
    __notifyevents__ += ['ProcessActiveShipChanged']

    def ApplyAttributes(self, attributes):
        uicls.BrowserWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_9_64_4')
        self.SetTopparentHeight(0)
        blue.pyos.synchro.Yield()
        uthread.new(self.ToggleButtonAppearance)

    def AddTrustedHeaderData(self):
        self.AddToAllTrustedSites('EVE_TRUSTED', 'Yes')
        self.AddToAllOtherSites('EVE_TRUSTED', 'No')
        self.AddToCCPTrustedSites('EVE_USERID', '%s' % eve.session.userid)
        self.AddToCCPTrustedSites('EVE_VERSION', '%s' % boot.build)
        if sm.GetService('machoNet').GetTransport('ip:packet:server') is not None and sm.GetService('machoNet').GetTransport('ip:packet:server').transport.address is not None:
            self.AddToAllTrustedSites('EVE_SERVERIP', sm.GetService('machoNet').GetTransport('ip:packet:server') and sm.GetService('machoNet').GetTransport('ip:packet:server').transport.address)
        if eve.session.charid:
            self.AddToAllTrustedSites('EVE_CHARNAME', eve.session.charid and cfg.eveowners.Get(eve.session.charid).name.encode('ascii', 'replace'))
            self.AddToAllTrustedSites('EVE_CHARID', '%s' % eve.session.charid)
        if eve.session.corpid:
            self.AddToAllTrustedSites('EVE_CORPNAME', eve.session.corpid and cfg.eveowners.Get(eve.session.corpid).name)
            self.AddToAllTrustedSites('EVE_CORPID', '%s' % eve.session.corpid)
        if eve.session.allianceid:
            self.AddToAllTrustedSites('EVE_ALLIANCENAME', eve.session.allianceid and cfg.eveowners.Get(eve.session.allianceid).name)
            self.AddToAllTrustedSites('EVE_ALLIANCEID', '%s' % eve.session.allianceid)
        if eve.session.regionid:
            self.AddToAllTrustedSites('EVE_REGIONNAME', eve.session.regionid and cfg.evelocations.Get(eve.session.regionid).name)
            self.AddToAllTrustedSites('EVE_REGIONID', eve.session.regionid)
        if eve.session.solarsystemid or eve.session.solarsystemid2:
            self.AddToAllTrustedSites('EVE_SOLARSYSTEMNAME', (eve.session.solarsystemid or eve.session.solarsystemid2) and cfg.evelocations.Get(eve.session.solarsystemid or eve.session.solarsystemid2).name)
            self.AddToAllTrustedSites('EVE_SOLARSYSTEMID', '%s' % (eve.session.solarsystemid or eve.session.solarsystemid2))
        if eve.session.constellationid:
            self.AddToAllTrustedSites('EVE_CONSTELLATIONNAME', eve.session.constellationid and cfg.evelocations.Get(eve.session.constellationid).name)
            self.AddToAllTrustedSites('EVE_CONSTELLATIONID', eve.session.constellationid)
        if eve.session.stationid:
            self.AddToAllTrustedSites('EVE_STATIONNAME', eve.session.stationid and cfg.evelocations.Get(eve.session.stationid).name)
            self.AddToAllTrustedSites('EVE_STATIONID', '%s' % eve.session.stationid)
        if eve.session.corprole:
            self.AddToAllTrustedSites('EVE_CORPROLE', '%s' % eve.session.corprole)
        if eve.session.warfactionid:
            self.AddToAllTrustedSites('EVE_WARFACTIONID', '%s' % eve.session.warfactionid)
        activeShipID = util.GetActiveShip()
        if activeShipID is not None:
            self.AddShipToAllTrustedSites(activeShipID)

    def OnSessionChanged(self, isRemote, sess, change):
        uicls.BrowserWindowCore.OnSessionChanged(self, isRemote, sess, change)
        if change.has_key('regionid'):
            if eve.session.regionid:
                self.AddToAllTrustedSites('EVE_REGIONNAME', eve.session.regionid and cfg.evelocations.Get(eve.session.regionid).name)
                self.AddToAllTrustedSites('EVE_REGIONID', '%s' % eve.session.regionid)
        if change.has_key('constellationid'):
            if eve.session.constellationid:
                self.AddToAllTrustedSites('EVE_CONSTELLATIONNAME', eve.session.constellationid and cfg.evelocations.Get(eve.session.constellationid).name)
                self.AddToAllTrustedSites('EVE_CONSTELLATIONID', '%s' % eve.session.constellationid)
        if change.has_key('solarsystemid') or change.has_key('solarsystemid2'):
            ssid = eve.session.solarsystemid or eve.session.solarsystemid2
            if ssid:
                self.AddToAllTrustedSites('EVE_SOLARSYSTEMNAME', ssid and cfg.evelocations.Get(ssid).name)
                self.AddToAllTrustedSites('EVE_SOLARSYSTEMID', '%s' % ssid)
        if change.has_key('corpid'):
            if eve.session.corpid:
                self.AddToAllTrustedSites('EVE_CORPNAME', eve.session.corpid and cfg.eveowners.Get(eve.session.corpid).name)
                self.AddToAllTrustedSites('EVE_CORPID', '%s' % eve.session.corpid)
        if change.has_key('stationid'):
            if eve.session.stationid:
                self.AddToAllTrustedSites('EVE_STATIONNAME', eve.session.stationid and cfg.evelocations.Get(eve.session.stationid).name)
                self.AddToAllTrustedSites('EVE_STATIONID', '%s' % eve.session.stationid)
            else:
                self.RemoveFromAllTrustedSites('EVE_STATIONNAME')
                self.RemoveFromAllTrustedSites('EVE_STATIONID')
        if change.has_key('allianceid'):
            if eve.session.allianceid:
                self.AddToAllTrustedSites('EVE_ALLIANCENAME', eve.session.allianceid and cfg.eveowners.Get(eve.session.allianceid).name)
                self.AddToAllTrustedSites('EVE_ALLIANCEID', '%s' % eve.session.allianceid)
            else:
                self.RemoveFromAllTrustedSites('EVE_ALLIANCENAME')
                self.RemoveFromAllTrustedSites('EVE_ALLIANCEID')
        if change.has_key('corprole'):
            self.AddToAllTrustedSites('EVE_CORPROLE', '%s' % eve.session.corprole or 0)
        if change.has_key('warfactionid'):
            self.AddToAllTrustedSites('EVE_WARFACTIONID', '%s' % eve.session.warfactionid)

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if shipID is not None:
            self.AddShipToAllTrustedSites(shipID)
        else:
            self.RemoveShipFromAllTrustedSites()

    def AddShipToAllTrustedSites(self, shipID):
        self.AddToAllTrustedSites('EVE_SHIPID', '%s' % shipID)
        self.AddToAllTrustedSites('EVE_SHIPNAME', cfg.evelocations.Get(shipID).name.encode('ascii', 'replace'))
        shipDogmaItem = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDogmaItem(shipID)
        shipTypeID = shipDogmaItem.typeID
        self.AddToAllTrustedSites('EVE_SHIPTYPEID', '%s' % shipTypeID)
        self.AddToAllTrustedSites('EVE_SHIPTYPENAME', cfg.invtypes.Get(shipTypeID).name)

    def RemoveShipFromAllTrustedSites(self):
        self.RemoveFromAllTrustedSites('EVE_SHIPID')
        self.RemoveFromAllTrustedSites('EVE_SHIPNAME')
        self.RemoveFromAllTrustedSites('EVE_SHIPTYPEID')
        self.RemoveFromAllTrustedSites('EVE_SHIPTYPENAME')

    def ToggleButtonAppearance(self):
        if self and not self.destroyed and hasattr(self, 'tabButtons'):
            for btn in self.tabButtons:
                btn.LiteMode(True)