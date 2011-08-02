import util
import warObject
import blue

class WarsO(warObject.base):
    __guid__ = 'warObject.wars'

    def __init__(self, boundObject):
        warObject.base.__init__(self, boundObject)
        self.warsByOwnerID = {}
        self.warsEnded = []
        self.warsStarted = []



    def GetCostOfWarAgainst(self, ownerID):
        return self.GetMoniker().GetCostOfWarAgainst(ownerID)



    def GetWars(self, ownerID, forceRefresh = 0):
        if self.warsByOwnerID.has_key(ownerID):
            if forceRefresh or blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0]) > 43200000:
                del self.warsByOwnerID[ownerID]
        if not self.warsByOwnerID.has_key(ownerID):
            self.warsByOwnerID[ownerID] = [blue.os.GetTime(), self.GetMoniker().GetWars(ownerID)]
        return self.warsByOwnerID[ownerID][1]



    def OnWarChanged(self, warID, declaredByID, againstID, change):
        self.LogInfo('OnWarChanged warID:', warID, 'declaredByID:', declaredByID, 'againstID:', againstID, 'change:', change)
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        ids = [declaredByID, againstID]
        try:
            for ownerID in ids:
                if self.warsByOwnerID.has_key(ownerID):
                    warsForOwnerID = self.warsByOwnerID[ownerID]
                    (timestamp, indexRowSet,) = (warsForOwnerID[0], warsForOwnerID[1])
                    if bAdd and len(indexRowSet.header) != len(change):
                        bAdd = False
                    if bAdd:
                        self.LogInfo('OnWarChanged adding war')
                        if len(change) != len(indexRowSet.header):
                            self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                            return 
                        line = []
                        for columnName in indexRowSet.columns:
                            line.append(change[columnName][1])

                        indexRowSet[warID] = blue.DBRow(indexRowSet.header, line)
                    else:
                        if not indexRowSet.has_key(warID):
                            return 
                        if bRemove:
                            self.LogInfo('OnWarChanged removing war')
                            del indexRowSet[warID]
                        else:
                            self.LogInfo('OnWarChanged updating war')
                            war = indexRowSet[warID]
                            for columnName in indexRowSet.columns:
                                if not change.has_key(columnName):
                                    continue
                                setattr(war, columnName, change[columnName][1])



        finally:
            sm.GetService('corpui').OnWarChanged(warID, declaredByID, againstID, change)
            sm.GetService('state').RemoveWarOwners(declaredByID, againstID)
            sm.GetService('tactical').InvalidateFlags()




    def GetRelationship(self, ownerIDaskingAbout):
        if ownerIDaskingAbout == eve.session.corpid:
            return const.warRelationshipYourCorp
        if ownerIDaskingAbout == eve.session.allianceid:
            return const.warRelationshipYourAlliance
        wars = self.GetWars(eve.session.allianceid or eve.session.corpid)
        for war in wars.itervalues():
            if war.timeFinished is not None and war.timeFinished < blue.os.GetTime() - DAY:
                continue
            if ownerIDaskingAbout in [war.declaredByID, war.againstID]:
                if util.IsWarInHostileState(war):
                    return const.warRelationshipAtWarCanFight
                return const.warRelationshipAtWar

        return const.warRelationshipUnknown



    def CheckLazyWarCache(self, ownerID):
        lk = ('LWC', ownerID)
        lock = self.boundObject.LockService(lk)
        try:
            if self.warsByOwnerID.has_key(ownerID):
                if blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0]) > 43200000:
                    del self.warsByOwnerID[ownerID]
            self.GetWars(ownerID)

        finally:
            self.boundObject.UnLockService(lk, lock)




    def AreInAnyHostileWarStates(self, ownerID):
        self.CheckLazyWarCache(ownerID)
        warsForOwnerID = self.warsByOwnerID[ownerID]
        (timestamp, rows,) = (warsForOwnerID[0], warsForOwnerID[1])
        for row in rows.itervalues():
            if (row.declaredByID == ownerID or row.againstID == ownerID) and util.IsWarInHostileState(row):
                return 1

        return 0



    def CheckForStartOrEndOfWar(self):
        wars = self.GetWars(eve.session.allianceid or eve.session.corpid)
        yesterday = blue.os.GetTime() - (DAY + HOUR)
        lastday = blue.os.GetTime() - DAY
        for war in wars.itervalues():
            if war.timeFinished is not None and war.timeFinished >= yesterday and war.timeFinished < lastday:
                if war.warID not in self.warsEnded:
                    sm.GetService('state').RemoveWarOwners(war.declaredByID, war.againstID)
                    sm.GetService('tactical').InvalidateFlags()
                    self.warsEnded.append(war.warID)
                    continue
            if util.IsWarInHostileState(war):
                if war.timeDeclared >= yesterday and war.timeDeclared < lastday:
                    if war.warID not in self.warsStarted:
                        sm.GetService('state').RemoveWarOwners(war.declaredByID, war.againstID)
                        sm.GetService('tactical').InvalidateFlags()
                        self.warsStarted.append(war.warID)





