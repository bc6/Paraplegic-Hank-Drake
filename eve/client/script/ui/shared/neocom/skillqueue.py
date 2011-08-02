import blue
import xtriui
import util
import uix
import uthread
import math
import listentry
import base
import sys
import uiconst
import log
import uicls
SKILLQUEUETIME = const.skillQueueTime
FILTER_ALL = 0
FILTER_PARTIAL = 1
FILTER_EXCLUDELVL5 = 2
FITSINQUEUE_DEFAULT = 0

class SkillQueue(uicls.Window):
    __guid__ = 'form.SkillQueue'
    __notifyevents__ = ['OnSkillFinished',
     'OnSkillStarted',
     'OnSkillPaused',
     'OnSkillQueueTrimmed',
     'OnGodmaSkillInjected',
     'OnSkillQueueRefreshed',
     'OnGodmaSkillTrained']
    default_top = 110

    def default_left(self):
        (leftpush, rightpush,) = sm.GetService('neocom').GetSideOffset()
        return leftpush



    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.SetCaption(mls.UI_SHARED_SQ_TRAININGQUEUE)
        self.SetWndIcon('50_13')
        self.godma = sm.GetService('godma')
        self.skillHandler = self.godma.GetSkillHandler()
        self.SetTopparentHeight(0)
        self.queueLastApplied = []
        self.isSaving = 0
        self.minWidth = 275
        self.SetMinSize([self.minWidth, 350])
        self.expanded = 0
        self.skillTimer = 0
        self.barTimer = 0
        self.scrollWidth = 0
        self.lightBlueColor = (0.21, 0.62, 0.74, 1.0)
        self.darkerBlueColor = (0.0, 0.52, 0.67, 1.0)
        self.ConstructLayout()
        self.Load()



    def Load(self, *args):
        self.sr.skillCombo.SelectItemByValue(settings.user.ui.Get('skillqueue_comboFilter', FILTER_ALL))
        self.expanded = settings.user.ui.Get('skillqueue_skillsExpanded', 1)
        if self.expanded:
            self.SetMinSize([700, 350])
            self.OnClickRightExpander()
        else:
            self.OnClickLeftExpander()
        self.SetTime()
        sm.StartService('skillqueue').BeginTransaction()
        self.queueLastApplied = sm.StartService('skillqueue').GetQueue()
        parallelCalls = []
        parallelCalls.append((self.LoadQueue, ()))
        parallelCalls.append((self.LoadSkills, ()))
        uthread.parallel(parallelCalls)
        inTraining = sm.StartService('skills').SkillInTraining()
        if not inTraining:
            self.GrayButton(self.sr.pauseBtn, gray=1)
        uthread.new(self.StartBars)
        uthread.new(self.LoopTimers)



    def ConstructLayout(self):
        self.sr.leftOuterPar = uicls.Container(name='leftOuterPar', parent=self.sr.main, align=uiconst.TOLEFT, width=64)
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftOuterPar, 'width', 'x', self.minWidth, self.scrollWidth)
        divider.OnSizeChanged = self.OnDetailScrollSizeChanged
        self.sr.divider = divider
        uicls.Line(parent=divider, align=uiconst.TOLEFT)
        uicls.Line(parent=divider, align=uiconst.TORIGHT)
        self.sr.rightOuterPar = uicls.Container(name='rightOuterPar', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.leftFooterPar = uicls.Container(parent=self.sr.leftOuterPar, align=uiconst.TOBOTTOM, height=26)
        self.sr.rightFooterPar = uicls.Container(parent=self.sr.rightOuterPar, align=uiconst.TOBOTTOM, height=26)
        uicls.Container(name='push', align=uiconst.TORIGHT, width=const.defaultPadding, parent=self.sr.rightOuterPar)
        uicls.Container(name='push', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.rightOuterPar)
        uicls.Container(name='push', align=uiconst.TORIGHT, width=const.defaultPadding, parent=self.sr.leftOuterPar)
        uicls.Container(name='push', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.leftOuterPar)
        self.sr.leftHeader = uicls.Container(parent=self.sr.leftOuterPar, align=uiconst.TOTOP, height=60, top=0, clipChildren=1)
        self.sr.leftScroll = uicls.Scroll(parent=self.sr.leftOuterPar, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        self.sr.leftScroll.SelectAll = self.DoNothing
        self.sr.leftScroll.sr.content.OnDropData = self.DoRemove
        self.sr.leftScroll.sr.content.AddSkillToQueue = self.AddSkillToQueue
        self.sr.rightHeader = uicls.Container(parent=self.sr.rightOuterPar, align=uiconst.TOTOP, height=60, top=0, clipChildren=1)
        uicls.Container(name='push', align=uiconst.TORIGHT, width=const.defaultPadding, parent=self.sr.rightHeader)
        uicls.Container(name='push', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.rightHeader)
        mainBarCont = uicls.Container(name='mainBarCont', parent=self.sr.rightHeader, align=uiconst.TOBOTTOM, height=40)
        self.sr.barCont = uicls.Container(name='barCont', parent=mainBarCont, align=uiconst.TOTOP, height=19)
        self.sr.arrowCont = uicls.Container(name='arrowCont', parent=self.sr.barCont, align=uiconst.TORIGHT, width=5, state=uiconst.UI_HIDDEN, idx=0)
        self.sr.mainBar = uicls.Container(name='mainBar', parent=self.sr.barCont, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.timeLine = uicls.Container(name='timeLine', parent=mainBarCont, align=uiconst.TOBOTTOM, height=16)
        sprite = uicls.Sprite(name='arrow', parent=self.sr.arrowCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/whiteArrow.png')
        sprite.rectTop = 0
        sprite.rectLeft = 0
        sprite.rectWidth = 9
        sprite.rectHeight = 19
        self.sr.arrowSprite = sprite
        self.sr.rightScroll = uicls.Scroll(parent=self.sr.rightOuterPar, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        self.sr.rightScroll.sr.content.OnDropData = self.DoDropData
        self.sr.rightScroll.sr.content.RemoveSkillFromQueue = self.RemoveSkillFromQueue
        self.sr.sqFinishesText = uicls.Label(text='', parent=self.sr.rightHeader, left=4, top=10, letterspace=1, fontsize=9, linespace=10, state=uiconst.UI_DISABLED, uppercase=1, idx=0)
        self.sr.sqTimeText = uicls.Label(text='', parent=self.sr.rightHeader, left=4, top=10, letterspace=1, fontsize=9, linespace=10, state=uiconst.UI_DISABLED, uppercase=1, idx=0, align=uiconst.TOPRIGHT)
        comboOptions = [(mls.UI_SHARED_SQ_MYSKILLS, FILTER_ALL), (mls.UI_SHARED_SQ_MYPARTIALLYTRAINED, FILTER_PARTIAL), (mls.UI_SHARED_SQ_EXCLUDELVL5, FILTER_EXCLUDELVL5)]
        self.sr.skillCombo = uicls.Combo(label='', parent=self.sr.leftHeader, options=comboOptions, name='', align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         22,
         0,
         0), callback=self.OnComboChange, width=200)
        fitsChecked = settings.user.ui.Get('skillqueue_fitsinqueue', FITSINQUEUE_DEFAULT)
        cb = uicls.Checkbox(text=mls.UI_SHARED_SQ_FITINTIMEFRAME, parent=self.sr.leftHeader, configName='skillqueue_fitsinqueue', retval=None, checked=fitsChecked, callback=self.OnCheckboxChange, align=uiconst.TOPLEFT, pos=(0,
         self.sr.skillCombo.top + self.sr.skillCombo.height + const.defaultPadding,
         400,
         0))
        self.sr.fitsCheckbox = cb
        applyBtn = uicls.Button(parent=self.sr.rightFooterPar, label=mls.UI_CMD_APPLY, pos=(const.defaultPadding,
         3,
         0,
         0), func=self.SaveChanges)
        self.sr.pauseBtn = uicls.Button(parent=self.sr.rightFooterPar, label=mls.UI_CMD_PAUSE, pos=(applyBtn.left + applyBtn.width + 2,
         3,
         0,
         0), func=self.PauseTraining)
        removeBtn = uicls.Button(parent=self.sr.rightFooterPar, label=mls.UI_CMD_REMOVE, pos=(const.defaultPadding,
         3,
         0,
         0), align=uiconst.TOPRIGHT, func=self.RemoveSkillFromQueue)
        addBtn = uicls.Button(parent=self.sr.leftFooterPar, label=mls.UI_CMD_ADD, top=3, align=uiconst.CENTERTOP, func=self.AddSkillToQueue)
        uicls.Line(parent=self.sr.rightFooterPar, align=uiconst.TOTOP)
        uicls.Line(parent=self.sr.leftFooterPar, align=uiconst.TOTOP)
        self.sr.leftExpander = uicls.Icon(parent=self.sr.leftOuterPar, idx=0, size=16, state=uiconst.UI_NORMAL, icon='ui_1_16_99', top=2)
        self.sr.rightExpander = uicls.Icon(parent=self.sr.rightOuterPar, idx=0, size=16, state=uiconst.UI_HIDDEN, icon='ui_1_16_100', top=2)
        self.sr.leftExpander.OnClick = self.OnClickLeftExpander
        self.sr.rightExpander.OnClick = self.OnClickRightExpander



    def OnDetailScrollSizeChanged(self):
        w = self.sr.leftOuterPar.width
        absWidth = self.sr.main.absoluteRight - self.sr.main.absoluteLeft
        if w > absWidth - self.sr.main.width - self.minWidth:
            w = absWidth - self.sr.main.width - self.minWidth
            ratio = float(w) / absWidth
            settings.user.ui.Set('skillqueue_divider', ratio)
            self._OnResize()
            return 
        ratio = float(w) / absWidth
        settings.user.ui.Set('skillqueue_divider', ratio)
        self.RedrawBars()



    def _OnResize(self, *args):
        if self and not self.destroyed and util.GetAttrs(self, 'sr', 'leftOuterPar'):
            self.scrollWidth = self.sr.main.absoluteRight - self.sr.main.absoluteLeft - self.minWidth
            w = (self.absoluteRight - self.absoluteLeft - self.minWidth) / 2
            absWidth = self.sr.main.absoluteRight - self.sr.main.absoluteLeft
            ratio = settings.user.ui.Get('skillqueue_divider', 0.5)
            w = int(ratio * absWidth)
            if w > self.scrollWidth:
                w = self.scrollWidth
            self.sr.leftOuterPar.width = max(self.minWidth, w)
            self.sr.divider.max = self.scrollWidth
            self.RedrawBars()



    def OnComboChange(self, combo, config, value):
        settings.user.ui.Set('skillqueue_comboFilter', value)
        self.ReloadSkills()



    def OnCheckboxChange(self, cb, *args):
        settings.user.ui.Set(cb.name, bool(cb.checked))
        self.ReloadSkills()



    def GrayButton(self, btn, gray = 1):
        inTraining = sm.StartService('skills').SkillInTraining()
        if gray and not inTraining:
            btn.SetLabel('<color=gray>%s</color>' % mls.UI_CMD_PAUSE)
            btn.state = uiconst.UI_DISABLED
        else:
            btn.SetLabel(mls.UI_CMD_PAUSE)
            btn.state = uiconst.UI_NORMAL



    def OnClickLeftExpander(self, *args):
        self.SetupCollapsed()
        self._OnResize()



    def SetupCollapsed(self):
        self.SetMinSize([self.minWidth, 350])
        self.expanded = 0
        settings.user.ui.Set('skillqueue_skillsExpanded', 0)
        self.sr.leftOuterPar.state = uiconst.UI_HIDDEN
        self.sr.divider.state = uiconst.UI_HIDDEN
        self.sr.rightExpander.state = uiconst.UI_NORMAL



    def OnClickRightExpander(self, *args):
        self.SetupExpanded()
        self.LoadSkills()
        self._OnResize()



    def SetupExpanded(self):
        self.SetMinSize([700, 350])
        self.expanded = 1
        settings.user.ui.Set('skillqueue_skillsExpanded', 1)
        self.sr.leftOuterPar.state = uiconst.UI_PICKCHILDREN
        self.sr.rightExpander.state = uiconst.UI_HIDDEN
        self.sr.divider.state = uiconst.UI_NORMAL



    def SaveChanges(self, *args):
        if self.isSaving == 1:
            return 
        queue = sm.StartService('skillqueue').GetQueue()
        try:
            self.isSaving = 1
            sm.StartService('skillqueue').CommitTransaction()
            self.queueLastApplied = queue

        finally:
            if self and not self.destroyed:
                sm.StartService('skillqueue').BeginTransaction()
                self.isSaving = 0




    def PauseTraining(self, *args):
        inTraining = sm.StartService('skills').SkillInTraining()
        if inTraining:
            sm.StartService('skills').AbortTrain(inTraining)



    def OnClose_(self, *args):
        if self.isSaving:
            return 
        queue = sm.StartService('skillqueue').GetQueue()
        if queue != self.queueLastApplied:
            uthread.new(self.ConfirmSavingOnClose)
        else:
            sm.StartService('skillqueue').RollbackTransaction()



    def ConfirmSavingOnClose(self):
        if eve.Message('QueueSaveChangesOnClose', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            queue = sm.StartService('skillqueue').GetQueue()
            sm.StartService('skillqueue').CommitTransaction()
        else:
            sm.StartService('skillqueue').RollbackTransaction()



    def ReloadSkills(self, force = 0, time = 1000):
        if self.expanded == 1 or force:
            self.skillTimer = base.AutoTimer(time, self.LoadSkills)



    def LoadSkills(self):
        self.skillTimer = 0
        groups = sm.GetService('skills').GetSkillGroups()
        scrolllist = []
        queLength = sm.GetService('skillqueue').GetTrainingLengthOfQueue()
        timeLeftInQueue = max(0, SKILLQUEUETIME - queLength)
        queue = sm.StartService('skillqueue').GetQueue()
        skillsInQueue = [ skillID for (skillID, level,) in queue ]
        fitsChecked = settings.user.ui.Get('skillqueue_fitsinqueue', FITSINQUEUE_DEFAULT)
        partialChecked = settings.user.ui.Get('skillqueue_comboFilter', FILTER_ALL) == FILTER_PARTIAL
        excludeLvl5 = settings.user.ui.Get('skillqueue_comboFilter', FILTER_ALL) == FILTER_EXCLUDELVL5
        for (group, skills, untrained, intraining, inqueue, points,) in groups:
            if not len(skills):
                continue
            skills.sort(lambda x, y: cmp(cfg.invtypes.Get(x.typeID).name, cfg.invtypes.Get(y.typeID).name))
            filteredSkills = []
            if fitsChecked or partialChecked or excludeLvl5:
                for skill in skills:
                    if excludeLvl5:
                        if skill.skillLevel >= 5:
                            continue
                    if partialChecked:
                        if skill.skillPoints >= skill.spHi or not skill.skillPoints > int(math.ceil(skill.spLo)):
                            continue
                    if fitsChecked:
                        timeLeft = 0
                        if skill.typeID in skillsInQueue:
                            nextLevel = sm.StartService('skillqueue').FindNextLevel(skill.typeID, skill.skillLevel, queue)
                        else:
                            nextLevel = skill.skillLevel + 1
                        if nextLevel:
                            if nextLevel <= 5:
                                (totalTime, timeLeft,) = sm.StartService('skillqueue').GetTrainingLengthOfSkill(skill.typeID, nextLevel)
                                if timeLeft > timeLeftInQueue:
                                    continue
                                skill.fitInfo = (nextLevel, timeLeft)
                            else:
                                continue
                    filteredSkills.append(skill)

                skills = filteredSkills
            if len(skills) < 1:
                continue
            label = '%s, %s' % (mls.UI_SHARED_GROUPLABELSKILLS % {'groupName': group.groupName,
              'numSkills': len(skills)}, mls.UI_SHARED_NUMPOINTS % {'points': util.FmtAmt(points)})
            data = {'GetSubContent': self.GetSubContent,
             'label': '%s [%s]' % (label, len(skills)),
             'groupItems': skills,
             'inqueue': inqueue,
             'id': ('skillqueue', group.groupID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0,
             'DropData': self.RemoveToGroup,
             'allowGuids': ['listentry.SkillQueueSkillEntry'],
             'BlockOpenWindow': 1}
            scrolllist.append(listentry.Get('Group', data))

        pos = self.sr.leftScroll.GetScrollProportion()
        self.sr.leftScroll.sr.id = 'skillqueue_leftview'
        self.sr.leftScroll.Load(contentList=scrolllist, headers=[], scrollTo=pos, noContentHint=mls.UI_RMR_TEXT10)



    def GetSubContent(self, data, *args):
        scrolllist = []
        queue = sm.StartService('skillqueue').GetQueue()
        skillsInQueue = [ skillID for (skillID, level,) in queue ]
        for skill in data.groupItems:
            invtype = cfg.invtypes.Get(skill.typeID)
            fitInfo = getattr(skill, 'fitInfo', None)
            if fitInfo is not None:
                nextLevel = fitInfo[0]
                timeLeft = fitInfo[1]
            else:
                skillID = invtype.id
                mySkillLevel = skill.skillLevel
                if skillID in skillsInQueue:
                    nextLevel = sm.StartService('skillqueue').FindNextLevel(skillID, skill.skillLevel, queue)
                else:
                    nextLevel = mySkillLevel + 1
                timeLeft = 0
                if nextLevel and nextLevel <= 5:
                    (totalTime, timeLeft,) = sm.StartService('skillqueue').GetTrainingLengthOfSkill(skillID, nextLevel)
            data = {}
            data['invtype'] = invtype
            data['skill'] = skill
            data['trained'] = skill.itemID != None
            data['timeLeft'] = timeLeft
            data['skillID'] = invtype.id
            data['trainToLevel'] = nextLevel - 1
            data['currentLevel'] = skill.skillLevel
            data['inTraining'] = [0, 1][(skill.flagID == const.flagSkillInTraining)]
            scrolllist.append(listentry.Get('SkillQueueSkillEntry', data))
            if hasattr(skill, 'flagID') and skill.flagID == const.flagSkillInTraining:
                sm.StartService('godma').GetStateManager().GetEndOfTraining(skill.itemID)

        return scrolllist



    def ReloadQueue(self):
        self.queueTimer = base.AutoTimer(1000, self.LoadQueue)



    def LoadQueue(self):
        self.queueTimer = 0
        mySkills = sm.StartService('skills').GetMyGodmaItem().skills
        queue = sm.StartService('skillqueue').GetQueue()
        allTrainingLengths = sm.StartService('skillqueue').GetAllTrainingLengths()
        scrolllist = []
        for (skillID, nextLevel,) in queue:
            invtype = cfg.invtypes.Get(skillID)
            skill = mySkills.get(skillID, None)
            if skill is None:
                sm.StartService('skillqueue').RemoveSkillFromQueue(skillID, nextLevel)
                continue
            time = allTrainingLengths.get((invtype.id, nextLevel), [0, 0])
            entry = self.GetRightEntry(invtype, skill, nextLevel, time[1])
            scrolllist.append(entry)

        self.sr.rightScroll.Load(contentList=scrolllist)
        self.UpdateTime()



    def GetRightEntry(self, invtype, skill, trainToLevel, timeLeft):
        data = {}
        data['invtype'] = invtype
        data['skill'] = skill
        data['trained'] = skill.itemID != None
        data['inQueue'] = 1
        data['trainToLevel'] = trainToLevel
        data['currentLevel'] = getattr(skill, 'skillLevel', 0)
        data['timeLeft'] = timeLeft
        data['skillID'] = invtype.id
        data['inTraining'] = [0, 1][(skill.flagID == const.flagSkillInTraining)]
        entry = listentry.Get('SkillQueueSkillEntry', data)
        return entry



    def UpdateTime(self):
        self.SetTime()
        self.DrawBars()



    def SetTime(self):
        timeEnd = sm.StartService('skillqueue').GetTrainingEndTimeOfQueue()
        inTraining = sm.StartService('skills').SkillInTraining()
        if inTraining and sm.StartService('skillqueue').FindInQueue(inTraining.typeID, inTraining.skillLevel + 1):
            fullTrainingTime = sm.StartService('skillqueue').GetTrainingLengthOfSkill(inTraining.typeID, inTraining.skillLevel + 1)
            ETA = inTraining.skillTrainingEnd
            if ETA is not None:
                timeEnd -= fullTrainingTime[1]
                leftTime = ETA - blue.os.GetTime()
                timeEnd += leftTime
        timeEnd = long(timeEnd)
        if timeEnd > blue.os.GetTime():
            self.sr.sqFinishesText.text = mls.UI_SHARED_SQ_FINISHES % {'date': util.FmtDate(timeEnd, 'll')}
        timeLeft = timeEnd - blue.os.GetTime()
        self.sr.sqTimeText.text = '%s' % util.FmtDate(long(timeLeft), 'ss')
        self.allTrainingLengths = sm.StartService('skillqueue').GetAllTrainingLengths()
        self.queueEnds = timeEnd
        self.queueTimeLeft = timeLeft
        self.lasttime = blue.os.GetTime()



    def LoopTimers(self, *args):
        while self and not self.destroyed:
            inTraining = sm.StartService('skills').SkillInTraining()
            now = blue.os.GetTime()
            lasttime = getattr(self, 'lasttime', now)
            diff = now - lasttime
            queueEnds = getattr(self, 'queueEnds', None)
            timeLeft = getattr(self, 'queueTimeLeft', None)
            if queueEnds is not None and queueEnds >= now and timeLeft is not None:
                if inTraining and sm.StartService('skillqueue').FindInQueue(inTraining.typeID, inTraining.skillLevel + 1) is not None:
                    timeLeft = timeLeft - diff
                    self.queueTimeLeft = timeLeft
                else:
                    queueEnds = self.queueEnds + diff
                    self.queueEnds = queueEnds
                self.lasttime = now
                if queueEnds > blue.os.GetTime():
                    self.sr.sqFinishesText.text = mls.UI_SHARED_SQ_FINISHES % {'date': util.FmtDate(queueEnds, 'll')}
                timeLeft = max(0, timeLeft)
                self.sr.sqTimeText.text = '%s' % util.FmtDate(long(timeLeft), 'ss')
                self.UpdatingBars()
            else:
                self.sr.sqFinishesText.text = ''
                self.sr.sqTimeText.text = ''
            blue.pyos.synchro.Sleep(1000)




    def StartBars(self):
        while self and not self.destroyed:
            if util.GetAttrs(self, 'sr', 'mainBar') and self.sr.mainBar.absoluteRight - self.sr.mainBar.absoluteLeft > 0:
                break
            blue.pyos.synchro.Sleep(500)

        if not self or self.destroyed:
            return 
        self.DrawBars()



    def UpdatingBars(self):
        self.barUpdatingTimer = base.AutoTimer(1000, self.DrawBars, (1,))



    def RedrawBars(self):
        self.barTimer = base.AutoTimer(1000, self.DrawBars)



    def DrawBars(self, updating = 0):
        bar = self.sr.mainBar
        if bar is None or bar.destroyed:
            return 
        (l, t, w, h,) = bar.GetAbsolute()
        if w <= 0:
            return 
        inTraining = sm.StartService('skills').SkillInTraining()
        if updating and inTraining is None:
            return 
        self.barTimer = 0
        self.barUpdatingTimer = 0
        barWidth = w
        uix.Flush(self.sr.mainBar)
        uix.Flush(self.sr.timeLine)
        totalTime = const.skillQueueTime
        percentages = {}
        for item in self.allTrainingLengths.iteritems():
            (key, value,) = item
            time = value[1]
            if inTraining and key[0] == inTraining.typeID and key[1] == inTraining.skillLevel + 1:
                ETA = inTraining.skillTrainingEnd
                if ETA is not None:
                    time = float(ETA - blue.os.GetTime())
            per = time / totalTime
            percentages[key] = per

        hours = totalTime / HOUR
        interval = barWidth / float(hours)
        left = 0
        for i in xrange(hours + 1):
            left = min(barWidth - 1, int(i * interval))
            uicls.Line(parent=self.sr.timeLine, align=uiconst.RELATIVE, weight=1, left=left, width=1, height=5)

        txt0 = uicls.Label(text='0', parent=self.sr.timeLine, fontsize=9, letterspace=2, uppercase=1, top=5, left=0, state=uiconst.UI_NORMAL)
        txt12 = uicls.Label(text='12', parent=self.sr.timeLine, fontsize=9, letterspace=2, uppercase=1, top=5, left=int(interval * 12) - 5, state=uiconst.UI_NORMAL)
        txt24 = uicls.Label(text='24', parent=self.sr.timeLine, fontsize=9, letterspace=2, uppercase=1, top=5, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        colors = [self.lightBlueColor, self.darkerBlueColor]
        queue = sm.StartService('skillqueue').GetQueue()
        left = 0
        counter = 0
        barInfo = []
        color = 1
        f = None
        for key in queue:
            color = int(not color)
            percentage = percentages.get(key, 0.0)
            width = max(2, percentage * barWidth)
            intWidth = int(round(width))
            f = uicls.Fill(parent=bar, name='barfill', align=uiconst.TOLEFT, color=colors[color], width=intWidth)
            barInfo.append((intWidth, int(left), colors[color]))
            left += width
            counter += 1

        uicls.Fill(parent=bar, align=uiconst.TOTOP, color=(0.2, 0.2, 0.2, 1), height=19, state=uiconst.UI_DISABLED)
        if barWidth and left > barWidth:
            self.sr.arrowCont.state = uiconst.UI_DISABLED
            self.sr.arrowSprite.color.SetRGB(colors[color][0], colors[color][1], colors[color][2])
            if f is not None:
                f.align = uiconst.TOALL
                f.width = 0
        else:
            self.sr.arrowCont.state = uiconst.UI_HIDDEN
        self.UpdateBars(barInfo)



    def UpdateBars(self, barInfo):
        if not barInfo:
            return 
        barInfoLength = len(barInfo)
        for (counter, entry,) in enumerate(self.sr.rightScroll.GetNodes()):
            barInfoLength = len(barInfo)
            if counter > barInfoLength - 1:
                return 
            self.SetBarInfo(entry, barInfo[counter])
            if entry.panel is None or counter >= barInfoLength:
                continue
            entry.panel.UpdateBar()




    def SetBarInfo(self, entry, barInfo):
        (width, left, color,) = barInfo
        entry.barWidth = width
        entry.barLeft = left
        entry.barColor = color



    def AddSkillToQueue(self, *args):
        queue = sm.StartService('skillqueue').GetQueue()
        selected = self.sr.leftScroll.GetSelected()
        try:
            for entry in selected:
                skillAdded = self.AddSkillThroughSkillEntry(entry, queue)
                if skillAdded:
                    self.ChangeEntry(entry)


        finally:
            self.UpdateTime()




    def AddSkillThroughSkillEntry(self, data, queue, idx = -1, refresh = 0):
        if not data.Get('meetRequirements', 0):
            return False
        nextLevel = sm.StartService('skillqueue').FindNextLevel(data.skillID, data.skill.skillLevel, queue)
        if nextLevel is None or nextLevel > 5:
            eve.Message('CustomNotify', {'notify': mls.UI_SHARED_SQ_LEVEL5PLANNED})
            return False
        self.DoAddSkill(data.invtype, data.skill, nextLevel, idx)
        if settings.user.ui.Get('skillqueue_fitsinqueue', FITSINQUEUE_DEFAULT):
            self.ReloadSkills(time=2000)
        if refresh:
            self.UpdateTime()
            self.ReloadEntriesIfNeeded()
        return True



    def AddSkillsThroughOtherEntry(self, skillID, idx, queue, nextLevel = None, refresh = 0):
        mySkills = sm.StartService('skills').GetMyGodmaItem().skills
        skill = mySkills.get(skillID, None)
        if skill is None:
            raise UserError('CustomNotify', {'notify': mls.UI_SHARED_SQ_DONTHAVESKILL})
        if nextLevel is None:
            nextLevel = sm.StartService('skillqueue').FindNextLevel(skillID, skill.skillLevel, queue)
        if nextLevel > 5:
            return 
        invtype = cfg.invtypes.Get(skillID)
        self.DoAddSkill(invtype, skill, nextLevel, idx)
        if settings.user.ui.Get('skillqueue_fitsinqueue', FITSINQUEUE_DEFAULT):
            self.ReloadSkills(time=2000)
        if refresh:
            self.UpdateTime()
            self.ReloadEntriesIfNeeded()
        return True



    def DoAddSkill(self, invtype, skill, trainToLevel, idx = -1):
        skillID = invtype.id
        timeLeft = sm.StartService('skillqueue').GetTrainingLengthOfSkill(skillID, trainToLevel)
        entry = self.GetRightEntry(invtype, skill, trainToLevel, timeLeft[1])
        sm.StartService('skillqueue').AddSkillToQueue(skillID, trainToLevel, position=idx)
        self.sr.rightScroll.AddEntries(idx, [entry])



    def MoveUp(self, *args):
        self.Move(-1)



    def MoveDown(self, *args):
        self.Move(1)



    def Move(self, direction):
        queueLength = sm.StartService('skillqueue').GetNumberOfSkillsInQueue()
        selected = self.sr.rightScroll.GetSelected()
        if len(selected) > 1:
            eve.Message('CustomNotify', {'notify': mls.UI_SHARED_SQ_CANONLYMOVEONE})
            return 
        for data in selected:
            newIdx = max(-1, data.idx + direction)
            condition = False
            if direction == -1 and data.idx >= 0:
                condition = True
            elif direction == 1 and data.idx < queueLength - 1:
                condition = True
            if data.skillID and condition:
                self.DoMove(data, newIdx, queueLength)




    def DoMove(self, data, newIdx, queueLength, movingBelow = 0):
        trainToLevel = data.Get('trainToLevel', None)
        if data.skillID and trainToLevel:
            skillPos = newIdx
            if newIdx == -1:
                skillPos = queueLength - 1
            sm.StartService('skillqueue').MoveSkillToPosition(data.skillID, trainToLevel, skillPos)
            newLength = sm.StartService('skillqueue').GetNumberOfSkillsInQueue()
            if queueLength != newLength:
                self.ReloadQueue()
            else:
                self.sr.rightScroll.RemoveEntries([data])
                self.sr.rightScroll.AddEntries(skillPos - movingBelow, [data])
                self.sr.rightScroll.SelectNode(data)



    def RemoveSkillFromQueue(self, *args):
        selected = self.sr.rightScroll.GetSelected()
        self.DoRemove(None, selected)



    def RemoveToGroup(self, id, nodes):
        self.DoRemove(None, nodes)



    def DoRemove(self, dragObj, entries, *args):
        entries.reverse()
        removeList = []
        for entry in entries:
            if not util.GetAttrs(entry, 'inQueue'):
                return 
            trainToLevel = entry.Get('trainToLevel', -1)
            try:
                sm.StartService('skillqueue').RemoveSkillFromQueue(entry.invtype.id, trainToLevel)
                removeList.append(entry)
            except UserError:
                self.ReloadAfterRemove(removeList)
                raise 
            self.ReloadAfterRemove(removeList)




    def ReloadAfterRemove(self, removeList):
        self.sr.rightScroll.RemoveEntries(removeList)
        self.ReloadEntriesIfNeeded()
        self.UpdateTime()
        if settings.user.ui.Get('skillqueue_fitsinqueue', FITSINQUEUE_DEFAULT):
            self.ReloadSkills(time=2000)



    def DoDropData(self, dragObj, entries, idx = -1):
        queue = sm.StartService('skillqueue').GetQueue()
        if not entries:
            return 
        if idx == -1:
            idx = len(queue)
        data = entries[0]
        if data.__guid__ == 'listentry.SkillQueueSkillEntry':
            if data.Get('inQueue', None):
                movingBelow = 0
                if idx > data.idx:
                    movingBelow = 1
                newIdx = max(0, idx)
                if data.skillID:
                    self.DoMove(data, newIdx, len(queue), movingBelow)
            else:
                skillAdded = self.AddSkillThroughSkillEntry(data, queue, idx)
        elif data.__guid__ == 'listentry.SkillEntry':
            skillAdded = self.AddSkillThroughSkillEntry(data, queue, idx)
        elif data.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            category = util.GetAttrs(data, 'rec', 'categoryID')
            if category == const.categorySkill:
                sm.StartService('skills').InjectSkillIntoBrain([data.item])
                blue.pyos.synchro.Sleep(500)
                self.AddSkillsThroughOtherEntry(data.item.typeID, idx, queue, nextLevel=1)
        elif data.__guid__ in ('xtriui.CertSlot',):
            if data.rec.certID is None:
                skillAdded = self.AddSkillsThroughOtherEntry(data.rec.typeID, idx, queue)
        self.UpdateTime()
        self.ReloadEntriesIfNeeded()



    def ChangeEntry(self, entry, force = 0):
        if self.expanded == 0 and not force:
            return 
        queue = sm.StartService('skillqueue').GetQueue()
        skillID = entry.skillID
        skill = entry.skill
        nextLevel = sm.StartService('skillqueue').FindNextLevel(skillID, skill.skillLevel, queue)
        timeLeft = 0
        if nextLevel and nextLevel <= 5:
            (totalTime, timeLeft,) = sm.StartService('skillqueue').GetTrainingLengthOfSkill(skillID, nextLevel)
        entry.trainToLevel = nextLevel - 1
        entry.timeLeft = timeLeft
        if entry.panel:
            entry.panel.sr.timeLeftText.text = util.FmtDate(long(timeLeft), 'ss')
            entry.panel.FillBoxes(skill.skillLevel, nextLevel - 1)



    def ReloadEntriesIfNeeded(self, force = 0):
        if self.expanded == 0 and not force:
            return 
        for entry in self.sr.leftScroll.GetNodes():
            if entry.__guid__ != 'listentry.SkillQueueSkillEntry':
                continue
            self.ChangeEntry(entry)




    def OnSkillQueueTrimmed(self, removedSkills):
        self.LoadQueue()
        self.ReloadSkills()



    def OnSkillFinished(self, skillItemID, skillID, level):
        if (skillID, level) in self.queueLastApplied:
            self.queueLastApplied.remove((skillID, level))
        self.LoadQueue()
        self.ReloadSkills()



    def OnSkillStarted(self, skillID = None, level = None):
        self.LoadQueue()
        self.ReloadSkills()
        self.GrayButton(self.sr.pauseBtn, gray=0)



    def OnSkillPaused(self, skillItemID):
        self.LoadQueue()
        self.ReloadSkills()
        self.GrayButton(self.sr.pauseBtn, gray=1)



    def OnGodmaSkillInjected(self):
        self.ReloadSkills()



    def OnGodmaSkillTrained(self, skillID):
        self.ReloadSkills()



    def OnSkillQueueRefreshed(self):
        self.LoadQueue()
        self.ReloadSkills()



    def DoNothing(self):
        pass




class SkillQueueSkillEntry(listentry.BaseSkillEntry):
    __guid__ = 'listentry.SkillQueueSkillEntry'
    __nonpersistvars__ = ['selection', 'id']

    def Startup(self, *args):
        self.entryHeight = 0
        self.blinking = 0
        listentry.BaseSkillEntry.Startup(self, *args)
        self.barWidth = 0
        self.barHeigth = 0
        self.barLeft = 0
        self.sr.bar = uicls.Container(name='posIndicator', parent=self, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, height=3, top=0, clipChildren=1)
        self.sr.posIndicatorCont = uicls.Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicatorNo = uicls.Fill(parent=self.sr.posIndicatorCont, color=(0.61, 0.05, 0.005, 1.0))
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes = uicls.Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN



    def Load(self, node):
        listentry.BaseSkillEntry.Load(self, node)
        data = node
        self.skillID = data.skillID
        for i in xrange(5):
            fill = self.sr.Get('box_%s' % i)
            fill.SetRGB(*self.whiteColor)
            if data.skill.skillLevel > i:
                fill.state = uiconst.UI_DISABLED
            else:
                fill.state = uiconst.UI_HIDDEN
            sm.StartService('ui').StopBlink(fill)

        self.sr.nameLevelLabel.text = '%s (%sx)' % (data.invtype.name, self.rank)
        self.inQueue = data.Get('inQueue', 0)
        if self.inQueue == 1:
            self.sr.levelHeader1.text = '%s %s' % (mls.UI_GENERIC_LEVEL, data.trainToLevel)
            self.sr.pointsLabel.text = ''
        else:
            self.sr.levelHeader1.text = '%s %s' % (mls.UI_GENERIC_LEVEL, data.skill.skillLevel)
            self.sr.pointsLabel.text = self.skillPointsText
        if data.trained:
            shouldNotUpdate = self.inQueue == 1 and data.skill.skillLevel + 1 != self.sr.node.trainToLevel
            if data.skill.flagID == const.flagSkillInTraining and not shouldNotUpdate:
                uthread.new(self.UpdateTraining, data.skill)
            else:
                skill = data.skill
                if skill.spHi is not None:
                    timeLeft = data.timeLeft
                    self.sr.timeLeftText.text = '%s' % util.FmtDate(long(timeLeft), 'ss')
                if shouldNotUpdate:
                    self.GetIcon('chapter')
                else:
                    self.UpdateHalfTrained()
        self.AdjustTimerContWidth()
        self.sr.levelParent.width = self.sr.levels.width + const.defaultPadding
        self.FillBoxes(data.skill.skillLevel, data.trainToLevel)
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN
        if self.inQueue == 1:
            self.sr.inTrainingHilite.state = uiconst.UI_HIDDEN
            self.UpdateBar()



    def FillBoxes(self, currentLevel, trainToLevel):
        inTraining = sm.StartService('skills').SkillInTraining()
        for i in xrange(currentLevel, 5):
            if inTraining and inTraining.typeID == self.skillID:
                if not self.inQueue:
                    if i == currentLevel:
                        self.blinking = 1
                        continue
                elif currentLevel + 1 == trainToLevel:
                    self.blinking = 1
                    continue
            box = self.sr.Get('box_%s' % i, None)
            box.state = uiconst.UI_HIDDEN
            if box and i < trainToLevel:
                box.SetRGB(*self.blueColor)
                box.state = uiconst.UI_DISABLED




    def GetMenu(self):
        m = []
        if self.rec.typeID is not None:
            m += sm.StartService('menu').GetMenuFormItemIDTypeID(None, self.rec.typeID, ignoreMarketDetails=0)
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        if self.inQueue == 1:
            if util.GetAttrs(self, 'parent', 'RemoveSkillFromQueue'):
                m.append(None)
                m.append((mls.UI_CMD_REMOVE, self.parent.RemoveSkillFromQueue, ()))
        elif util.GetAttrs(self, 'parent', 'AddSkillToQueue'):
            if util.GetAttrs(self, 'sr', 'node', 'currentLevel') < 5:
                queue = sm.StartService('skillqueue').GetQueue()
                nextLevel = sm.StartService('skillqueue').FindNextLevel(self.sr.node.skillID, self.sr.node.skill.skillLevel, queue)
                if nextLevel < 6:
                    m.append(None)
                    m.append((mls.UI_CMD_ADD, self.parent.AddSkillToQueue, ()))
        return m



    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)



    def UpdateTraining(self, skill):
        if not self or self.destroyed:
            return 
        currentPoints = listentry.BaseSkillEntry.UpdateTraining(self, skill)
        level = skill.skillLevel
        fill = self.sr.Get('box_%s' % int(level))
        fill.state = uiconst.UI_DISABLED
        if self.blinking == 1:
            sm.StartService('ui').BlinkSpriteA(fill, 1.0, time=1000.0, maxCount=0, passColor=0, minA=0.5)
        if self.inQueue == 0:
            self.OnSkillpointChange(currentPoints)
        self.UpdateHalfTrained()



    def UpdateProgress(self):
        try:
            if self.endOfTraining is None:
                self.timer = None
                return 
            skill = self.rec
            timeLeft = self.endOfTraining - blue.os.GetTime()
            if self.inQueue == 0:
                secs = timeLeft / 10000000L
                currentPoints = min(skill.spHi - secs / 60.0 * skill.spm, skill.spHi)
                self.OnSkillpointChange(currentPoints)
            else:
                self.SetTimeLeft(timeLeft)
            self.UpdateHalfTrained()
        except:
            self.timer = None
            log.LogException()
            sys.exc_clear()



    def GetDragData(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]



    def OnDropData(self, dragObj, nodes, *args):
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN
        if util.GetAttrs(self, 'parent', 'OnDropData'):
            if self.inQueue:
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)
            else:
                node = nodes[0]
                if util.GetAttrs(node, 'panel', 'inQueue'):
                    self.parent.OnDropData(dragObj, nodes)



    def OnDragEnter(self, dragObj, nodes, *args):
        if not self.inQueue or nodes is None:
            return 
        node = nodes[0]
        if hasattr(node, 'Get') and node.Get('skillID', None):
            level = None
            if util.GetAttrs(node, 'panel', '__guid__') == 'listentry.SkillEntry':
                queue = sm.StartService('skillqueue').GetQueue()
                level = sm.StartService('skillqueue').FindNextLevel(node.skillID, node.skill.skillLevel, queue)
            else:
                level = node.Get('trainToLevel', 1)
                if node.Get('inQueue', None) is None:
                    level += 1
            self.DisplayIndicator(node.skillID, level, self.sr.node.idx)
        elif node.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            category = util.GetAttrs(node, 'rec', 'categoryID')
            if category == const.categorySkill:
                typeID = util.GetAttrs(node, 'rec', 'typeID')
                if typeID is not None:
                    skill = sm.StartService('skills').GetMySkillsFromTypeID(typeID)
                    if skill:
                        self.sr.posIndicatorNo.state = uiconst.UI_DISABLED
                        return 
                    meetsReq = sm.StartService('godma').CheckSkillRequirementsForType(typeID)
                    if not meetsReq:
                        self.sr.posIndicatorNo.state = uiconst.UI_DISABLED
                        return 
                    self.sr.posIndicatorYes.state = uiconst.UI_DISABLED
        elif node.__guid__ == 'xtriui.CertSlot':
            if util.GetAttrs(node, 'rec', 'certID') is None:
                typeID = util.GetAttrs(node, 'rec', 'typeID')
                if typeID is not None:
                    mySkills = sm.StartService('skills').GetMyGodmaItem().skills
                    skill = mySkills.get(typeID, None)
                    if skill is None:
                        return 
                    skill = sm.StartService('skills').GetMySkillsFromTypeID(typeID)
                    queue = sm.StartService('skillqueue').GetQueue()
                    level = sm.StartService('skillqueue').FindNextLevel(typeID, skill.skillLevel, queue)
                    self.DisplayIndicator(typeID, level, self.sr.node.idx)



    def OnDragExit(self, *args):
        if not self.inQueue:
            return 
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN



    def DisplayIndicator(self, skillID, level, idx):
        test = sm.StartService('skillqueue').CheckCanInsertSkillAtPosition(skillID, level, idx, check=1)
        if test:
            self.sr.posIndicatorYes.state = uiconst.UI_DISABLED
        else:
            self.sr.posIndicatorNo.state = uiconst.UI_DISABLED



    def UpdateBar(self):
        uix.Flush(self.sr.bar)
        width = self.sr.node.Get('barWidth', 0)
        left = self.sr.node.Get('barLeft', 0)
        color = self.sr.node.Get('barColor', (0, 0, 0, 0))
        uicls.Fill(parent=self.sr.bar, align=uiconst.RELATIVE, color=color, left=left, top=0, width=width, height=2, state=uiconst.UI_DISABLED)
        uicls.Fill(parent=self.sr.bar, color=(0.2, 0.2, 0.2, 1), state=uiconst.UI_DISABLED)



    def GetHeight(self, *args):
        (node, width,) = args
        node.height = 36
        return node.height




