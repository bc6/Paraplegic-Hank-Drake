import util
import corpObject
import blue

class WarsO(corpObject.base):
    __guid__ = 'corpObject.wars'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)



    def DoSessionChanging(self, isRemote, session, change):
        pass



    def RetractWar(self, againstID):
        if eve.session.allianceid is not None:
            raise RuntimeError('YouAreInAnAllianceSoCallOnThatService')
        return self.GetCorpRegistry().RetractWar(againstID)



    def ChangeMutualWarFlag(self, warID, mutual):
        if eve.session.allianceid is not None:
            raise RuntimeError('YouAreInAnAllianceSoCallOnThatService')
        return self.GetCorpRegistry().ChangeMutualWarFlag(warID, mutual)



    def GetRecentKills(self, num, offset):
        shipKills = self.GetCorpRegistry().GetRecentKillsAndLosses(num, offset)
        return [ k for k in shipKills if k.finalCorporationID == eve.session.corpid ]



    def GetRecentLosses(self, num, offset):
        shipKills = self.GetCorpRegistry().GetRecentKillsAndLosses(num, offset)
        return [ k for k in shipKills if k.victimCorporationID == eve.session.corpid ]




