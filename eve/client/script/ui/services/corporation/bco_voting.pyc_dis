#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/corporation/bco_voting.py
import util
import dbutil
import corpObject
import blue
import uthread

class VotingO(corpObject.base):
    __guid__ = 'corpObject.voting'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.__voteCaseOptionsRD = None
        self.Reset()

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.Reset()

    def Reset(self):
        self.__voteCasesByCorporation = {}
        self.__voteCaseOptionsByCorporation = {}
        self.__votesByCorpIDByVoteCaseID = {}
        self.CanViewVotes_ = None

    def GetVoteCasesByCorporation(self, corpid, status = 0, maxLen = 0):
        if status == 0:
            if not self.__voteCasesByCorporation.has_key(corpid):
                self.__voteCasesByCorporation[corpid] = self.GetCorpRegistry().GetVoteCasesByCorporation(corpid)
            return self.__voteCasesByCorporation[corpid]
        else:
            return self.GetCorpRegistry().GetVoteCasesByCorporation(corpid, status, maxLen)

    def GetVoteCaseOptions(self, voteCaseID, corpID = None):
        if corpID not in self.__voteCaseOptionsByCorporation:
            self.__voteCaseOptionsByCorporation[corpID] = {}
        if voteCaseID not in self.__voteCaseOptionsByCorporation[corpID]:
            self.__voteCaseOptionsByCorporation[corpID][voteCaseID] = self.GetCorpRegistry().GetVoteCaseOptions(corpID, voteCaseID)
            self.__voteCaseOptionsRD = self.__voteCaseOptionsByCorporation[corpID][voteCaseID].header
        return self.__voteCaseOptionsByCorporation[corpID][voteCaseID]

    def GetVotes(self, corpID, voteCaseID):
        if not self.__votesByCorpIDByVoteCaseID.has_key(corpID):
            self.__votesByCorpIDByVoteCaseID[corpID] = {}
        if not self.__votesByCorpIDByVoteCaseID[corpID].has_key(voteCaseID):
            self.__votesByCorpIDByVoteCaseID[corpID][voteCaseID] = self.GetCorpRegistry().GetVotes(corpID, voteCaseID)
        return self.__votesByCorpIDByVoteCaseID[corpID][voteCaseID]

    def InsertVoteCase(self, voteCaseText, description, corporationID, voteType, voteCaseOptions, startDateTime = None, endDateTime = None):
        return self.GetCorpRegistry().InsertVoteCase(voteCaseText, description, corporationID, voteType, voteCaseOptions, startDateTime, endDateTime)

    def InsertVote(self, corporationID, voteCaseID, voteValue):
        return self.GetCorpRegistry().InsertVote(corporationID, voteCaseID, voteValue)

    def OnCorporationVoteCaseChanged(self, corporationID, voteCaseID, change):
        try:
            if self.__voteCasesByCorporation.has_key(corporationID):
                bAdd, bRemove = self.GetAddRemoveFromChange(change)
                if bAdd:
                    row = blue.DBRow(self.__voteCasesByCorporation[corporationID].header)
                    for columnName, values in change.iteritems():
                        setattr(row, columnName, change[columnName][1])

                    self.__voteCasesByCorporation[corporationID][voteCaseID] = row
                    if self.__voteCasesByCorporation[corporationID][voteCaseID].voteType == const.voteCEO:
                        self.corp__members.MemberCanRunForCEO_ = None
                elif bRemove:
                    if self.__voteCasesByCorporation[corporationID].has_key(voteCaseID):
                        del self.__voteCasesByCorporation[corporationID][voteCaseID]
                elif self.__voteCasesByCorporation[corporationID].has_key(voteCaseID):
                    row = self.__voteCasesByCorporation[corporationID][voteCaseID]
                    for columnName, oldAndNewValue in change.iteritems():
                        oldValue, newValue = oldAndNewValue
                        setattr(row, columnName, newValue)

        finally:
            uthread.new(self.OnCorporationVoteCaseChanged_thread, corporationID, voteCaseID, change).context = 'svc.corp.OnCorporationVoteCaseChanged'

    def OnCorporationVoteCaseChanged_thread(self, corporationID, voteCaseID, change):
        sm.GetService('corpui').OnCorporationVoteCaseChanged(corporationID, voteCaseID, change)

    def OnCorporationVoteCaseOptionChanged(self, corporationID, voteCaseID, optionID, change):
        try:
            if corporationID in self.__voteCaseOptionsByCorporation:
                bAdd, bRemove = self.GetAddRemoveFromChange(change)
                if bAdd:
                    header = self.__voteCaseOptionsRD
                    if header is None:
                        self.GetVoteCaseOptions(voteCaseID, corporationID)
                        header = self.__voteCaseOptionsRD
                    if voteCaseID not in self.__voteCaseOptionsByCorporation[corporationID]:
                        self.__voteCaseOptionsByCorporation[corporationID][voteCaseID] = dbutil.CIndexedRowset(header, 'optionID')
                    line = blue.DBRow(header)
                    for columnName in header.Keys():
                        setattr(line, columnName, change[columnName][1])

                    self.__voteCaseOptionsByCorporation[corporationID][voteCaseID][optionID] = line
                elif bRemove:
                    if self.__voteCaseOptionsByCorporation[corporationID].has_key(voteCaseID):
                        if self.__voteCaseOptionsByCorporation[corporationID][voteCaseID].has_key(optionID):
                            del self.__voteCaseOptionsByCorporation[corporationID][voteCaseID][optionID]
                elif self.__voteCaseOptionsByCorporation[corporationID].has_key(voteCaseID):
                    row = self.__voteCaseOptionsByCorporation[corporationID][voteCaseID][optionID]
                    for columnName, oldAndNewValue in change.iteritems():
                        oldValue, newValue = oldAndNewValue
                        setattr(row, columnName, newValue)

        finally:
            uthread.new(self.OnCorporationVoteCaseOptionChanged_thread, corporationID, voteCaseID, optionID, change).context = 'svc.corp.OnCorporationVoteCaseOptionChanged'

    def OnCorporationVoteCaseOptionChanged_thread(self, corporationID, voteCaseID, optionID, change):
        sm.GetService('corpui').OnCorporationVoteCaseOptionChanged(corporationID, voteCaseID, optionID, change)

    def OnCorporationVoteChanged(self, corporationID, voteCaseID, characterID, change):
        try:
            if self.__votesByCorpIDByVoteCaseID.has_key(corporationID):
                bAdd, bRemove = self.GetAddRemoveFromChange(change)
                if bAdd:
                    header = None
                    for indexRowset in self.__votesByCorpIDByVoteCaseID[corporationID].itervalues():
                        header = indexRowset.header
                        break

                    line = []
                    for columnName in header:
                        line.append(change[columnName][1])

                    if not self.__votesByCorpIDByVoteCaseID[corporationID].has_key(voteCaseID):
                        self.__votesByCorpIDByVoteCaseID[corporationID][voteCaseID] = util.IndexRowset(header, None, 'characterID')
                    self.__votesByCorpIDByVoteCaseID[corporationID][voteCaseID][characterID] = line
                elif bRemove:
                    if self.__votesByCorpIDByVoteCaseID[corporationID].has_key(voteCaseID):
                        if self.__votesByCorpIDByVoteCaseID[corporationID][voteCaseID].has_key(characterID):
                            del self.__votesByCorpIDByVoteCaseID[corporationID][voteCaseID][characterID]
                elif self.__votesByCorpIDByVoteCaseID[corporationID].has_key(voteCaseID):
                    row = self.__votesByCorpIDByVoteCaseID[corporationID][voteCaseID][characterID]
                    for columnName, oldAndNewValue in change.iteritems():
                        oldValue, newValue = oldAndNewValue
                        setattr(row, columnName, newValue)

        finally:
            uthread.new(self.OnCorporationVoteChanged_thread, corporationID, voteCaseID, characterID, change).context = 'svc.corp.OnCorporationVoteChanged'

    def OnCorporationVoteChanged_thread(self, corporationID, voteCaseID, characterID, change):
        sm.GetService('corpui').OnCorporationVoteChanged(corporationID, voteCaseID, characterID, change)

    def OnShareChange(self, shareholderID, corporationID, change):
        if shareholderID == eve.session.charid:
            self.CanViewVotes_ = None

    def CanViewVotes(self, corpid, new = 0):
        bCan = 0
        if eve.session.corpid == corpid:
            if eve.session.corprole & const.corpRoleDirector == const.corpRoleDirector:
                return 1
            if util.IsNPC(eve.session.corpid):
                return 0
            if self.CanViewVotes_ is None or new:
                self.CanViewVotes_ = (corpid, self.GetCorpRegistry().CanViewVotes(corpid))
            elif self.CanViewVotes_[0] != corpid:
                self.CanViewVotes_ = (corpid, self.GetCorpRegistry().CanViewVotes(corpid))
            bCan = self.CanViewVotes_[1]
        else:
            bCan = self.GetCorpRegistry().CanViewVotes(corpid)
        return bCan

    def CanVote(self, corpID):
        bCan = 0
        shares = self.corp__shares.GetSharesByShareholder()
        if len(shares) and shares.has_key(corpID):
            bCan = 1
        if bCan == 0:
            if self.corp__corporations.GetCorporation().ceoID == eve.session.charid:
                if eve.session.corpid == corpID:
                    bCan = 1
                else:
                    shares = self.corp__shares.GetSharesByShareholder(1)
                    if len(shares) and shares.has_key(corpID):
                        bCan = 1
        return bCan