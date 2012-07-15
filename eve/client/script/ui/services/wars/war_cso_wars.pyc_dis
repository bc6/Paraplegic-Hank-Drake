#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/wars/war_cso_wars.py
import util
import warObject
import blue
import warUtil
import itertools

class WarsO(warObject.base):
    __guid__ = 'warObject.wars'

    def __init__(self, boundObject):
        warObject.base.__init__(self, boundObject)
        self.warsByOwnerID = {}
        self.warsByWarID = {}
        self.warsEnded = []
        self.warsStarted = []

    def GetCostOfWarAgainst(self, ownerID):
        return self.GetMoniker().GetCostOfWarAgainst(ownerID)

    def GetWars(self, ownerID, forceRefresh = 0):
        if ownerID in self.warsByOwnerID:
            if forceRefresh or blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0], blue.os.GetWallclockTime()) > 43200000:
                del self.warsByOwnerID[ownerID]
        if ownerID not in self.warsByOwnerID:
            wars = self.GetMoniker().GetWars(ownerID)
            self.warsByWarID.update({war.warID:war for war in wars.itervalues()})
            warsByOwnerID = {war.warID for war in wars.itervalues()}
            self.warsByOwnerID[ownerID] = (blue.os.GetWallclockTime(), warsByOwnerID)
            usedWarIDs = set()
            for lastUpdated, warIDs in self.warsByOwnerID.itervalues():
                usedWarIDs.update(warIDs)

            for warID in self.warsByWarID.keys():
                if warID not in usedWarIDs:
                    del self.warsByWarID[warID]

        warIDs = self.warsByOwnerID[ownerID][1]
        return {warID:self.warsByWarID[warID] for warID in warIDs if warID in self.warsByWarID}

    def OnWarChanged(self, war, ownerIDs, change):
        try:
            warsByOwnerID = {ownerID:warIDs for ownerID, (lastUpdated, warIDs) in self.warsByOwnerID.iteritems()}
            warUtil.HandleWarChange(war, self.warsByWarID, warsByOwnerID, ownerIDs, change)
        finally:
            sm.GetService('corpui').OnWarChanged(war, ownerIDs, change)
            sm.GetService('state').RemoveWarOwners(ownerIDs)
            sm.GetService('tactical').InvalidateFlags()

    def GetRelationship(self, ownerID):
        if ownerID == eve.session.corpid:
            return const.warRelationshipYourCorp
        if ownerID == eve.session.allianceid:
            return const.warRelationshipYourAlliance
        myWarEntityID = session.corpid if session.allianceid is None else session.allianceid
        wars = self.GetWars(myWarEntityID)
        entities = (ownerID, myWarEntityID)
        if util.IsAtWar(wars.itervalues(), entities):
            return const.warRelationshipAtWarCanFight
        for war in wars.itervalues():
            if myWarEntityID == war.againstID and ownerID in war.allies:
                return const.warRelationshipAlliesAtWar
            if ownerID == war.againstID and myWarEntityID in war.allies:
                return const.warRelationshipAlliesAtWar
            if ownerID in war.allies and myWarEntityID in war.allies:
                return const.warRelationshipAlliesAtWar

        return const.warRelationshipUnknown

    def CheckLazyWarCache(self, ownerID):
        lk = ('LWC', ownerID)
        lock = self.boundObject.LockService(lk)
        try:
            if self.warsByOwnerID.has_key(ownerID):
                if blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0], blue.os.GetWallclockTime()) > 43200000:
                    del self.warsByOwnerID[ownerID]
            self.GetWars(ownerID)
        finally:
            self.boundObject.UnLockService(lk, lock)

    def AreInAnyHostileWarStates(self, ownerID):
        self.CheckLazyWarCache(ownerID)
        warsForOwnerID = self.warsByOwnerID[ownerID]
        timestamp, warIDs = warsForOwnerID[0], warsForOwnerID[1]
        for warID in warIDs:
            war = self.warsByWarID[warID]
            if (war.declaredByID == ownerID or war.againstID == ownerID or ownerID in war.allies) and util.IsWarInHostileState(war):
                return 1

        return 0

    def CheckForStartOrEndOfWar(self):
        wars = self.GetWars(eve.session.allianceid or eve.session.corpid)
        yesterday = blue.os.GetWallclockTime() - (DAY + HOUR)
        lastday = blue.os.GetWallclockTime() - DAY
        for war in wars.itervalues():
            if war.timeFinished is not None and war.timeFinished >= yesterday and war.timeFinished < lastday:
                if war.warID not in self.warsEnded:
                    sm.GetService('state').RemoveWarOwners(itertools.chain([war.declaredByID, war.againstID], war.allies))
                    sm.GetService('tactical').InvalidateFlags()
                    self.warsEnded.append(war.warID)
                    continue
            if util.IsWarInHostileState(war):
                if war.timeDeclared >= yesterday and war.timeDeclared < lastday:
                    if war.warID not in self.warsStarted:
                        sm.GetService('state').RemoveWarOwners(itertools.chain([war.declaredByID, war.againstID], war.allies))
                        sm.GetService('tactical').InvalidateFlags()
                        self.warsStarted.append(war.warID)

    def IsAllyInWar(self, warID):
        warEntityID = session.allianceid or session.corpid
        war = self.warsByWarID.get(warID, None)
        if war is None:
            return False
        allyRow = war.allies.get(warEntityID, None)
        if allyRow is not None and allyRow.timeFinished > blue.os.GetWallclockTime():
            return True
        return False