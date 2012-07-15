#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/parklife/overviewPresetSvc.py
from service import Service
import util

class OverviewPresetSvc(Service):
    __guid__ = 'svc.overviewPresetSvc'
    __displayName__ = 'Overview Preset Service'
    __serviceName__ = 'This service handles overview presets'
    __update_on_reload__ = 1

    def Run(self, *args):
        Service.Run(self, *args)
        self.isLoaded = False

    def LoadDataIfNeeded(self):
        if not self.isLoaded:
            self.defaultOverviews = dict()
            if hasattr(cfg, 'overviewDefaults') and hasattr(cfg.overviewDefaults, 'data'):
                for key in cfg.overviewDefaults.data:
                    row = cfg.overviewDefaults.Get(key)
                    o = util.KeyVal()
                    o.row = row
                    o.groups = []
                    for groupRow in cfg.overviewDefaultGroups[row.overviewID]:
                        o.groups.append(groupRow.groupID)

                    self.defaultOverviews[row.overviewShortName] = o

            self.sortedDefaultOverviewNames = sorted(self.defaultOverviews.iterkeys(), key=lambda k: self.defaultOverviews[k].row.overviewName)
            self.isLoaded = True

    def GetDefaultOverviewNameList(self):
        self.LoadDataIfNeeded()
        return self.sortedDefaultOverviewNames

    def GetDefaultOverviewName(self, name):
        self.LoadDataIfNeeded()
        if name in self.defaultOverviews:
            return self.defaultOverviews[name].row.overviewName

    def GetDefaultOverviewGroups(self, name):
        self.LoadDataIfNeeded()
        if name in self.defaultOverviews:
            return self.defaultOverviews[name].groups
        return []