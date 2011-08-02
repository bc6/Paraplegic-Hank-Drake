import util
import allianceObject
import blue

class AllianceApplicationsO(allianceObject.base):
    __guid__ = 'allianceObject.applications'

    def __init__(self, boundObject):
        allianceObject.base.__init__(self, boundObject)
        self.applications = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'allianceid' in change:
            self.applications = None



    def GetApplications(self, showRejected = False):
        if self.applications is None:
            self.applications = self.GetMoniker().GetApplications()
        if showRejected:
            return self.applications
        ret = {}
        for corpID in self.applications:
            app = self.applications[corpID]
            if app.state != const.allianceApplicationRejected:
                ret[corpID] = app

        return ret



    def UpdateApplication(self, corpID, applicationText, state):
        return self.GetMoniker().UpdateApplication(corpID, applicationText, state)



    def OnAllianceApplicationChanged(self, allianceID, corpID, change):
        if allianceID != eve.session.allianceid:
            return 
        (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
        if self.applications is not None:
            if bAdd:
                if len(change) != len(self.applications.header):
                    self.LogWarn('IncorrectNumberOfColumns ignoring change as Add change:', change)
                    return 
                line = []
                for columnName in self.applications.header:
                    line.append(change[columnName][1])

                self.applications[corpID] = line
            elif not self.applications.has_key(corpID):
                return 
            if bRemove:
                del self.applications[corpID]
            else:
                application = self.applications[corpID]
                for columnName in application.header:
                    if not change.has_key(columnName):
                        continue
                    setattr(application, columnName, change[columnName][1])

        sm.GetService('corpui').OnAllianceApplicationChanged(allianceID, corpID, change)




