import util
import corpObject
import blue

class CorpAllianceO(corpObject.base):
    __guid__ = 'corpObject.alliance'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self._CorpAllianceO__applicationsByAllianceID = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self._CorpAllianceO__applicationsByAllianceID = None



    def GetSuggestedAllianceShortNames(self, allianceName):
        return self.GetCorpRegistry().GetSuggestedAllianceShortNames(allianceName)



    def CreateAlliance(self, allianceName, shortName, description, url):
        return self.GetCorpRegistry().CreateAlliance(allianceName, shortName, description, url)



    def ApplyToJoinAlliance(self, allianceID, applicationText):
        if self.GetAllianceApplications().has_key(allianceID):
            raise UserError('CantApplyTwiceToAlliance')
        return self.GetCorpRegistry().ApplyToJoinAlliance(allianceID, applicationText)



    def GetAllianceApplications(self):
        if self._CorpAllianceO__applicationsByAllianceID is None:
            self._CorpAllianceO__applicationsByAllianceID = self.GetCorpRegistry().GetAllianceApplications()
        return self._CorpAllianceO__applicationsByAllianceID



    def DeleteAllianceApplication(self, allianceID):
        return self.GetCorpRegistry().DeleteAllianceApplication(allianceID)



    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        try:
            if corpID == eve.session.corpid:
                (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
                if self._CorpAllianceO__applicationsByAllianceID is not None:
                    if bAdd:
                        if len(change) != len(self._CorpAllianceO__applicationsByAllianceID.header):
                            self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                            return 
                        line = []
                        for columnName in self._CorpAllianceO__applicationsByAllianceID.header:
                            line.append(change[columnName][1])

                        self._CorpAllianceO__applicationsByAllianceID[allianceID] = line
                    elif not self._CorpAllianceO__applicationsByAllianceID.has_key(allianceID):
                        return 
                    if bRemove:
                        del self._CorpAllianceO__applicationsByAllianceID[allianceID]
                    else:
                        application = self._CorpAllianceO__applicationsByAllianceID[allianceID]
                        for columnName in application.header:
                            if not change.has_key(columnName):
                                continue
                            setattr(application, columnName, change[columnName][1])


        finally:
            sm.GetService('corpui').OnAllianceApplicationChanged(allianceID, corpID, change)





