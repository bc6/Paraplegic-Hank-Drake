#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/shared/neocom/assetsinfo.py
import service
import blue
import uthread
import uiutil
import form
import util
import localization

class AssetsSvc(service.Service):
    __exportedcalls__ = {'Show': [],
     'SetHint': []}
    __guid__ = 'svc.assets'
    __notifyevents__ = ['OnSessionChanged',
     'OnItemChange',
     'OnItemNameChange',
     'OnPostCfgDataChanged']
    __servicename__ = 'assets'
    __displayname__ = 'Assets Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Assets')
        self.locationCache = {}

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.Close()

    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
        else:
            wnd = self.GetWnd()
            if wnd and not wnd.destroyed:
                uthread.new(wnd.Refresh)

    def OnItemChange(self, item, change):
        itemLocationIDs = [item.locationID]
        if const.ixLocationID in change:
            itemLocationIDs.append(change[const.ixLocationID])
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            if change.keys() == [const.ixLocationID] and change.values() == [0]:
                return
            if util.IsStation(item.locationID) or const.ixLocationID in change and util.IsStation(change[const.ixLocationID]):
                key = wnd.sr.maintabs.GetSelectedArgs()
                if key is not None:
                    if key[:7] == 'station':
                        if util.IsSolarSystem(item.locationID) and const.ixLocationID in change and change[const.ixLocationID] == eve.session.stationid:
                            return
                        if eve.session.stationid in itemLocationIDs:
                            wnd.sr.maintabs.ReloadVisible()
                    elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
                        uthread.new(wnd.UpdateLite, item.locationID, key, change.get(const.ixLocationID, item.locationID))

    def OnItemNameChange(self):
        wnd = self.GetWnd(0)
        if wnd:
            wnd.Refresh()

    def Show(self, stationID = None):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            if stationID is not None:
                wnd.sr.maintabs.ShowPanelByName(localization.GetByLabel('UI/Inventory/Inventory/AssetsWindow/AllItems'))
                blue.pyos.synchro.Yield()
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ == 'listentry.Group':
                        if entry.id == ('assetslocations_allitems', stationID):
                            uicore.registry.SetListGroupOpenState(('assetslocations_allitems', stationID), 1)
                            wnd.sr.scroll.PrepareSubContent(entry)
                            wnd.sr.scroll.ShowNodeIdx(entry.idx)

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed and wnd.key and wnd.key[:7] == 'station':
                wnd.sr.maintabs.ReloadVisible()

    def GetAll(self, key, blueprintOnly = 0, isCorp = 0, keyID = None, sortKey = 0):
        stations = self.GetStations(blueprintOnly, isCorp)
        sortlocations = []
        mapSvc = sm.StartService('map')
        uiSvc = sm.StartService('ui')
        for station in stations:
            blue.pyos.BeNice()
            solarsystemID = uiSvc.GetStation(station.stationID).solarSystemID
            loc = self.locationCache.get(solarsystemID, None)
            if loc is None:
                constellationID = mapSvc.GetParent(solarsystemID)
                loc = self.locationCache.get(constellationID, None)
                if loc is None:
                    regionID = mapSvc.GetParent(constellationID)
                    loc = (solarsystemID, constellationID, regionID)
                else:
                    regionID = loc[2]
                self.locationCache[solarsystemID] = loc
                self.locationCache[constellationID] = loc
                self.locationCache[regionID] = loc
            else:
                constellationID = loc[1]
                regionID = loc[2]
            if key == 'allitems':
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'sysitems':
                if solarsystemID == (keyID or eve.session.solarsystemid2):
                    sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'conitems' and constellationID == (keyID or eve.session.constellationid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'regitems' and regionID == (keyID or eve.session.regionid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))

        sortlocations = uiutil.SortListOfTuples(sortlocations)
        return sortlocations

    def GetStations(self, blueprintOnly = 0, isCorp = 0):
        stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations(blueprintOnly, isCorp)
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        return stations

    def GetWnd(self, new = 0):
        if new:
            return form.AssetsWindow.Open()
        return form.AssetsWindow.GetIfOpen()

    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.SetHint(hintstr)