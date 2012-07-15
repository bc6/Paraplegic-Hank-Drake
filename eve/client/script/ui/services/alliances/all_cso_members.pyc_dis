#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/alliances/all_cso_members.py
import util
import allianceObject
import blue

class AllianceMembersO(allianceObject.base):
    __guid__ = 'allianceObject.members'

    def __init__(self, boundObject):
        allianceObject.base.__init__(self, boundObject)
        self.members = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'allianceid' in change:
            self.members = None

    def GetMembers(self):
        if self.members is None:
            self.members = self.GetMoniker().GetMembers()
        return self.members

    def DeclareExecutorSupport(self, corpID):
        current = self.base__alliance.GetAlliance()
        if current.dictatorial and corpID != current.executorCorpID:
            raise UserError('CanNotChooseExecutorAsDictatorial')
        self.GetMoniker().DeclareExecutorSupport(corpID)

    def DeleteMember(self, corpID):
        self.GetMoniker().DeleteMember(corpID)

    def OnAllianceMemberChanged(self, allianceID, corpID, change):
        if allianceID != eve.session.allianceid:
            return
        bAdd, bRemove = self.GetAddRemoveFromChange(change)
        if self.members is not None:
            if bAdd:
                if len(change) != len(self.members.columns):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return
                line = []
                for columnName in self.members.columns:
                    line.append(change[columnName][1])

                self.members[corpID] = blue.DBRow(self.members.header, line)
            else:
                if not self.members.has_key(corpID):
                    return
                if bRemove:
                    del self.members[corpID]
                else:
                    member = self.members[corpID]
                    for columnName in change.iterkeys():
                        setattr(member, columnName, change[columnName][1])

        sm.GetService('corpui').OnAllianceMemberChanged(allianceID, corpID, change)

    def ResetMembers(self):
        self.members = None