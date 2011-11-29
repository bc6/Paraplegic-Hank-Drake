import util
import allianceObject
import blue

class AllianceO(allianceObject.base):
    __guid__ = 'allianceObject.alliance'

    def __init__(self, boundObject):
        allianceObject.base.__init__(self, boundObject)
        self.alliancesByAllianceID = None
        self.rankedAlliances = util.KeyVal(time=None, alliances=None, standings=None, maxLen=None)



    def DoSessionChanging(self, isRemote, session, change):
        pass



    def GetRankedAlliances(self, maxLen = 100):
        if self.rankedAlliances.time is not None:
            if self.rankedAlliances.maxLen != maxLen or blue.os.TimeDiffInMs(self.rankedAlliances.time, blue.os.GetWallclockTime()) > 5000:
                self.rankedAlliances.time = None
        if self.rankedAlliances.time is None:
            self.rankedAlliances.time = blue.os.GetWallclockTime()
            self.rankedAlliances.maxLen = maxLen
            self.rankedAlliances.alliances = sm.RemoteSvc('allianceRegistry').GetRankedAlliances(maxLen)
            self.rankedAlliances.standings = {}
            for a in self.rankedAlliances.alliances:
                s = sm.GetService('standing').GetStanding(eve.session.corpid, a.allianceID)
                self.rankedAlliances.standings[a.allianceID] = s

        return self.rankedAlliances



    def UpdateAlliance(self, description, url):
        return self.GetMoniker().UpdateAlliance(description, url)



    def GetAlliance(self, allianceID = None):
        if allianceID is None:
            allianceID = eve.session.allianceid
        if allianceID is None:
            raise RuntimeError('NoSuchAlliance')
        if self.alliancesByAllianceID is not None and self.alliancesByAllianceID.has_key(allianceID):
            return self.alliancesByAllianceID[allianceID]
        alliance = None
        if allianceID == eve.session.allianceid:
            alliance = self.GetMoniker().GetAlliance()
        else:
            alliance = sm.RemoteSvc('allianceRegistry').GetAlliance(allianceID)
        self.LoadAlliance(alliance)
        return self.alliancesByAllianceID[allianceID]



    def LoadAlliance(self, alliance):
        if self.alliancesByAllianceID is None:
            self.alliancesByAllianceID = util.IndexRowset(alliance.header, [alliance.line], 'allianceID')
        else:
            line = []
            for columnName in self.alliancesByAllianceID.header:
                line.append(getattr(alliance, columnName))

            self.alliancesByAllianceID[alliance.allianceID] = line



    def OnAllianceChanged(self, allianceID, change):
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        if self.alliancesByAllianceID is not None:
            if bAdd:
                if len(change) != len(self.alliancesByAllianceID.header):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return 
                line = []
                for columnName in self.alliancesByAllianceID.header:
                    line.append(change[columnName][1])

                self.alliancesByAllianceID[allianceID] = line
            elif not self.alliancesByAllianceID.has_key(allianceID):
                return 
            if bRemove:
                del self.alliancesByAllianceID[allianceID]
            else:
                alliance = self.alliancesByAllianceID[allianceID]
                for columnName in alliance.header:
                    if not change.has_key(columnName):
                        continue
                    setattr(alliance, columnName, change[columnName][1])

                if cfg.allianceshortnames.data.has_key(allianceID):
                    header = cfg.allianceshortnames.header
                    line = cfg.allianceshortnames.data[allianceID]
                    i = -1
                    for columnName in header:
                        i = i + 1
                        if not change.has_key(columnName):
                            continue
                        line[i] = change[columnName][1]

        sm.GetService('corpui').OnAllianceChanged(allianceID, change)




