#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/certificateSvc.py
import service
import blue
import uthread
import util
import types
import form
import localization
import uix

class Certificates(service.Service):
    __exportedcalls__ = {'GrantCertificate': [],
     'UpdateCertificateVisibilityFlags': [],
     'GetMyCertificates': [],
     'HaveCertificate': [],
     'GetParentSkills': [],
     'GetParentCertificates': [],
     'GetChildCertificates': [],
     'OpenCertificateWindow': [service.ROLE_IGB | service.ROLE_PLAYER],
     'FindCertificateWindow': [],
     'GetCategories': [],
     'GetGrades': [],
     'HasPrerequisites': [],
     'GetCertificatesByCharacter': [],
     'GetHighestLevelOfClass': [],
     'GrantAllCertificates': [],
     'GetCertificateRecommendationsFromCertificateID': []}
    __notifyevents__ = []
    __guid__ = 'svc.certificates'
    __servicename__ = 'certificates'
    __displayname__ = 'Certificate Service'
    __startupdependencies__ = ['settings']

    def __init__(self):
        service.Service.__init__(self)
        self.myCertificates = None
        self.prerequisites = {}
        self.children = {}
        self.certificatesByClass = None

    def Run(self, memStream = None):
        self.LoadRelationshipData()

    def LoadRelationshipData(self):
        self.prerequisites = {}
        self.children = {}
        for relationshipKey in cfg.certificaterelationships:
            relationship = cfg.certificaterelationships.Get(relationshipKey)
            parentID = relationship.parentID
            childID = relationship.childID
            parentTypeID = relationship.parentTypeID
            if childID not in self.prerequisites:
                self.prerequisites[childID] = util.KeyVal(skills=[], certificates=[])
            if parentID > 0:
                if parentID not in self.children:
                    self.children[parentID] = []
                self.children[parentID].append(childID)
                self.prerequisites[childID].certificates.append(parentID)
            else:
                self.prerequisites[childID].skills.append((parentTypeID, relationship.parentLevel))

    def HasPrerequisiteSkills(self, certificateID):
        if certificateID not in self.prerequisites:
            self.LogWarn('Certificate with ID', certificateID, 'has no prerequisites')
            return True
        prereqSkills = self.prerequisites[certificateID].skills
        mySkills = sm.StartService('skills').MySkills()
        for typeID, level in prereqSkills:
            requirementPassed = False
            for skill in mySkills:
                if skill.typeID == typeID:
                    if skill.skillLevel >= level:
                        requirementPassed = True
                    break

            if not requirementPassed:
                return False

        return True

    def HasPrerequisiteCertificates(self, certificateID):
        if certificateID not in self.prerequisites:
            return True
        if self.myCertificates is None:
            self.GetMyCertificates()
        prereqCertificates = self.prerequisites[certificateID].certificates
        for requiredCertificateID in prereqCertificates:
            if requiredCertificateID not in self.myCertificates:
                return False

        return True

    def HasPrerequisites(self, certificateID):
        if not self.HasPrerequisiteCertificates(certificateID):
            return False
        if not self.HasPrerequisiteSkills(certificateID):
            return False
        return True

    def GrantCertificate(self, certificateID):
        if self.HaveCertificate(certificateID):
            raise UserError('CertificateAlreadyGranted')
        if not self.HasPrerequisiteSkills(certificateID):
            raise UserError('CertificateSkillPrerequisitesNotMet')
        if not self.HasPrerequisiteCertificates(certificateID):
            raise UserError('CertificateCertPrerequisitesNotMet')
        sm.RemoteSvc('certificateMgr').GrantCertificate(certificateID)
        self.myCertificates[certificateID] = util.KeyVal(grantDate=blue.os.GetWallclockTime(), visibilityFlags=0)
        sm.ScatterEvent('OnCertificateIssued', certificateID)

    def UpdateCertificateVisibilityFlags(self, certificateID, visibilityFlags):
        if not self.HaveCertificate(certificateID):
            raise UserError('CertificateNotOwned')
        currentVisFlags = self.myCertificates[certificateID][CERT_VISIBILITY_FLAGS]
        if visibilityFlags == currentVisibilityFlags:
            return
        sm.RemoteSvc('certificateMgr').UpdateCertificateFlags(certificateID, visibilityFlags)
        self.myCertificates[certificateID].visibilityFlags = visibilityFlags

    def GetMyCertificates(self, forceUpdate = False):
        if self.myCertificates is None or forceUpdate:
            self.myCertificates = {}
            certs = sm.RemoteSvc('certificateMgr').GetMyCertificates()
            for cert in certs:
                self.myCertificates[cert.certificateID] = util.KeyVal(grantDate=cert.grantDate, visibilityFlags=cert.visibilityFlags)

        return self.myCertificates

    def HaveCertificate(self, certificateID):
        return certificateID in self.GetMyCertificates()

    def GetParentSkills(self, certificateID):
        if certificateID not in self.prerequisites:
            return []
        return self.prerequisites[certificateID].skills

    def GetParentCertificates(self, certificateID):
        if certificateID not in self.prerequisites:
            return []
        return self.prerequisites[certificateID].certificates

    def GetChildCertificates(self, certificateID):
        if certificateID not in self.children:
            return []
        return self.children[certificateID]

    def OpenCertificateWindow(self, certID = None):
        if not certID:
            certID = settings.user.ui.Get('cert_lastViewed', 1)
        wnd = form.certificateWindow.GetIfOpen()
        if not wnd:
            sm.GetService('tutorial').OpenTutorialSequence_Check(uix.tutorialCertificates)
            wnd = form.certificateWindow.Open(certID=int(certID))
        else:
            wnd.Maximize()
            wnd.LoadTree(int(certID))

    def FindCertificateWindow(self):
        return form.certificateWindow.GetIfOpen()

    def GetCategories(self, certificates):
        categories = {}
        for key, value in certificates.iteritems():
            cat = value.categoryID
            currentValue = categories.get(cat, [])
            currentValue.append(value)
            categories[cat] = currentValue

        return categories

    def GetGrades(self, certificateList):
        grades = {}
        for value in certificateList:
            valueGrade = value.grade
            currentValue = grades.get(valueGrade, [])
            currentValue.append(value)
            grades[valueGrade] = currentValue

        return grades

    def GetAllShipCertificateRecommendations(self):
        return sm.RemoteSvc('certificateMgr').GetAllShipCertificateRecommendations()

    def GetCertificateRecommendationsByShipTypeID(self, typeID):
        all = self.GetAllShipCertificateRecommendations().Filter('shipTypeID')
        shipRec = all.get(typeID, [])
        return shipRec

    def GetCertificatesByCharacter(self, charID):
        return sm.RemoteSvc('certificateMgr').GetCertificatesByCharacter(charID)

    def GetCertificateRecommendationsFromCertificateID(self, certificateID):
        all = self.GetAllShipCertificateRecommendations().Filter('certificateID')
        certRec = all.get(certificateID, [])
        return certRec

    def GetHighestLevelOfClass(self, items, *args):
        highestLevels = {}
        for each in items:
            if not each:
                continue
            currentHighest = highestLevels.get(each.classID, None)
            if currentHighest is None:
                highestLevels[each.classID] = (each.grade, each)
            else:
                currentLevel, currentInfo = currentHighest
                if currentLevel < each.grade:
                    highestLevels[each.classID] = (each.grade, each)

        highestLevelsList = []
        for key, value in highestLevels.iteritems():
            grade, certInfo = value
            highestLevelsList.append(certInfo)

        return highestLevelsList

    def GetCertificatesByClass(self):
        if self.certificatesByClass is not None:
            return self.certificatesByClass
        certs = {}
        for cert in cfg.certificates:
            if cert.classID not in certs:
                certs[cert.classID] = []
            certs[cert.classID].append(cert)

        self.certificatesByClass = certs
        return self.certificatesByClass

    def ChangeVisibilityFlag(self, visibilityChanged):
        if visibilityChanged is None or len(visibilityChanged) < 1:
            return
        updateDict = {}
        certsByClass = self.GetCertificatesByClass()
        for certID in visibilityChanged:
            certObj = cfg.certificates.Get(certID)
            sameClassCerts = certsByClass.get(certObj.classID, None)
            for similarCert in sameClassCerts:
                similarCertID = similarCert.certificateID
                if similarCertID == certID:
                    continue
                if similarCertID in self.myCertificates:
                    if similarCertID in visibilityChanged:
                        continue
                    certData = self.myCertificates[similarCertID]
                    if certData.visibilityFlags != visibilityChanged[certID]:
                        updateDict[similarCertID] = visibilityChanged[certID]

            updateDict[certID] = visibilityChanged[certID]

        sm.RemoteSvc('certificateMgr').BatchCertificateUpdate(updateDict)
        for certID in updateDict:
            self.myCertificates[certID].visibilityFlags = updateDict[certID]

    def IsInProgress(self, certID):
        preSkills = sm.StartService('certificates').GetParentSkills(certID)
        preCerts = sm.StartService('certificates').GetParentCertificates(certID)
        for each in preSkills:
            skillID, level = each
            skillStatus = self.SkillStatus(skillID, level)
            if skillStatus.status == 2:
                return True

        for cert in preCerts:
            if sm.StartService('certificates').HaveCertificate(cert):
                return True

        return False

    def SkillStatus(self, skillID, level):
        mine = sm.StartService('skills').MySkillLevelsByID()
        skill = util.KeyVal()
        if skillID not in mine:
            skill.status = 0
            skill.current = None
        elif mine[skillID] < level:
            skill.status = 1
            skill.current = mine[skillID]
        else:
            skill.status = 2
            skill.current = mine[skillID]
        return skill

    def GrantAllCertificates(self, certificates):
        issued = sm.RemoteSvc('certificateMgr').BatchCertificateGrant(certificates)
        if not issued:
            return
        for certificateID in issued:
            self.myCertificates[certificateID] = util.KeyVal(grantDate=blue.os.GetWallclockTime(), visibilityFlags=0)

        sm.ScatterEvent('OnCertificateIssued')

    def FindAvailableCerts(self, showProgress = 0):
        self.LogInfo('Finding available certificates...')
        startTime = blue.os.GetWallclockTime()
        readyDict = {}
        childrenDict = {}
        for cert in cfg.certificates:
            certID = cert.certificateID
            blue.pyos.BeNice()
            if not self.HaveCertificate(certID) and self.HasPrerequisites(certID):
                readyDict[certID] = 1
                for child in self.GetChildCertificates(certID):
                    childrenDict[child] = 1

        if showProgress:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/Certificates/LoadingWindow/LoadingTitle'), localization.GetByLabel('UI/Certificates/LoadingWindow/LoadingText'), 2, 4)
        somethingFound = 1
        while somethingFound:
            blue.pyos.BeNice()
            somethingFound = 0
            childrenDictCopy = childrenDict.copy()
            for certID in childrenDictCopy.iterkeys():
                blue.pyos.BeNice()
                if self.MetWithReadyDict(certID, readyDict):
                    readyDict[certID] = 1
                    childrenDict.pop(certID)
                    for child in self.GetChildCertificates(certID):
                        blue.pyos.BeNice()
                        childrenDict[child] = 1
                        somethingFound = 1

        diff = (blue.os.GetWallclockTime() - startTime) / float(SEC)
        self.LogInfo('Done finding available certificates. Found', len(readyDict), 'certificates in', diff, 'seconds')
        return readyDict

    def MetWithReadyDict(self, certID, readyDict):
        preSkills = self.GetParentSkills(certID)
        preCerts = self.GetParentCertificates(certID)
        for each in preSkills:
            skillID, level = each
            skillStatus = self.SkillStatus(skillID, level)
            if skillStatus.status != 2:
                return False

        for cert in preCerts:
            if not self.HaveCertificate(cert):
                if cert not in readyDict:
                    return False

        return True

    def GetCertificateLabel(self, certificateID):
        classes = sm.RemoteSvc('certificateMgr').GetCertificateClasses()
        data = cfg.certificates.Get(certificateID)
        label = cfg.invtypes.Get(const.typeCertificate).name
        desc = cfg.invtypes.Get(const.typeCertificate).description
        grade = localization.GetByLabel('UI/Certificates/CertificateGrades/Grade1')
        if data:
            classdata = classes[data.classID]
            if classdata:
                label = localization.GetByMessageID(classdata.classNameID)
            gradeDict = {1: 'UI/Certificates/CertificateGrades/Grade1',
             2: 'UI/Certificates/CertificateGrades/Grade2',
             3: 'UI/Certificates/CertificateGrades/Grade3',
             4: 'UI/Certificates/CertificateGrades/Grade4',
             5: 'UI/Certificates/CertificateGrades/Grade5'}
            gradePath = gradeDict.get(data.grade)
            grade = localization.GetByLabel(gradePath)
            desc = data.description
        return (label, grade, desc)