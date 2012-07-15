#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/carbon/common/script/zaction/zactionLoggerSvc.py
import blue
import service
import re
import uthread
import time
import GameWorld

class ZactionLoggerService(service.Service):
    __guid__ = 'svc.zactionLoggerSvc'
    __dependencies__ = ['BaseEntityService']
    __exportedcalls__ = {'GetCombatLog': [service.ROLE_QA],
     'GetLineNumber': [service.ROLE_QA],
     'GetComboElementVersion': [service.ROLE_QA],
     'GetEntityList': [service.ROLE_QA],
     'GetCategoryList': [service.ROLE_QA]}
    __componentTypes__ = []

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.SEPERATOR = ' - '
        self.DEFAULT_COMBO_OPTION = 'All'
        self.INVALID_VALUE_DEFAULT = '0'
        self.combatLog = []
        self.combatLogEntityList = [(self.DEFAULT_COMBO_OPTION, self.DEFAULT_COMBO_OPTION)]
        self.combatLogCategoryList = [(self.DEFAULT_COMBO_OPTION, self.DEFAULT_COMBO_OPTION)]
        self.comboElementVersion = 0
        self.lineNumber = 0
        self.idToNameDict = {}
        self.entityIdentifierDict = {}
        self.attributeIdentifierDict = {}

        def _GetServices():
            if boot.role == 'client':
                self.entitySvc = sm.GetService('entityClient')
            else:
                self.entitySvc = sm.GetService('entityServer')

        uthread.new(_GetServices)
        self.RegisterIdentifierCallback('property', self._GetPropertyString)
        GameWorld.RegisterPythonActionProc('CombatLog', self.DoCombatLogLine, ('ENTID', 'ChatString', 'LogCategory'))

    def RegisterIdentifierCallback(self, identifierString, identifierCallback):
        self.attributeIdentifierDict[identifierString] = identifierCallback

    def GetNameFromID(self, entID):
        return self.INVALID_VALUE_DEFAULT

    def GetSubbedAttributeString(self, stringToSub, targetID, entID):
        self.entityIdentifierDict = {'target': targetID,
         'me': entID,
         'self': entID}

        def AttributeSubstr(name):
            nameGroup = name.group(0).strip('{}')
            parts = re.split('\\.', nameGroup)
            if parts[0] in self.attributeIdentifierDict:
                return self.attributeIdentifierDict[parts[0]](targetID, entID, parts[0], parts[1])
            else:
                self.LogError('AttributeSvc: %s : invalid attribute identifier specified: %s' % (boot.role, parts[0]))
                return self.INVALID_VALUE_DEFAULT

        regEx = '({.*?})'
        return re.sub(regEx, AttributeSubstr, stringToSub, flags=re.IGNORECASE)

    def _GetReferencedEntity(self, targetID, entID, entityReference):
        return self.entityIdentifierDict[entityReference]

    def _GetPropertyString(self, targetID, entID, preDot, postDot):
        propVal = GameWorld.GetPropertyForCurrentPythonProc(postDot)
        if propVal != None:
            if isinstance(propVal, float):
                propVal = round(propVal, 1)
            return str(propVal)
        else:
            self.LogError('zactionLoggerSvc: %s : invalid property %s referenced' % (boot.role, postDot))
            return self.INVALID_VALUE_DEFAULT

    def _GetEntityNameString(self, targetID, entID, preDot, postDot):
        entityID = self._GetReferencedEntity(targetID, entID, postDot)
        return self.GetNameFromID(entityID)

    def DoCombatLogLine(self, entID, chatString, logCategory):
        MAX_COMBAT_LOG_LENGTH = 1024
        if logCategory == None:
            logCategory = self.DEFAULT_COMBO_OPTION
        success, targetID = GameWorld.GetTargetIDForCurrentPythonProc('TargetType')
        if not success:
            return False
        subbedChat = self.GetSubbedAttributeString(chatString, targetID, entID)
        curTime = time.strftime('%X', time.gmtime())
        self.bNewElementAdded = self.UpdateLogEntityList(entID)
        if [logCategory, logCategory] not in self.combatLogCategoryList:
            self.combatLogCategoryList.append([logCategory, logCategory])
            self.comboElementVersion += 1
        subbedChat = curTime + self.SEPERATOR + subbedChat
        logLine = (subbedChat, entID, logCategory)
        self.combatLog.append(logLine)
        self.lineNumber += 1
        while len(self.combatLog) > MAX_COMBAT_LOG_LENGTH:
            self.combatLog.pop(0)

        return True

    def GetCombatLog(self, entityFilter, categoryFilter):
        messageList = []
        for entry in self.combatLog:
            logline, entityID, category = entry
            if entityFilter == self.DEFAULT_COMBO_OPTION or entityFilter == entityID:
                if categoryFilter == self.DEFAULT_COMBO_OPTION:
                    messageList.append(entry)
                elif categoryFilter == category:
                    messageList.append(entry)

        return messageList

    def UpdateLogEntityList(self, entID):
        lineCreator = self.GetDisplayNameFromID(entID)
        for entry in self.combatLogEntityList:
            comboString, comboID = entry
            if comboID == entID:
                if comboString == self.INVALID_VALUE_DEFAULT + self.SEPERATOR + str(entID):
                    entry[0] = lineCreator
                    return True
                else:
                    return False

        self.combatLogEntityList.append([lineCreator, entID])
        return True

    def GetDisplayNameFromID(self, entID):
        if entID in self.idToNameDict:
            if self.idToNameDict[entID] != self.INVALID_VALUE_DEFAULT:
                name = self.idToNameDict[entID] + self.SEPERATOR + str(entID)
                return name
        name = self.GetNameFromID(entID)
        self.idToNameDict[entID] = name
        return name + self.SEPERATOR + str(entID)

    def GetLineNumber(self):
        return self.lineNumber

    def GetComboElementVersion(self):
        return self.comboElementVersion

    def GetEntityList(self):
        return self.combatLogEntityList

    def GetCategoryList(self):
        return self.combatLogCategoryList