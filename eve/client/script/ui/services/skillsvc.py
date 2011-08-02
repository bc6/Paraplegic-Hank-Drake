import blue
import service
import uiutil
import sys
import uthread
import util
import xtriui
import skillUtil
import uiconst

class SkillsSvc(service.Service):
    __guid__ = 'svc.skills'
    __exportedcalls__ = {'SkillInTraining': [],
     'HasSkill': [],
     'MySkills': [],
     'MySkillLevelsByID': [],
     'GetSkillPoints': [],
     'GetSkillGroups': [],
     'GetSkillCount': [],
     'GetAllSkills': [],
     'GetSkillHistory': [],
     'GetFreeSkillPoints': [],
     'SetFreeSkillPoints': []}
    __notifyevents__ = ['ProcessSessionChange',
     'OnGodmaSkillStartTraining',
     'OnGodmaSkillTrainingStopped',
     'OnSkillFinished',
     'OnRespecInfoChanged',
     'OnGodmaMultipleSkillsTrained',
     'OnFreeSkillPointsChanged',
     'OnGodmaSkillInjected',
     'OnAdminSkillChange']
    __servicename__ = 'skills'
    __displayname__ = 'Skill Client Service'
    __dependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Skills')
        self.Reset()



    def Stop(self, memStream = None):
        self.Reset()



    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()



    def Reset(self):
        self.myskills = None
        self.mySkillsByTypeID = None
        self.allskills = None
        self.skillHistory = None
        self.respecInfo = None
        self.freeSkillPoints = None



    def SkillInTraining(self, *args):
        inTraining = [ each for each in self.GetMyGodmaItem().skills.itervalues() if each.flagID == const.flagSkillInTraining ]
        if inTraining:
            return inTraining[0]
        else:
            return None



    def OnSkillFinished(self, skillID, skillTypeID = None, skillLevel = None):
        oldNotification = settings.user.ui.Get('skills_showoldnotification', 0)
        try:
            self.skillHistory = None
            skill = sm.GetService('godma').GetItem(skillID)
            self.myskills = None
            if oldNotification == 1:
                eve.Message('SkillTrained', {'name': cfg.invtypes.Get(skill.typeID).name,
                 'lvl': skill.skillLevel})
        except:
            sys.exc_clear()
        if oldNotification == 0:
            eve.Message('skillTrainingFanfare')
            uthread.new(sm.StartService('neocom').ShowSkillNotification, [skill.typeID])



    def OnGodmaMultipleSkillsTrained(self, skillTypeIDs):
        oldNotification = settings.user.ui.Get('skills_showoldnotification', 0)
        if oldNotification == 1:
            if len(skillTypeIDs) == 1:
                skill = self.GetMySkillsFromTypeID(skillTypeIDs[0])
                skillLevel = skill.skillLevel if skill is not None else mls.UI_GENERIC_UNKNOWN
                eve.Message('SkillTrained', {'name': cfg.invtypes.Get(skillTypeIDs[0]).name,
                 'lvl': skillLevel})
            else:
                eve.Message('MultipleSkillsTrainedNotify', {'num': len(skillTypeIDs)})
        else:
            eve.Message('skillTrainingFanfare')
            uthread.new(sm.StartService('neocom').ShowSkillNotification, skillTypeIDs)



    def MySkills(self, renew = 0, byTypeID = False):
        if self.myskills is None or renew:
            self.LogInfo('MySkills::Renewing skill info')
            self.myskills = self.GetMyGodmaItem().skills.values()
            self.mySkillsByTypeID = self.myskills.Index('typeID')
        if byTypeID:
            return self.mySkillsByTypeID
        return self.myskills



    def MySkillLevelsByID(self, renew = 0):
        skills = {}
        for skill in self.MySkills(renew):
            skills[skill.typeID] = skill.skillLevel

        return skills



    def OnGodmaSkillStartTraining(self, typeID = None, *args):
        self.skillHistory = None
        if self.myskills is not None and typeID is not None:
            for skill in self.myskills:
                if skill.typeID == typeID:
                    return 

            self.MySkills(1)



    def OnGodmaSkillTrainingStopped(self, *args):
        self.skillHistory = None
        self.MySkills(1)



    def OnGodmaSkillInjected(self, *args):
        self.MySkills(1)



    def OnAdminSkillChange(self, skillItemID, skillTypeID, newSP):
        self.MySkills(1)



    def HasSkill(self, skillID):
        mine = self.MySkills()
        skills = [ skill for skill in mine if skill.typeID == skillID ]
        if len(skills):
            return skills[0]



    def GetAllSkills(self):
        if not self.allskills:
            self.allskills = [ sm.GetService('godma').GetType(each.typeID) for each in cfg.invtypes if each.categoryID == const.categorySkill if each.published == 1 ]
        return self.allskills



    def GetSkillHistory(self):
        if self.skillHistory is None:
            self.skillHistory = sm.GetService('godma').GetSkillHandler().GetSkillHistory()
        return self.skillHistory



    def GetSkillGroups(self, advanced = False):
        skillgroups = [ g for g in cfg.invgroups if g.categoryID == const.categorySkill if g.groupID not in [const.groupFakeSkills] ]
        skillgroups = uiutil.SortByAttribute(skillgroups, 'groupName')
        skillInTraining = sm.GetService('skills').SkillInTraining()
        ownSkills = [ skill for skill in self.GetMyGodmaItem().skills.values() ] + [skillInTraining]
        allSkills = self.GetAllSkills()
        skillsbygroup = []
        (doneItem, doneType,) = ([], [])
        skillQueue = sm.StartService('skillqueue').GetServerQueue()
        skillsInQueue = [ skillID for (skillID, trainlevel,) in skillQueue ]
        for each in skillgroups:
            tmp = [each,
             [],
             [],
             [],
             []]
            tmpGrpSkl = []
            points = 0
            for skill in ownSkills:
                if not skill or skill.itemID in doneItem:
                    continue
                typeinfo = cfg.invtypes.Get(skill.typeID)
                if typeinfo.groupID == each.groupID:
                    tmp[1].append(skill)
                    doneItem.append(skill.itemID)
                    if skill.typeID not in doneType:
                        doneType.append(skill.typeID)
                    points += skill.skillPoints
                    if skill.flagID == const.flagSkillInTraining:
                        tmp[3].append(skill)
                    if skill.typeID in skillsInQueue:
                        tmp[4].append(skill.typeID)

            if advanced:
                for skill in allSkills:
                    if skill.typeID not in doneType and skill.groupID == each.groupID:
                        tmpGrpSkl.append(skill)

                tmp[2] += tmpGrpSkl
            tmp.append(points)
            skillsbygroup.append(tmp)

        return skillsbygroup



    def GetMySkillsFromTypeID(self, typeID):
        return self.MySkills(byTypeID=True).get(typeID, None)



    def GetMyGodmaItem(self):
        ret = sm.GetService('godma').GetItem(eve.session.charid)
        while ret is None:
            blue.pyos.synchro.Sleep(500)
            ret = sm.GetService('godma').GetItem(eve.session.charid)

        return ret



    def GetSkillCount(self):
        return len(self.GetMyGodmaItem().skills.values())



    def GetSkillPoints(self, groupID = None):
        total = 0
        skills = self.GetMyGodmaItem().skills
        for skillID in skills:
            skill = skills[skillID]
            if groupID is not None:
                typeinfo = cfg.invtypes.Get(skill.typeID)
                if typeinfo.groupID == groupID:
                    total += skill.skillPoints
            else:
                total += skill.skillPoints

        return total



    def Train(self, skillX):
        skill = self.SkillInTraining()
        if skill and eve.Message('ConfirmResetSkillTraining', {'name': skill.type.typeName,
         'lvl': skill.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return 
        sm.GetService('godma').GetSkillHandler().CharStartTrainingSkill(skillX.itemID, skillX.locationID)



    def InjectSkillIntoBrain(self, skillX):
        skillIDList = [ skill.itemID for skill in skillX ]
        if not skillIDList:
            return 
        skillsLocation = skillX[0].locationID
        sm.GetService('godma').GetSkillHandler().InjectSkillIntoBrain(skillIDList, skillsLocation)



    def AbortTrain(self, skillX):
        if eve.Message('ConfirmAbortSkillTraining', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            sm.GetService('godma').GetSkillHandler().CharStopTrainingSkill()



    def GetRespecInfo(self):
        if self.respecInfo is None:
            self.respecInfo = sm.GetService('godma').GetSkillHandler().GetRespecInfo()
        return self.respecInfo



    def OnRespecInfoChanged(self, *args):
        self.respecInfo = None
        sm.ScatterEvent('OnRespecInfoUpdated')



    def OnOpenCharacterSheet(self, skillIDs, certAvailable, *args):
        wnd = sm.GetService('charactersheet').GetWnd(1)
        wnd.Maximize()
        if wnd:
            if len(certAvailable) > 0:
                certButton = uiutil.GetChild(wnd, 'characterSheetMenuCertificatesBtn')
                if certButton:
                    certButton.Blink()
            blue.pyos.synchro.Sleep(500)
            wnd.sr.skilltabs.ShowPanelByName(mls.UI_GENERIC_HISTORY)
            blue.pyos.synchro.Sleep(500)
            skillIDsCopy = skillIDs[:]
            for node in wnd.sr.scroll.GetNodes():
                if node.id in skillIDsCopy:
                    wnd.sr.scroll._SelectNode(node)
                    skillIDsCopy.remove(node.id)




    def ShowSkillNotification(self, skillTypeIDs, left):
        certAvailable = sm.StartService('certificates').FindAvailableCerts()
        data = util.KeyVal()
        skillText = ''
        if len(skillTypeIDs) == 1:
            skill = sm.StartService('skills').GetMySkillsFromTypeID(skillTypeIDs[0])
            skillLevel = skill.skillLevel if skill is not None else mls.UI_GENERIC_UNKNOWN
            skillText = '%s - %s' % (cfg.invtypes.Get(skillTypeIDs[0]).name, mls.UI_SHARED_SKILLS_SKILLLEVEL % {'num': skillLevel})
        else:
            skillText = mls.UI_SHARED_SKILLS_NUMSKILLS % {'num': len(skillTypeIDs)}
        certText = ''
        if len(certAvailable) > 0:
            if len(certAvailable) == 1:
                certText = mls.UI_SHARED_SKILLS_CERTAVAILABLE
            else:
                certText = mls.UI_SHARED_SKILLS_CERTSAVAILABLE % {'num': len(certAvailable)}
        if not sm.StartService('skillqueue').IsRunning():
            blue.pyos.synchro.Sleep(1000)
        queue = sm.StartService('skillqueue').GetServerQueue()
        queueText = ''
        if len(queue) == 0:
            queueText = '<color=red>%s</color>' % mls.UI_SHARED_SKILLS_NOSKILLSINQUEUE
        data.headerText = mls.UI_GENERIC_SKILLTRAININGCOMPLETE
        data.text1 = skillText
        data.text2 = certText
        data.text3 = queueText
        icon = xtriui.PopupNotification(name='skillCompleted', align=uiconst.TOPLEFT, left=left, top=60, height=60, width=230, parent=None, idx=0)
        icon.state = uiconst.UI_NORMAL
        uicore.layer.abovemain.children.insert(0, icon)
        icon.Startup()
        icon.Load(data)
        icon.OnClick = (sm.StartService('skills').OnOpenCharacterSheet, skillTypeIDs, certAvailable)



    def OnFreeSkillPointsChanged(self, newFreeSkillPoints):
        self.SetFreeSkillPoints(newFreeSkillPoints)



    def GetFreeSkillPoints(self):
        if self.freeSkillPoints is None:
            return 0
        return self.freeSkillPoints



    def ApplyFreeSkillPoints(self, skillTypeID, pointsToApply):
        if self.freeSkillPoints is None:
            self.GetFreeSkillPoints()
        if self.SkillInTraining() is not None:
            raise UserError('CannotApplyFreePointsWhileQueueActive')
        skill = self.GetMySkillsFromTypeID(skillTypeID)
        if skill is None:
            raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': cfg.invtypes.Get(skillTypeID).name})
        spAtMaxLevel = skillUtil.GetSPForLevelRaw(skill.skillTimeConstant, 5)
        if skill.skillPoints + pointsToApply > spAtMaxLevel:
            pointsToApply = spAtMaxLevel - skill.skillPoints
        if pointsToApply > self.freeSkillPoints:
            raise UserError('CannotApplyFreePointsNotEnoughRemaining', {'pointsRequested': pointsToApply,
             'pointsRemaining': self.freeSkillPoints})
        if pointsToApply <= 0:
            return 
        skillQueue = sm.GetService('skillqueue').GetQueue()
        for (queueTypeID, queueLevel,) in skillQueue:
            if queueTypeID == skillTypeID:
                raise UserError('CannotApplyFreePointsToQueuedSkill', {'skillName': cfg.invtypes.Get(skillTypeID).name})

        newFreePoints = sm.GetService('godma').GetSkillHandler().ApplyFreeSkillPoints(skill.typeID, pointsToApply)
        self.SetFreeSkillPoints(newFreePoints)



    def SetFreeSkillPoints(self, newFreePoints):
        if self.freeSkillPoints is None or newFreePoints != self.freeSkillPoints:
            if self.freeSkillPoints is None or newFreePoints > self.freeSkillPoints:
                uthread.new(self.ShowSkillPointsNotification_thread)
            self.freeSkillPoints = newFreePoints
            sm.ScatterEvent('OnFreeSkillPointsChanged_Local')



    def ShowSkillPointsNotification(self, number = (0, 0), time = 5000, *args):
        skillPointsNow = self.GetFreeSkillPoints()
        skillPointsLast = settings.user.ui.Get('freeSkillPoints', -1)
        if skillPointsLast == skillPointsNow:
            return 
        if skillPointsNow <= 0:
            return 
        ahidden = sm.GetService('neocom').GetAHidden() or settings.user.windows.Get('neoalign', 'left') != 'left'
        BIG = settings.user.windows.Get('neowidth', 1) and not ahidden
        left = [[36, 2], [132, 2]][BIG][ahidden] + 14
        data = util.KeyVal()
        data.headerText = mls.UI_GENERIC_SKILLPOINTSAPPLIED
        data.text1 = mls.UI_GENERIC_UNALLOCATEDSKILLPOINTSINCHARSHEET
        data.text2 = None
        data.iconNum = 'ui_94_64_8'
        data.time = time
        icon = uiutil.FindChild(uicore.layer.abovemain, 'newmail')
        if not icon:
            icon = xtriui.PopupNotification(name='skillpointsapplied', parent=None, align=uiconst.TOPLEFT, pos=(left,
             60,
             230,
             60), idx=0)
            icon.state = uiconst.UI_NORMAL
            uicore.layer.abovemain.children.insert(0, icon)
            icon.Startup()
        icon.Load(data)
        settings.user.ui.Set('freeSkillPoints', skillPointsNow)
        return icon



    def ShowSkillPointsNotification_thread(self):
        blue.pyos.synchro.Sleep(5000)
        self.ShowSkillPointsNotification()




