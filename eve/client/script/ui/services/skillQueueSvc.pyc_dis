#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/client/script/ui/services/skillQueueSvc.py
import service
import blue
import uthread
import util
import types
import form
import skillUtil
import sys
import uix
import uiconst
import uiutil
import localization

class SkillQueueService(service.Service):
    __exportedcalls__ = {}
    __guid__ = 'svc.skillqueue'
    __servicename__ = 'skillqueue'
    __displayname__ = 'Skill Queue Client Service'
    __dependencies__ = ['godma', 'skills', 'machoNet']
    __notifyevents__ = ['OnGodmaSkillTrained',
     'OnGodmaSkillStartTraining',
     'OnGodmaSkillTrainingStopped',
     'OnSkillQueueForciblyUpdated']

    def __init__(self):
        service.Service.__init__(self)
        self.skillQueue = []
        self.serverSkillQueue = []
        self.skillQueueCache = None
        self.skillPrerequisiteAttributes = [ 'requiredSkill%d' % x for x in (1, 2, 3, 4, 5, 6) ]
        self.cachedSkillQueue = None
        self.timeCutoff = DAY

    def Run(self, memStream = None):
        self.skillQueue, freeSkillPoints = self.godma.GetSkillHandler().GetSkillQueueAndFreePoints()
        self.skillQueueCache = None
        if freeSkillPoints is not None and freeSkillPoints > 0:
            sm.GetService('skills').SetFreeSkillPoints(freeSkillPoints)

    def BeginTransaction(self):
        sendEvent = False
        if self.cachedSkillQueue is not None:
            sendEvent = True
            self.LogWarn('New skill queue transaction being opened - skill queue being overwritten!')
        self.skillQueueCache = None
        self.skillQueue, freeSkillPoints = self.godma.GetSkillHandler().GetSkillQueueAndFreePoints()
        if freeSkillPoints > 0:
            self.skills.SetFreeSkillPoints(freeSkillPoints)
        self.cachedSkillQueue = self.GetQueue()
        if sendEvent:
            sm.ScatterEvent('OnSkillQueueRefreshed')

    def RollbackTransaction(self):
        if self.cachedSkillQueue is None:
            self.LogError('Cannot rollback a skill queue transaction - no transaction was opened!')
            return
        self.skillQueue = self.cachedSkillQueue
        self.skillQueueCache = None
        self.cachedSkillQueue = None

    def CommitTransaction(self):
        if self.cachedSkillQueue is None:
            self.LogError('Cannot commit a skill queue transaction - no transaction was opened!')
            return
        self.PrimeCache(True)
        cachedQueueCache = {}
        i = 0
        for queueSkillID, queueSkillLevel in self.cachedSkillQueue:
            if queueSkillID not in cachedQueueCache:
                cachedQueueCache[queueSkillID] = {}
            cachedQueueCache[queueSkillID][queueSkillLevel] = i
            i += 1

        hasChanges = False
        for skillTypeID, skillLevel in self.cachedSkillQueue:
            if skillTypeID not in self.skillQueueCache:
                hasChanges = True
                break
            elif skillLevel not in self.skillQueueCache[skillTypeID]:
                hasChanges = True
                break

        if not hasChanges:
            for skillTypeID, skillLevel in self.skillQueue:
                position = self.skillQueueCache[skillTypeID][skillLevel]
                if skillTypeID not in cachedQueueCache:
                    hasChanges = True
                elif skillLevel not in cachedQueueCache[skillTypeID]:
                    hasChanges = True
                elif position != cachedQueueCache[skillTypeID][skillLevel]:
                    hasChanges = True
                if hasChanges:
                    break

        scatterEvent = False
        try:
            if hasChanges:
                self.TrimQueue()
                skillHandler = sm.StartService('godma').GetSkillHandler()
                skillHandler.SaveSkillQueue(self.skillQueue)
                scatterEvent = True
            elif self.skillQueue is not None and len(self.skillQueue) and sm.StartService('skills').SkillInTraining() is None:
                skillHandler = sm.StartService('godma').GetSkillHandler()
                skillHandler.CharStartTrainingSkillByTypeID(self.skillQueue[0][0])
                scatterEvent = True
        except UserError as e:
            if e.msg == 'UserAlreadyHasSkillInTraining':
                scatterEvent = True
            raise 
        finally:
            self.cachedSkillQueue = None
            if scatterEvent:
                sm.ScatterEvent('OnSkillQueueRefreshed')

    def CheckCanInsertSkillAtPosition(self, skillTypeID, skillLevel, position, check = 0):
        if position is None or position < 0 or position > len(self.skillQueue):
            raise UserError('QueueInvalidPosition')
        self.PrimeCache()
        mySkills = self.GetGodmaSkillsSet()
        ret = True
        try:
            skillObj = mySkills.get(skillTypeID, None)
            if skillObj is None:
                raise UserError('QueueSkillNotUploaded')
            if skillObj.skillLevel >= skillLevel:
                raise UserError('QueueCannotTrainPreviouslyTrainedSkills')
            if skillObj.skillLevel >= 5:
                raise UserError('QueueCannotTrainPastMaximumLevel', {'typeName': (TYPEID, skillTypeID)})
            if skillTypeID in self.skillQueueCache:
                for lvl, lvlPosition in self.skillQueueCache[skillTypeID].iteritems():
                    if lvl < skillLevel and lvlPosition >= position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')
                    elif lvl > skillLevel and lvlPosition < position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')

            else:
                godmaType = self.godma.GetType(skillTypeID)
                for attributeName in self.skillPrerequisiteAttributes:
                    attributeVal = getattr(godmaType, attributeName, None)
                    attributeLevel = getattr(godmaType, attributeName + 'Level', None)
                    if attributeVal and attributeLevel is not None:
                        skillObj = mySkills.get(attributeVal, None)
                        if skillObj is None or attributeLevel > skillObj.skillLevel:
                            raise UserError('QueuePrerequisitesNotMet', {'skill': attributeVal,
                             'level': attributeLevel})

            if position > 0:
                if self.GetTrainingLengthOfQueue(position) > self.timeCutoff:
                    raise UserError('QueueTooLong')
        except UserError as ue:
            if check and ue.msg in ('QueueTooLong', 'QueuePrerequisitesNotMet', 'QueueCannotPlaceSkillLevelsOutOfOrder', 'QueueCannotTrainPreviouslyTrainedSkills', 'QueueSkillNotUploaded'):
                sys.exc_clear()
                ret = False
            else:
                raise 

        return ret

    def AddSkillToQueue(self, skillTypeID, skillLevel, position = None):
        if self.FindInQueue(skillTypeID, skillLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        skillQueueLength = len(self.skillQueue)
        if skillQueueLength >= const.skillQueueMaxSkills:
            raise UserError('QueueTooManySkills', {'num': const.skillQueueMaxSkills})
        newPos = position if position is not None and position >= 0 else skillQueueLength
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, newPos)
        if newPos == skillQueueLength:
            self.skillQueue.append((skillTypeID, skillLevel))
            self.AddToCache(skillTypeID, skillLevel, newPos)
        else:
            if newPos > skillQueueLength:
                raise UserError('QueueInvalidPosition')
            self.skillQueueCache = None
            self.skillQueue.insert(newPos, (skillTypeID, skillLevel))
            self.TrimQueue()
        return newPos

    def RemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID in self.skillQueueCache:
            for cacheLevel in self.skillQueueCache[skillTypeID]:
                if cacheLevel > skillLevel:
                    raise UserError('QueueCannotRemoveSkillsWithHigherLevelsStillInQueue')

        self.InternalRemoveFromQueue(skillTypeID, skillLevel)

    def FindInQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return None
        if skillLevel not in self.skillQueueCache[skillTypeID]:
            return None
        return self.skillQueueCache[skillTypeID][skillLevel]

    def MoveSkillToPosition(self, skillTypeID, skillLevel, position):
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, position)
        self.PrimeCache()
        currentPosition = self.skillQueueCache[skillTypeID][skillLevel]
        if currentPosition < position:
            position -= 1
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        return self.AddSkillToQueue(skillTypeID, skillLevel, position)

    def GetQueue(self):
        return self.skillQueue[:]

    def GetServerQueue(self):
        if self.cachedSkillQueue is not None:
            return self.cachedSkillQueue[:]
        else:
            return self.GetQueue()

    def GetNumberOfSkillsInQueue(self):
        return len(self.skillQueue)

    def GetTrainingLengthOfQueue(self, position = None):
        if position is not None and position < 0:
            raise RuntimeError('Invalid queue position: ', position)
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        playerTheoreticalSkillPoints = {}
        godmaSkillSet = self.GetGodmaSkillsSet()
        currentIndex = 0
        finalIndex = position
        if finalIndex is None:
            finalIndex = len(self.skillQueue)
        for queueSkillTypeID, queueSkillLevel in self.skillQueue:
            if currentIndex >= finalIndex:
                break
            currentIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skillObj = godmaSkillSet.get(queueSkillTypeID, None)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(skillObj)
            addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(queueSkillTypeID, queueSkillLevel, playerTheoreticalSkillPoints[queueSkillTypeID], currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        return trainingTime

    def GetTrainingEndTimeOfQueue(self):
        return blue.os.GetWallclockTime() + self.GetTrainingLengthOfQueue()

    def GetTrainingLengthOfSkill(self, skillTypeID, skillLevel, position = None):
        if position is not None and (position < 0 or position > len(self.skillQueue)):
            raise RuntimeError('GetTrainingLengthOfSkill received an invalid position.')
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        currentIndex = 0
        targetIndex = position
        addedSP = 0
        addedTime = 0
        if targetIndex is None:
            targetIndex = self.FindInQueue(skillTypeID, skillLevel)
            if targetIndex is None:
                targetIndex = len(self.skillQueue)
        playerTheoreticalSkillPoints = {}
        godmaSkillSet = self.GetGodmaSkillsSet()
        for queueSkillTypeID, queueSkillLevel in self.skillQueue:
            if currentIndex >= targetIndex:
                break
            elif queueSkillTypeID == skillTypeID and queueSkillLevel == skillLevel and currentIndex < targetIndex:
                currentIndex += 1
                continue
            currentIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skillObj = godmaSkillSet.get(queueSkillTypeID, None)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(skillObj)
            addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(queueSkillTypeID, queueSkillLevel, playerTheoreticalSkillPoints[queueSkillTypeID], currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        if skillTypeID not in playerTheoreticalSkillPoints:
            skillObj = godmaSkillSet.get(skillTypeID, None)
            if skillObj is not None:
                playerTheoreticalSkillPoints[skillTypeID] = skillObj.skillPoints
            else:
                playerTheoreticalSkillPoints[skillTypeID] = 0
        addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(skillTypeID, skillLevel, playerTheoreticalSkillPoints[skillTypeID], currentAttributes)
        trainingTime += addedTime
        return (trainingTime, addedTime)

    def GetTrainingParametersOfSkillInEnvironment(self, skillTypeID, skillLevel, existingSkillPoints = 0, playerAttributeDict = None):
        skillTimeConstant = 0
        primaryAttributeID = 0
        secondaryAttributeID = 0
        playerCurrentSP = existingSkillPoints
        skillTimeConstant = self.godma.GetTypeAttribute(skillTypeID, const.attributeSkillTimeConstant)
        primaryAttributeID = self.godma.GetTypeAttribute(skillTypeID, const.attributePrimaryAttribute)
        secondaryAttributeID = self.godma.GetTypeAttribute(skillTypeID, const.attributeSecondaryAttribute)
        if existingSkillPoints is None:
            skillObj = self.GetGodmaSkillsSet().get(skillTypeID, None)
            if skillObj is not None:
                playerCurrentSP = skillObj.skillPoints
            else:
                playerCurrentSP = 0
        if skillTimeConstant is None:
            self.LogWarn('GetTrainingLengthOfSkillInEnvironment could not find skill type ID:', skillTypeID, 'via Godma')
            return 0
        skillPointsToTrain = skillUtil.GetSPForLevelRaw(skillTimeConstant, skillLevel) - playerCurrentSP
        if skillPointsToTrain <= 0:
            return (0, 0)
        attrDict = playerAttributeDict
        if attrDict is None:
            attrDict = self.GetPlayerAttributeDict()
        playerPrimaryAttribute = attrDict[primaryAttributeID]
        playerSecondaryAttribute = attrDict[secondaryAttributeID]
        if playerPrimaryAttribute <= 0 or playerSecondaryAttribute <= 0:
            raise RuntimeError('GetTrainingLengthOfSkillInEnvironment found a zero attribute value on character', session.charid, 'for attributes [', primaryAttributeID, secondaryAttributeID, ']')
        trainingRate = skillUtil.GetSkillPointsPerMinute(playerPrimaryAttribute, playerSecondaryAttribute)
        trainingTimeInMinutes = float(skillPointsToTrain) / float(trainingRate)
        return (skillPointsToTrain, trainingTimeInMinutes * MIN)

    def TrimQueue(self):
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        playerTheoreticalSkillPoints = {}
        godmaSkillSet = self.GetGodmaSkillsSet()
        cutoffIndex = 0
        for queueSkillTypeID, queueSkillLevel in self.skillQueue:
            cutoffIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skillObj = godmaSkillSet.get(queueSkillTypeID, None)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(skillObj)
            addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(queueSkillTypeID, queueSkillLevel, playerTheoreticalSkillPoints[queueSkillTypeID], currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            if trainingTime > self.timeCutoff:
                break

        if cutoffIndex < len(self.skillQueue):
            removedSkills = self.skillQueue[cutoffIndex:]
            self.skillQueue = self.skillQueue[:cutoffIndex]
            self.skillQueueCache = None
            sm.ScatterEvent('OnSkillQueueTrimmed', removedSkills)

    def GetAllTrainingLengths(self):
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        resultsDict = {}
        playerTheoreticalSkillPoints = {}
        godmaSkillSet = self.GetGodmaSkillsSet()
        for queueSkillTypeID, queueSkillLevel in self.skillQueue:
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skillObj = godmaSkillSet.get(queueSkillTypeID, None)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(skillObj)
            addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(queueSkillTypeID, queueSkillLevel, playerTheoreticalSkillPoints[queueSkillTypeID], currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            resultsDict[queueSkillTypeID, queueSkillLevel] = (trainingTime, addedTime)

        return resultsDict

    def InternalRemoveFromQueue(self, skillTypeID, skillLevel):
        skillPosition = self.FindInQueue(skillTypeID, skillLevel)
        if skillPosition is None:
            raise UserError('QueueSkillNotPresent')
        if skillPosition == len(self.skillQueue):
            del self.skillQueueCache[skillTypeID][skillLevel]
            self.skillQueue.pop()
        else:
            self.skillQueueCache = None
            self.skillQueue.pop(skillPosition)

    def ClearCache(self):
        self.skillQueueCache = None

    def AddToCache(self, skillTypeID, skillLevel, position):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            self.skillQueueCache[skillTypeID] = {}
        self.skillQueueCache[skillTypeID][skillLevel] = position

    def GetGodmaSkillsSet(self):
        return self.skills.GetMyGodmaItem().skills

    def GetPlayerAttributeDict(self):
        charItem = self.godma.GetItem(session.charid)
        attrDict = {}
        for each in charItem.displayAttributes:
            attrDict[each.attributeID] = each.value

        return attrDict

    def PrimeCache(self, force = False):
        if force:
            self.skillQueueCache = None
        if self.skillQueueCache is None:
            i = 0
            self.skillQueueCache = {}
            for queueSkillID, queueSkillLevel in self.skillQueue:
                self.AddToCache(queueSkillID, queueSkillLevel, i)
                i += 1

    def GetSkillPointsFromSkillObject(self, skillObject):
        if skillObject is None:
            return 0
        else:
            skillTrainingEnd, spHi, spm = skillObject.skillTrainingEnd, skillObject.spHi, skillObject.spm
            if skillTrainingEnd is not None and spHi is not None:
                secs = (skillTrainingEnd - blue.os.GetWallclockTime()) / SEC
                return min(spHi - secs / 60.0 * spm, spHi)
            return skillObject.skillPoints

    def OnGodmaSkillTrained(self, skillID):
        skill = sm.GetService('godma').GetItem(skillID)
        skillTypeID = skill.typeID
        level = skill.skillLevel
        if (skillTypeID, level) in self.skillQueue:
            try:
                self.InternalRemoveFromQueue(skillTypeID, level)
                sm.ScatterEvent('OnSkillFinished', skillID, skillTypeID, level)
            except UserError as ue:
                sys.exc_clear()

        if self.cachedSkillQueue and (skillTypeID, level) in self.cachedSkillQueue:
            self.cachedSkillQueue.remove((skillTypeID, level))

    def OnGodmaSkillStartTraining(self, skillID, ETA):
        skill = sm.GetService('godma').GetItem(skillID)
        level = skill.skillLevel + 1
        if (skill.typeID, level) not in self.skillQueue:
            self.AddSkillToQueue(skill.typeID, level, 0)
        else:
            self.MoveSkillToPosition(skill.typeID, level, 0)
        sm.ScatterEvent('OnSkillStarted', skill.typeID, level)

    def OnGodmaSkillTrainingStopped(self, skillID, silent):
        sm.ScatterEvent('OnSkillPaused', skillID)

    def OnSkillQueueTrimmed(self, removedSkills):
        eve.Message('skillQueueTrimmed', {'num': len(removedSkills)})

    def TrainSkillNow(self, skillID, toSkillLevel, *args):
        inTraining = sm.StartService('skills').SkillInTraining()
        if inTraining and eve.Message('ConfirmSkillTrainingNow', {'name': inTraining.type.typeName,
         'lvl': inTraining.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.BeginTransaction()
        commit = True
        try:
            if self.FindInQueue(skillID, toSkillLevel) is not None:
                self.MoveSkillToPosition(skillID, toSkillLevel, 0)
                eve.Message('SkillQueueStarted')
            else:
                self.AddSkillToQueue(skillID, toSkillLevel, 0)
                text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillID, amount=toSkillLevel)
                if inTraining:
                    eve.Message('AddedToQueue', {'skillname': text})
                else:
                    eve.Message('AddedToQueueAndStarted', {'skillname': text})
        except UserError as RuntimeError:
            commit = False
            raise 
        finally:
            if commit:
                self.CommitTransaction()
            else:
                self.RollbackTransaction()

    def AddSkillToEnd(self, skillID, current, nextLevel = None):
        queueLength = self.GetNumberOfSkillsInQueue()
        if queueLength >= const.skillQueueMaxSkills:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/SkillQueue/QueueIsFull')})
            return
        totalTime = self.GetTrainingLengthOfQueue()
        if totalTime > const.skillQueueTime:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/SkillQueue/QueueIsFull')})
            return
        if nextLevel is None:
            queue = self.GetServerQueue()
            nextLevel = self.FindNextLevel(skillID, current, queue)
        self.AddSkillToQueue(skillID, nextLevel)
        try:
            sm.StartService('godma').GetSkillHandler().AddToEndOfSkillQueue(skillID, nextLevel)
            text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillID, amount=nextLevel)
            if sm.StartService('skills').SkillInTraining():
                eve.Message('AddedToQueue', {'skillname': text})
            else:
                eve.Message('AddedToQueueAndStarted', {'skillname': text})
        except UserError:
            self.RemoveSkillFromQueue(skillID, nextLevel)
            raise 

        sm.ScatterEvent('OnSkillStarted')

    def FindNextLevel(self, skillID, current, list = None):
        if list is None:
            list = self.GetServerQueue()
        nextLevel = None
        for i in xrange(1, 7):
            if current >= i:
                continue
            inQueue = bool((skillID, i) in list)
            if inQueue is False:
                nextLevel = i
                break

        return nextLevel

    def OnSkillQueueForciblyUpdated(self):
        if self.skillQueueCache is not None:
            self.BeginTransaction()

    def IsQueueWndOpen(self):
        return form.SkillQueue.IsOpen()

    def GetAddMenuForSkillEntries(self, skill):
        m = []
        if skill is None:
            return m
        skillLevel = skill.skillLevel
        if skillLevel is not None:
            sqWnd = form.SkillQueue.GetIfOpen()
            if skillLevel < 5:
                queue = self.GetQueue()
                nextLevel = self.FindNextLevel(skill.typeID, skill.skillLevel, queue)
                if skill.flagID == const.flagSkill:
                    trainingTime, totalTime = self.GetTrainingLengthOfSkill(skill.typeID, skill.skillLevel + 1, 0)
                    takesText = ''
                    if trainingTime <= 0:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/CompletionImminent')
                    else:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/SkillTimeLeft', timeLeft=long(trainingTime))
                    if sqWnd:
                        if nextLevel < 6 and self.FindInQueue(skill.typeID, skill.skillLevel + 1) is None:
                            trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToFrontOfQueueTime', {'takes': takesText})
                            m.append((trainText, sqWnd.AddSkillsThroughOtherEntry, (skill.typeID,
                              0,
                              queue,
                              nextLevel,
                              1)))
                    else:
                        trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainNowWithTime', {'skillLevel': skill.skillLevel + 1,
                         'takes': takesText})
                        m.append((trainText, self.TrainSkillNow, (skill.typeID, skill.skillLevel + 1)))
                if nextLevel < 6:
                    if sqWnd:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToEndOfQueue', {'nextLevel': nextLevel})
                        m.append((label, sqWnd.AddSkillsThroughOtherEntry, (skill.typeID,
                          -1,
                          queue,
                          nextLevel,
                          1)))
                    else:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainAfterQueue', {'nextLevel': nextLevel})
                        m.append((label, self.AddSkillToEnd, (skill.typeID, skill.skillLevel, nextLevel)))
                if sm.GetService('skills').GetFreeSkillPoints() > 0:
                    diff = skill.spHi + 0.5 - skill.skillPoints
                    m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints'), self.UseFreeSkillPoints, (skill.typeID, diff)))
            if skill.flagID == const.flagSkillInTraining:
                m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AbortTraining'), sm.StartService('skills').AbortTrain, (skill,)))
        if m:
            m.append(None)
        return m

    def UseFreeSkillPoints(self, skillTypeID, diff):
        if sm.StartService('skills').SkillInTraining():
            eve.Message('CannotApplyFreePointsWhileQueueActive')
            return
        freeSkillPoints = sm.StartService('skills').GetFreeSkillPoints()
        text = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/UseSkillPointsWindow', skill=skillTypeID, skillPoints=int(diff))
        caption = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints')
        ret = uix.QtyPopup(maxvalue=freeSkillPoints, caption=caption, label=text)
        if ret is None:
            return
        sp = int(ret.get('qty', ''))
        currentSkillPoints = sm.GetService('skills').GetSkillPoints()
        sm.StartService('skills').ApplyFreeSkillPoints(skillTypeID, sp)