import util
import corpObject

class ApplicationsO(corpObject.base):
    __guid__ = 'corpObject.applications'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.corpApplications = None
        self.myApplications = None



    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change:
            self.myApplications = None
        if 'corpid' in change:
            self.corpApplications = None



    def Reset(self):
        self.corpApplications = None
        self.myApplications = None



    def OnCorporationApplicationChanged(self, applicantID, corporationID, change):
        applications = [self.corpApplications, self.myApplications][(applicantID == eve.session.charid)]
        if applications is not None:
            (bAdd, bRemove,) = self.GetAddRemoveFromChange(change)
            key = (corporationID, applicantID)
            if bAdd:
                header = None
                for example in applications.itervalues():
                    header = example.header
                    break

                if header is None:
                    header = change.keys()
                line = []
                for columnName in header:
                    line.append(change[columnName][1])

                application = util.Row(header, line)
                applications[key] = application
            elif bRemove:
                if applications.has_key(key):
                    del applications[key]
            elif applications.has_key(key):
                application = applications[key]
                for columnName in change.iterkeys():
                    setattr(application, columnName, change[columnName][1])

                applications[key] = application
        sm.GetService('corpui').OnCorporationApplicationChanged(applicantID, corporationID, change)



    def GetMyApplications(self, corporationID = -1, forceUpdate = False):
        if self.myApplications is None or forceUpdate:
            self.myApplications = {}
            applications = self.GetCorpRegistry().GetMyApplications()
            for application in applications:
                key = (application.corporationID, application.characterID)
                self.myApplications[key] = application

        if corporationID != -1:
            key = (corporationID, eve.session.charid)
            if self.myApplications.has_key(key):
                return self.myApplications[key]
        else:
            res = []
            for application in self.myApplications.itervalues():
                if res == []:
                    res = util.Rowset(application.header)
                res.lines.append(application.line)

            return res
        return []



    def GetMyApplicationsWithStatus(self, status):
        applications = self.GetMyApplications()
        if 0 == len(applications):
            return applications
        res = util.Rowset(applications.header)
        for application in applications:
            if application.status == status:
                res.lines.append(application.line)

        return res



    def GetApplications(self, characterID = -1, forceUpdate = False):
        if eve.session.corprole & const.corpRolePersonnelManager != const.corpRolePersonnelManager:
            return []
        else:
            if self.corpApplications is None or forceUpdate:
                self.corpApplications = {}
                applications = self.GetCorpRegistry().GetApplications()
                for application in applications.itervalues():
                    key = (application.corporationID, application.characterID)
                    self.corpApplications[key] = application

            if characterID == -1:
                res = []
                for application in self.corpApplications.itervalues():
                    if res == []:
                        res = util.Rowset(application.header)
                    res.lines.append(application.line)

                return res
            key = (eve.session.corpid, characterID)
            if self.corpApplications.has_key(key):
                return self.corpApplications[key]
            return []



    def GetApplicationsWithStatus(self, status):
        applications = self.GetApplications()
        if 0 == len(applications):
            return applications
        res = util.Rowset(applications.header)
        for application in applications:
            if application.status == status:
                res.lines.append(application.line)

        return res



    def DeleteApplication(self, corporationID, characterID):
        if not (eve.session.charid == characterID or eve.session.corpid == corporationID and eve.session.corprole & const.corpRolePersonnelManager == const.corpRolePersonnelManager):
            return []
        self.GetCorpRegistry().DeleteApplication(corporationID, characterID)
        key = (corporationID, characterID)
        for applications in (self.corpApplications, self.myApplications):
            if applications is not None and applications.has_key(key):
                change = {}
                row = applications[key]
                for columnName in row.header:
                    oldVal = getattr(row, columnName)
                    change[columnName] = (oldVal, None)

                del applications[key]
                self.LogInfo('bco_applications::DeleteApplication sending fake notification')
                sm.GetService('corpui').OnCorporationApplicationChanged(characterID, corporationID, change)




    def InsertApplication(self, corporationID, applicationText):
        return self.GetCorpRegistry().InsertApplication(corporationID, applicationText)



    def UpdateApplicationOffer(self, characterID, applicationText, status, applicationDateTime = None):
        return self.GetCorpRegistry().UpdateApplicationOffer(characterID, applicationText, status, applicationDateTime)




