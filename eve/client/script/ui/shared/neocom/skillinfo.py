import sys
import blue
import uthread
import uix
import log
import base
import util
import listentry
import trinity
import math
import skillUtil
import uiconst
import uicls

class BaseSkillEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.BaseSkillEntry'
    __nonpersistvars__ = ['selection', 'id']

    def init(self):
        self.lasttime = None
        self.lastprogress = None
        self.lastrate = None
        self.timer = None
        self.totalpoints = None
        self.hilitePartiallyTrained = None
        self.blueColor = (0.0, 0.52, 0.67, 1.0)
        self.whiteColor = (1.0, 1.0, 1.0, 0.5)
        self.skillPointsText = ''
        self.rank = 0.0



    def _OnClose(self):
        uicls.SE_BaseClassCore._OnClose(self)
        self.timer = None



    def Startup(self, *args):
        sub = uicls.Container(name='sub', parent=self)
        self.sr.inTrainingHilite = uicls.Fill(parent=self, name='inTrainingHilite', padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.15), state=uiconst.UI_HIDDEN)
        uicls.Container(name='push', parent=sub, width=32, align=uiconst.TOLEFT)
        self.sr.icon = uicls.Icon(name='skillIcon', parent=sub, align=uiconst.CENTERLEFT, size=32, width=32, height=32, ignoreSize=True)
        self.sr.icon.state = uiconst.UI_DISABLED
        self.sr.haveicon = uicls.Icon(name='haveIcon', parent=sub, size=16, left=20, align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN)
        uicls.Container(name='push', parent=sub, width=18, align=uiconst.TORIGHT)
        self.sr.levelParent = uicls.Container(name='levelParent', parent=sub, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED)
        self.sr.levelHeaderParent = uicls.Container(name='levelHeaderParent', parent=sub, align=uiconst.TORIGHT, state=uiconst.UI_HIDDEN)
        self.sr.levels = uicls.Container(name='levels', parent=self.sr.levelParent, align=uiconst.TOPLEFT, left=0, top=5, width=48, height=10)
        uicls.Line(parent=self.sr.levels, align=uiconst.TOTOP, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=self.sr.levels, align=uiconst.TOBOTTOM, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=self.sr.levels, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.5))
        uicls.Line(parent=self.sr.levels, align=uiconst.TORIGHT, color=(1.0, 1.0, 1.0, 0.5))
        for i in xrange(5):
            f = uicls.Fill(parent=self.sr.levels, name='level%d' % i, align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=2 + i * 9, top=2, width=8, height=6)
            setattr(self.sr, 'box_%s' % i, f)

        self.sr.progressbarparent = uicls.Container(name='progressbarparent', parent=self.sr.levelParent, align=uiconst.TOPLEFT, left=0, top=20, width=48, height=6)
        self.sr.progressBar = uicls.Fill(parent=self.sr.progressbarparent, name='progressbar', align=uiconst.RELATIVE, color=(1.0, 1.0, 1.0, 0.5), left=2, top=2, height=2, state=uiconst.UI_HIDDEN)
        uicls.Frame(parent=self.sr.progressbarparent)
        self.sr.levelHeader1 = uicls.Label(text='', parent=self.sr.levelHeaderParent, left=10, top=5, letterspace=2, fontsize=9, linespace=10, state=uiconst.UI_DISABLED, uppercase=1, idx=0, align=uiconst.TOPRIGHT)
        self.sr.levelHeader1.name = 'levelHeader1'
        textCont = uicls.Container(name='textCont', parent=sub, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.nameLevelLabel = uicls.Label(text='', parent=textCont, left=0, top=2, state=uiconst.UI_DISABLED, clipped=1, singleline=1)
        self.sr.nameLevelLabel.name = 'nameLevelLabel'
        self.sr.pointsLabel = uicls.Label(text='', parent=textCont, left=0, top=16, state=uiconst.UI_DISABLED, clipped=1, singleline=1)
        self.sr.pointsLabel.name = 'pointsLabel'
        self.sr.selection = uicls.Fill(parent=self, padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.selection.name = 'selection'
        self.sr.selection.state = uiconst.UI_HIDDEN
        self.sr.timeLeftText = uicls.Label(text='', parent=self.sr.levelHeaderParent, left=10, top=19, letterspace=1, fontsize=9, linespace=10, state=uiconst.UI_DISABLED, uppercase=1, idx=0, align=uiconst.TOPRIGHT)
        self.sr.timeLeftText.name = 'timeLeftText'
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.hilite = uicls.Fill(parent=self, name='hilite', padTop=1, padBottom=1, color=(1.0, 1.0, 1.0, 0.25))
        self.sr.infoicon = uicls.InfoIcon(size=16, left=2, top=2, parent=sub, idx=0, name='infoicon', align=uiconst.TOPRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.endOfTraining = None



    def Load(self, node):
        self.sr.node = node
        self.sr.node.meetRequirements = False
        self.lasttime = None
        self.lastsecs = None
        self.lastpoints = None
        self.timer = None
        self.endOfTraining = None
        self.hilitePartiallyTrained = settings.user.ui.Get('charsheet_hilitePartiallyTrainedSkills', False)
        data = node
        self.rec = data.skill
        self.skillPointsText = ''
        self.rank = 0.0
        self.sr.timeLeftText.text = ''
        if data.trained:
            self.rank = int(data.skill.skillTimeConstant + 0.4)
            if data.skill.skillLevel >= 5:
                self.skillPointsText = '<b>SP: %s</b>' % util.FmtAmt(data.skill.skillPoints)
            else:
                self.skillPointsText = '<b>SP: %s/%s</b>' % (util.FmtAmt(data.skill.skillPoints), util.FmtAmt(data.skill.spHi + 0.5))
                self.sr.node.meetRequirements = True
            self.sr.levelParent.state = uiconst.UI_PICKCHILDREN
            self.sr.levelHeaderParent.state = uiconst.UI_PICKCHILDREN
            self.sr.haveicon.state = uiconst.UI_HIDDEN
            self.sr.nameLevelLabel.color.SetRGB(1.0, 1.0, 1.0, 1.0)
            self.sr.pointsLabel.color.SetRGB(1.0, 1.0, 1.0, 1.0)
            self.hint = None
            self.GetIcon('complete')
        else:
            self.sr.levelParent.state = uiconst.UI_HIDDEN
            self.sr.levelHeaderParent.state = uiconst.UI_HIDDEN
            self.sr.haveicon.state = uiconst.UI_PICKCHILDREN
            self.sr.node.meetRequirements = sm.StartService('charactersheet').MeetSkillRequirements(data.invtype.typeID)
            if self.sr.node.meetRequirements:
                tappend = mls.UI_GENERIC_SKILLMEETREQUIREMENTS
            else:
                tappend = mls.UI_GENERIC_SKILLNOTMEETREQUIREMENTS
            self.GetHaveIcon(self.sr.node.meetRequirements)
            self.skillPointsText = tappend
            self.hint = tappend
            self.sr.nameLevelLabel.color.SetRGB(1.0, 1.0, 1.0, 0.75)
            self.sr.pointsLabel.color.SetRGB(1.0, 1.0, 1.0, 0.75)
            for each in cfg.dgmtypeattribs.get(data.invtype.typeID, []):
                if each.attributeID == const.attributeSkillTimeConstant:
                    self.rank = int(each.value)

            self.GetIcon()
        if data.Get('inTraining', 0):
            self.sr.inTrainingHilite.state = uiconst.UI_DISABLED
        else:
            self.sr.inTrainingHilite.state = uiconst.UI_HIDDEN
        self.Lolite()
        if data.Get('selected', 0):
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN



    def GetIcon(self, state = None):
        icon = {'untrained': 'ui_50_64_11',
         'new': 'ui_50_64_11',
         'partial': 'ui_50_64_12',
         'intraining': 'ui_50_64_12',
         'chapter': 'ui_50_64_13',
         'complete': 'ui_50_64_14'}.get(state, 'ui_50_64_11')
        self.sr.icon.LoadIcon(icon, ignoreSize=True)
        self.sr.icon.SetSize(32, 32)



    def GetHaveIcon(self, have = 0):
        if have:
            self.sr.haveicon.LoadIcon('ui_38_16_193')
        else:
            self.sr.haveicon.LoadIcon('ui_38_16_194')



    def UpdateTraining(self, skill):
        if not self or self.destroyed:
            return 
        spm = skill.spm
        ETA = skill.skillTrainingEnd
        spHi = skill.spHi
        level = skill.skillLevel
        if not self or self.destroyed or util.GetAttrs(self, 'sr', 'node', 'skill', 'itemID') != skill.itemID:
            return 
        if ETA:
            time = ETA - blue.os.GetTime()
            secs = time / 10000000L
        else:
            time = 0
            secs = 0
        currentPoints = 0
        if spHi is not None:
            currentPoints = spHi - secs / 60.0 * spm
        if util.GetAttrs(self, 'sr', 'node', 'trainToLevel') != level:
            if util.GetAttrs(self, 'sr', 'node', 'timeLeft'):
                time = self.sr.node.timeLeft
            else:
                time = None
        self.SetTimeLeft(time)
        if ETA:
            self.endOfTraining = ETA
        else:
            self.endOfTraining = None
        self.lasttime = blue.os.GetTime()
        self.lastsecs = secs
        self.lastpoints = currentPoints
        self.timer = base.AutoTimer(1000, self.UpdateProgress)
        return currentPoints



    def UpdateHalfTrained(self):
        skill = self.rec
        if self.endOfTraining is None:
            self.timer = None
            currentPoints = skill.skillPoints
        elif self.rec.flagID == const.flagSkillInTraining:
            secs = (self.endOfTraining - blue.os.GetTime()) / 10000000L
            currentPoints = min(skill.spHi - secs / 60.0 * skill.spm, skill.spHi)
            self.GetIcon('intraining')
        else:
            currentPoints = skill.skillPoints
        currentSpL = skillUtil.GetSPForLevelRaw(skill.skillTimeConstant, skill.skillLevel)
        if skill.skillPoints < skill.spHi:
            if skill.skillPoints > int(math.ceil(skill.spLo)):
                self.GetIcon('partial')
                if self.hilitePartiallyTrained:
                    self.sr.nameLevelLabel.text = '<color=0xffeec900>%s' % self.sr.nameLevelLabel.text
                    self.sr.pointsLabel.text = '<color=0xffeec900>%s' % self.sr.pointsLabel.text
            else:
                self.GetIcon('chapter')
            self.sr.progressBar.width = int(44 * (float(currentPoints - currentSpL) / (skill.spHi - currentSpL)))
            self.sr.progressBar.state = uiconst.UI_DISABLED
        else:
            self.GetIcon('complete')
            self.sr.progressBar.state = uiconst.UI_HIDDEN
        if self.rec.flagID == const.flagSkillInTraining:
            self.GetIcon('intraining')



    def OnSkillpointChange(self, skillPoints = None):
        if self.destroyed:
            return 
        if skillPoints is None:
            skillPoints = self.rec.skillPoints
        skill = self.rec
        if skill.skillLevel >= 5:
            skillPointsText = '<b>SP: %s</b>' % util.FmtAmt(skillPoints)
        else:
            skillPointsText = '<b>SP: %s/%s</b>' % (util.FmtAmt(skillPoints), util.FmtAmt(skill.spHi + 0.5))
        self.sr.nameLevelLabel.text = '%s (%sx)' % (skill.type.typeName, int(skill.skillTimeConstant + 0.4))
        self.sr.pointsLabel.text = skillPointsText



    def OnMouseEnter(self, *args):
        if self.rec.itemID is None:
            return 
        if not eve.dragData:
            self.Hilite()
        eve.Message('ListEntryEnter')



    def OnMouseExit(self, *args):
        self.Lolite()



    def GetHeight(self, *args):
        pass



    def Hilite(self):
        self.sr.hilite.state = uiconst.UI_DISABLED



    def Lolite(self):
        self.sr.hilite.state = uiconst.UI_HIDDEN



    def OnDblClick(self, *args):
        pass



    def OnClick(self, *args):
        pass



    def ShowInfo(self, *args):
        sm.StartService('info').ShowInfo(self.rec.typeID, self.rec.itemID)



    def GetTimeLeft(self, rec):
        timeLeft = None
        if rec.skillLevel < 5 and rec.flagID == const.flagSkill:
            timeLeft = sm.StartService('godma').GetStateManager().GetTimeForTraining(rec.itemID) * 60 * SEC
        return timeLeft



    def SetTimeLeft(self, timeLeft):
        if self is not None and not self.destroyed and self.sr.Get('timeLeftText', None):
            if timeLeft is None:
                timeLeftText = ''
            elif timeLeft <= 0:
                timeLeftText = mls.UI_SHARED_COMPLETIONIMMINENT
            else:
                timeLeftText = util.FmtDate(long(timeLeft), 'ss')
            self.sr.timeLeftText.text = '%s' % timeLeftText
            self.AdjustTimerContWidth()



    def AdjustTimerContWidth(self, *args):
        self.sr.levelHeaderParent.width = max(self.sr.levelHeader1.textwidth + 18, self.sr.timeLeftText.textwidth + 18, 60)




class SkillEntry(BaseSkillEntry):
    __guid__ = 'listentry.SkillEntry'
    __nonpersistvars__ = ['selection', 'id']

    def Load(self, node):
        listentry.BaseSkillEntry.Load(self, node)
        data = node
        self.skillID = data.skillID
        plannedInQueue = data.Get('plannedInQueue', None)
        for i in xrange(5):
            fill = self.sr.Get('box_%s' % i)
            fill.SetRGB(*self.whiteColor)
            if data.skill.skillLevel > i:
                fill.state = uiconst.UI_DISABLED
            else:
                fill.state = uiconst.UI_HIDDEN
            if plannedInQueue and i >= data.skill.skillLevel and i <= plannedInQueue - 1:
                fill.SetRGB(*self.blueColor)
                fill.state = uiconst.UI_DISABLED
            sm.StartService('ui').StopBlink(fill)

        self.sr.nameLevelLabel.text = '%s (%sx)' % (data.invtype.name, self.rank)
        self.sr.pointsLabel.text = self.skillPointsText
        self.sr.levelHeader1.text = '%s %s' % (mls.UI_GENERIC_LEVEL, data.skill.skillLevel)
        if data.trained:
            if data.skill.flagID == const.flagSkillInTraining:
                uthread.new(self.UpdateTraining, data.skill)
            else:
                skill = data.skill
                if skill.spHi is not None:
                    timeLeft = self.GetTimeLeft(skill)
                    self.SetTimeLeft(timeLeft)
                if not self or self.destroyed:
                    return 
                self.UpdateHalfTrained()
        self.AdjustTimerContWidth()
        self.sr.levelParent.width = self.sr.levels.width + const.defaultPadding



    def UpdateTraining(self, skill):
        if not self or self.destroyed:
            return 
        currentPoints = listentry.BaseSkillEntry.UpdateTraining(self, skill)
        level = skill.skillLevel
        fill = self.sr.Get('box_%s' % int(level))
        fill.state = uiconst.UI_DISABLED
        fill.SetRGB(*self.whiteColor)
        sm.StartService('ui').BlinkSpriteA(fill, 1.0, time=1000.0, maxCount=0, passColor=0, minA=0.5)
        self.OnSkillpointChange(currentPoints)
        self.UpdateHalfTrained()
        self.AdjustTimerContWidth()



    def GetMenu(self):
        m = []
        if self.rec.itemID is not None:
            m += sm.StartService('skillqueue').GetAddMenuForSkillEntries(self.rec)
            m += sm.StartService('menu').GetMenuFormItemIDTypeID(self.rec.itemID, self.rec.typeID, ignoreMarketDetails=0)
        elif self.rec.typeID is not None:
            m += sm.StartService('menu').GetMenuFormItemIDTypeID(None, self.rec.typeID, ignoreMarketDetails=0)
        return m



    def UpdateProgress(self):
        try:
            if self.endOfTraining is None:
                self.timer = None
                return 
            ms = blue.os.TimeDiffInMs(self.lasttime)
            timeEndured = blue.os.GetTime() - self.lasttime
            skill = self.rec
            timeLeft = self.endOfTraining - blue.os.GetTime()
            secs = timeLeft / 10000000L
            currentPoints = min(skill.spHi - secs / 60.0 * skill.spm, skill.spHi)
            self.OnSkillpointChange(currentPoints)
            self.SetTimeLeft(timeLeft)
            self.UpdateHalfTrained()
        except:
            self.timer = None
            log.LogException()
            sys.exc_clear()



    def GetDragData(self, *args):
        return [self.sr.node]



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 32
        return node.height




