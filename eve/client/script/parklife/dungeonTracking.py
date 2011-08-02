import service
import util

class DungeonTracking(service.Service):
    __guid__ = 'svc.dungeonTracking'
    __notifyevents__ = ['ProcessSessionChange', 'OnDistributionDungeonEntered', 'OnEscalatingPathDungeonEntered']

    def __init__(self):
        service.Service.__init__(self)
        self.distributionDungeonsEntered = None
        self.escalatingPathDungeonsEntered = None



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)



    def ProcessSessionChange(self, isRemote, session, change):
        if change.has_key('locationid'):
            self.distributionDungeonsEntered = None
            self.escalatingPathDungeonsEntered = None



    def OnDistributionDungeonEntered(self, row):
        if self.distributionDungeonsEntered is None:
            self.distributionDungeonsEntered = util.Rowset(row.header)
        self.distributionDungeonsEntered.append(row)



    def OnEscalatingPathDungeonEntered(self, row):
        if self.escalatingPathDungeonsEntered is None:
            self.escalatingPathDungeonsEntered = util.Rowset(row.header)
        self.escalatingPathDungeonsEntered.append(row)



    def GetDistributionDungeonsEntered(self):
        return self.distributionDungeonsEntered



    def GetEscalatingPathDungeonsEntered(self):
        return self.escalatingPathDungeonsEntered




