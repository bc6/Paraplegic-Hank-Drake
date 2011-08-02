import util
import allianceObject
import blue

class AllianceRelationshipsO(allianceObject.base):
    __guid__ = 'allianceObject.relationships'

    def __init__(self, boundObject):
        allianceObject.base.__init__(self, boundObject)
        self.relationships = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'allianceid' in change:
            self.relationships = None



    def Get(self):
        if self.relationships is None:
            self.relationships = self.GetMoniker().GetRelationships()
        return self.relationships



    def Set(self, relationship, toID):
        relationships = self.Get()
        if relationships.has_key(toID):
            if relationships[toID] == relationship:
                return 
        self.GetMoniker().SetRelationship(relationship, toID)



    def Delete(self, toID):
        relationships = self.Get()
        if not relationships.has_key(toID):
            return 
        return self.GetMoniker().DeleteRelationship(toID)



    def OnAllianceRelationshipChanged(self, allianceID, toID, change):
        if allianceID != eve.session.allianceid:
            return 
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        if self.relationships is not None:
            if bAdd:
                if len(change) != len(self.relationships.header):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return 
                line = []
                for columnName in self.relationships.header:
                    line.append(change[columnName][1])

                self.relationships[toID] = line
            elif not self.relationships.has_key(toID):
                return 
            if bRemove:
                del self.relationships[toID]
            else:
                member = self.relationships[toID]
                for columnName in member.header:
                    if not change.has_key(columnName):
                        continue
                    setattr(member, columnName, change[columnName][1])

        sm.GetService('corpui').OnAllianceRelationshipChanged(allianceID, toID, change)




