#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/corporation/bco_sanctionedActions.py
import util
import corpObject
import blue
import uthread
import copy

class SanctionedActionsO(corpObject.base):
    __guid__ = 'corpObject.sanctionedActions'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.__sanctionedActionsByCorpID = {}
        self.__sanctionedActionsByCorpID[0] = {}
        self.__sanctionedActionsByCorpID[1] = {}
        self.__sanctionedActionsByCorpID[2] = {}

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.__sanctionedActionsByCorpID = {}
            self.__sanctionedActionsByCorpID[0] = {}
            self.__sanctionedActionsByCorpID[1] = {}
            self.__sanctionedActionsByCorpID[2] = {}

    def GetSanctionedActionsByCorporation(self, corporationID, state):
        if corporationID not in self.__sanctionedActionsByCorpID[state]:
            rowset = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corporationID, state)
            self.__sanctionedActionsByCorpID[state][corporationID] = rowset.Index('voteCaseID')
        return self.__sanctionedActionsByCorpID[state][corporationID]

    def UpdateSanctionedAction(self, voteCaseID, inEffect, reason = ''):
        return self.GetCorpRegistry().UpdateSanctionedAction(voteCaseID, inEffect, reason)

    def OnSanctionedActionChanged(self, corpID, voteCaseID, change):
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if bAdd:
            if change.has_key('inEffect'):
                inEffect = change['inEffect'][1]
                state = inEffect
                if inEffect == 0:
                    if change.has_key('expires'):
                        if change['expires'][1] > blue.os.GetWallclockTime():
                            state = 2
                if corpID not in self.__sanctionedActionsByCorpID[state]:
                    rowset = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corpID, state)
                    self.__sanctionedActionsByCorpID[state][corpID] = rowset.Index('voteCaseID')
                    line = []
                    for columnName in rowset.columns:
                        line.append(change[columnName][1])

                    self.__sanctionedActionsByCorpID[state][corpID][voteCaseID] = blue.DBRow(self.__sanctionedActionsByCorpID[state][corpID].header, line)
                else:
                    line = []
                    for columnName in self.__sanctionedActionsByCorpID[state][corpID].columns:
                        line.append(change[columnName][1])

                    self.__sanctionedActionsByCorpID[state][corpID][voteCaseID] = blue.DBRow(self.__sanctionedActionsByCorpID[state][corpID].header, line)
        elif bRemove:
            if self.__sanctionedActionsByCorpID[1].has_key(corpID):
                if self.__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                    del self.__sanctionedActionsByCorpID[1][corpID][voteCaseID]
            elif self.__sanctionedActionsByCorpID[2].has_key(corpID):
                if self.__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                    del self.__sanctionedActionsByCorpID[2][corpID][voteCaseID]
            elif self.__sanctionedActionsByCorpID[0].has_key(corpID):
                if self.__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                    del self.__sanctionedActionsByCorpID[0][corpID][voteCaseID]
        elif change.has_key('inEffect'):
            oldRow = None
            oldEffect, newEffect = change['inEffect']
            if oldEffect == 0:
                if self.__sanctionedActionsByCorpID[2].has_key(corpID):
                    if self.__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                        oldRow = copy.deepcopy(self.__sanctionedActionsByCorpID[2][corpID][voteCaseID])
                        del self.__sanctionedActionsByCorpID[2][corpID][voteCaseID]
                elif self.__sanctionedActionsByCorpID[0].has_key(corpID):
                    if self.__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                        oldRow = copy.deepcopy(self.__sanctionedActionsByCorpID[0][corpID][voteCaseID])
                        del self.__sanctionedActionsByCorpID[0][corpID][voteCaseID]
            else:
                if self.__sanctionedActionsByCorpID[1].has_key(corpID):
                    if self.__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                        oldRow = copy.deepcopy(self.__sanctionedActionsByCorpID[1][corpID][voteCaseID])
                        del self.__sanctionedActionsByCorpID[1][corpID][voteCaseID]
                newEffect = 0
            if oldRow is None:
                oldRow = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corpID, newEffect).Index('voteCaseID')[voteCaseID]
            if corpID not in self.__sanctionedActionsByCorpID[newEffect]:
                self.__sanctionedActionsByCorpID[newEffect][corpID] = dbutil.CIndexedRowset(oldRow.header, 'voteCaseID')
            self.__sanctionedActionsByCorpID[newEffect][corpID][voteCaseID] = oldRow
            row = self.__sanctionedActionsByCorpID[newEffect][corpID][voteCaseID]
            for columnName, oldAndNewValue in change.iteritems():
                oldValue, newValue = oldAndNewValue
                setattr(row, columnName, newValue)

        else:
            row = None
            if self.__sanctionedActionsByCorpID[1].has_key(corpID):
                if self.__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                    row = self.__sanctionedActionsByCorpID[1][corpID][voteCaseID]
            elif self.__sanctionedActionsByCorpID[2].has_key(corpID):
                if self.__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                    row = self.__sanctionedActionsByCorpID[2][corpID][voteCaseID]
            elif self.__sanctionedActionsByCorpID[0].has_key(corpID):
                if self.__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                    row = self.__sanctionedActionsByCorpID[0][corpID][voteCaseID]
            if row:
                for columnName, oldAndNewValue in change.iteritems():
                    oldValue, newValue = oldAndNewValue
                    setattr(row, columnName, newValue)

        uthread.new(self.OnSanctionedActionChanged_thread, corpID, voteCaseID, change).context = 'svc.corp.OnSanctionedActionChanged'

    def OnSanctionedActionChanged_thread(self, corpID, voteCaseID, change):
        sm.GetService('corpui').OnSanctionedActionChanged(corpID, voteCaseID, change)