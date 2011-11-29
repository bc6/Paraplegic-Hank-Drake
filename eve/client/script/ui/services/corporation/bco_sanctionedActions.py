import util
import corpObject
import blue
import uthread
import copy

class SanctionedActionsO(corpObject.base):
    __guid__ = 'corpObject.sanctionedActions'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self._SanctionedActionsO__sanctionedActionsByCorpID = {}
        self._SanctionedActionsO__sanctionedActionsByCorpID[0] = {}
        self._SanctionedActionsO__sanctionedActionsByCorpID[1] = {}
        self._SanctionedActionsO__sanctionedActionsByCorpID[2] = {}
        self._SanctionedActionsO__sanctionedActionsRowsetHeader = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self._SanctionedActionsO__sanctionedActionsByCorpID = {}
            self._SanctionedActionsO__sanctionedActionsByCorpID[0] = {}
            self._SanctionedActionsO__sanctionedActionsByCorpID[1] = {}
            self._SanctionedActionsO__sanctionedActionsByCorpID[2] = {}
            self._SanctionedActionsO__sanctionedActionsRowsetHeader = None



    def GetSanctionedActionsByCorporation(self, corporationID, state):
        if not self._SanctionedActionsO__sanctionedActionsByCorpID[state].has_key(corporationID):
            rowset = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corporationID, state)
            self._SanctionedActionsO__sanctionedActionsByCorpID[state][corporationID] = util.IndexRowset(rowset.header, rowset.lines, 'voteCaseID')
            self._SanctionedActionsO__sanctionedActionsRowsetHeader = rowset.header
        return self._SanctionedActionsO__sanctionedActionsByCorpID[state][corporationID]



    def UpdateSanctionedAction(self, voteCaseID, inEffect, reason = ''):
        return self.GetCorpRegistry().UpdateSanctionedAction(voteCaseID, inEffect, reason)



    def OnSanctionedActionChanged(self, corpID, voteCaseID, change):
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        if bAdd:
            if change.has_key('inEffect'):
                inEffect = change['inEffect'][1]
                state = inEffect
                if inEffect == 0:
                    if change.has_key('expires'):
                        if change['expires'][1] > blue.os.GetWallclockTime():
                            state = 2
                if not self._SanctionedActionsO__sanctionedActionsByCorpID[state].has_key(corpID):
                    header = self._SanctionedActionsO__sanctionedActionsRowsetHeader
                    if not header:
                        rowset = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corpID, state)
                        self._SanctionedActionsO__sanctionedActionsByCorpID[state][corpID] = util.IndexRowset(rowset.header, rowset.lines, 'voteCaseID')
                        self._SanctionedActionsO__sanctionedActionsRowsetHeader = rowset.header
                    else:
                        self._SanctionedActionsO__sanctionedActionsByCorpID[state][corpID] = util.IndexRowset(rowset.header, None, 'voteCaseID')
                        line = []
                        for columnName in header:
                            line.append(change[columnName][1])

                    self._SanctionedActionsO__sanctionedActionsByCorpID[state][corpID][voteCaseID] = line
                else:
                    line = []
                    for columnName in self._SanctionedActionsO__sanctionedActionsRowsetHeader:
                        line.append(change[columnName][1])

                self._SanctionedActionsO__sanctionedActionsByCorpID[state][corpID][voteCaseID] = line
        elif bRemove:
            if self._SanctionedActionsO__sanctionedActionsByCorpID[1].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                    del self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID][voteCaseID]
            elif self._SanctionedActionsO__sanctionedActionsByCorpID[2].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                    del self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID][voteCaseID]
            elif self._SanctionedActionsO__sanctionedActionsByCorpID[0].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                    del self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID][voteCaseID]
        elif change.has_key('inEffect'):
            oldRow = None
            (oldEffect, newEffect,) = change['inEffect']
            if oldEffect == 0:
                if self._SanctionedActionsO__sanctionedActionsByCorpID[2].has_key(corpID):
                    if self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                        oldRow = copy.deepcopy(self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID][voteCaseID])
                        oldRow.header = self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID][voteCaseID].header
                        del self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID][voteCaseID]
                elif self._SanctionedActionsO__sanctionedActionsByCorpID[0].has_key(corpID):
                    if self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                        oldRow = copy.deepcopy(self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID][voteCaseID])
                        oldRow.header = self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID][voteCaseID].header
                        del self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID][voteCaseID]
            elif self._SanctionedActionsO__sanctionedActionsByCorpID[1].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                    oldRow = copy.deepcopy(self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID][voteCaseID])
                    oldRow.header = self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID][voteCaseID].header
                    del self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID][voteCaseID]
            newEffect = 0
            if oldRow is None:
                oldRow = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corpID, newEffect).Index('voteCaseID')[voteCaseID]
                if not self._SanctionedActionsO__sanctionedActionsRowsetHeader:
                    self._SanctionedActionsO__sanctionedActionsRowsetHeader = oldRow.header
            if not self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect].has_key(corpID):
                if not self._SanctionedActionsO__sanctionedActionsRowsetHeader:
                    rowset = self.GetCorpRegistry().GetSanctionedActionsByCorporation(corpID, newEffect)
                    self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect][corpID] = util.IndexRowset(rowset.header, rowset.lines, 'voteCaseID')
                    self._SanctionedActionsO__sanctionedActionsRowsetHeader = rowset.header
                else:
                    self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect][corpID] = util.IndexRowset(self._SanctionedActionsO__sanctionedActionsRowsetHeader, None, 'voteCaseID')
                    self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect][corpID][voteCaseID] = oldRow
            else:
                self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect][corpID][voteCaseID] = oldRow
            row = self._SanctionedActionsO__sanctionedActionsByCorpID[newEffect][corpID][voteCaseID]
            for (columnName, oldAndNewValue,) in change.iteritems():
                (oldValue, newValue,) = oldAndNewValue
                setattr(row, columnName, newValue)

        else:
            row = None
            if self._SanctionedActionsO__sanctionedActionsByCorpID[1].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID].has_key(voteCaseID):
                    row = self._SanctionedActionsO__sanctionedActionsByCorpID[1][corpID][voteCaseID]
            elif self._SanctionedActionsO__sanctionedActionsByCorpID[2].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID].has_key(voteCaseID):
                    row = self._SanctionedActionsO__sanctionedActionsByCorpID[2][corpID][voteCaseID]
            elif self._SanctionedActionsO__sanctionedActionsByCorpID[0].has_key(corpID):
                if self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID].has_key(voteCaseID):
                    row = self._SanctionedActionsO__sanctionedActionsByCorpID[0][corpID][voteCaseID]
            if row:
                for (columnName, oldAndNewValue,) in change.iteritems():
                    (oldValue, newValue,) = oldAndNewValue
                    setattr(row, columnName, newValue)

        uthread.new(self.OnSanctionedActionChanged_thread, corpID, voteCaseID, change).context = 'svc.corp.OnSanctionedActionChanged'



    def OnSanctionedActionChanged_thread(self, corpID, voteCaseID, change):
        sm.GetService('corpui').OnSanctionedActionChanged(corpID, voteCaseID, change)




