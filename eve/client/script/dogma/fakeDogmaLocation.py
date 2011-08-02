import dogmax
import sys
import weakref
import util
import string

class FakeDogmaLocation(dogmax.BaseDogmaLocation):
    __guid__ = 'dogmax.FakeDogmaLocation'

    def __init__(self, broker, locationID, locationGroup):
        dogmax.BaseDogmaLocation.__init__(self, broker)
        self.dogmaStaticMgr = sm.GetService('baseDogmaStaticSvc')
        self.godma = sm.GetService('godma')
        self.stateMgr = self.godma.GetStateManager()
        self.items = {}
        self.nextItemID = 0
        self.effectCompiler = sm.GetService('clientEffectCompiler')



    def GetChargeNonDB(self, shipID, flagID):
        for fittedItem in self.dogmaItems[shipID].GetFittedItems().itervalues():
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem.itemID




    def GetItem(self, itemID):
        try:
            return self.items[itemID]
        except KeyError:
            sys.exc_clear()
        return self.godma.GetItem(itemID)



    def CreateItem(self, typeID):
        uniqueID = self.nextItemID
        self.nextItemID += 1
        itemID = '%d_%d' % (typeID, uniqueID)
        typeObj = cfg.invtypes.Get(typeID)
        item = util.KeyVal(itemID=itemID, ownerID=None, locationID=None, flagID=None, typeID=typeID, groupID=typeObj.groupID, categoryID=typeObj.categoryID, singleton=1, stacksize=1, isOnline=1)
        self.items[itemID] = item
        return item



    def GetCharacter(self, itemID, flush):
        return self.GetItem(itemID)



    def Activate(self, itemID, effectID):
        dogmaItem = self.dogmaItems[itemID]
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = dogmax.Environment(envInfo.itemID, envInfo.charID, envInfo.shipID, envInfo.targetID, envInfo.otherID, effectID, weakref.proxy(self), None)
        env.dogmaLM = self
        self.StartEffect(effectID, itemID, env)



    def GetInstance(self, item):
        instanceRow = []
        for attributeID in self.GetAttributesByIndex().itervalues():
            instanceRow.append(getattr(item, self.dogmaStaticMgr.attributes[attributeID].attributeName, 0))

        return instanceRow



    def GetAttributesByIndex(self):
        ret = {}
        for (idx, attributeID,) in enumerate((const.attributeIsOnline,
         const.attributeDamage,
         const.attributeCharge,
         const.attributeSkillPoints,
         const.attributeArmorDamage,
         const.attributeShieldCharge,
         const.attributeIsIncapacitated)):
            ret[idx] = attributeID

        return ret



    def CheckSkillRequirements(self, charID, skillID, errorMsgName):
        skillItem = self.dogmaItems[skillID]
        skillSvc = sm.GetService('skills')
        missingSkills = {}
        for (requiredSkillTypeID, requiredSkillLevel,) in self.dogmaStaticMgr.GetRequiredSkills(skillItem.typeID).iteritems():
            requiredSkill = skillSvc.HasSkill(requiredSkillTypeID)
            if requiredSkill is None:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel
            elif self.GetAttributeValue(requiredSkill.itemID, const.attributeSkillLevel) < requiredSkillLevel:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel

        if len(missingSkills) > 0:
            skillNameList = []
            for (skillTypeID, skillLevel,) in missingSkills.iteritems():
                skillName = cfg.invtypes.Get(skillTypeID).name
                if skillLevel:
                    skillName += '%s %d' % (mls.SKILL_LEVEL, skillLevel)
                skillNameList.append(skillName)

            raise UserError(errorMsgName, {'requiredSkills': string.join(skillNameList, ', '),
             'itemName': (TYPEID, skillItem.typeID)})
        return missingSkills



    def BoardShip(self, shipID, charID):
        char = self.dogmaItems[charID]
        oldShipID = char.locationID
        charItems = char.GetFittedItems()
        for skill in charItems.itervalues():
            for effectID in skill.activeEffects.keys():
                self.StopEffect(effectID, skill.itemID)


        self.FitItemToLocation(shipID, charID, const.flagPilot)
        for skill in charItems.itervalues():
            self.StartPassiveEffects(skill.itemID, skill.typeID)




    def LoadFitting(self, fitting):
        shipItem = self.CreateItem(fitting.shipTypeID)
        self.LoadItem(shipItem.itemID, item=shipItem)
        self.LoadItem(session.charid)
        self.BoardShip(shipItem.itemID, session.charid)
        typesByFlag = {}
        for (typeID, flagID, qty,) in fitting.fitData:
            typesByFlag[flagID] = typeID

        for flags in (xrange(const.flagSubSystemSlot0, const.flagSubSystemSlot7 + 1), xrange(const.flagRigSlot0, const.flagRigSlot7), xrange(const.flagLoSlot0, const.flagHiSlot7 + 1)):
            for flagID in flags:
                try:
                    typeID = typesByFlag[flagID]
                    item = self.CreateItem(typeID)
                    self.LoadItem(item.itemID, item)
                    self.FitItemToLocation(shipItem.itemID, item.itemID, flagID)
                    del typesByFlag[flagID]
                except KeyError:
                    sys.exc_clear()


        return shipItem.itemID



    def LoadItemsInLocation(self, itemID):
        if itemID == session.charid:
            for charItem in self.godma.GetItem(itemID).skills.itervalues():
                self.LoadItem(charItem.itemID)

        elif itemID == session.shipid:
            ship = self.godma.GetItem(itemID)
            for module in ship.modules:
                self.LoadItem(module.itemID)

            for charge in ship.sublocations:
                self.LoadItem(charge.itemID)




    def GetHint(self, itemID, attributeID):
        dogmaItem = self.dogmaItems[itemID]
        modifiers = self.GetModifiersOnAttribute(itemID, attributeID, dogmaItem.locationID, dogmaItem.groupID, dogmaItem.ownerID, dogmaItem.typeID)
        baseValue = self.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.typeID, attributeID)
        GetFormatAndValue = sm.GetService('info').GetFormatAndValue
        ret = 'Base Value: %s\n' % GetFormatAndValue(cfg.dgmattribs.Get(attributeID), baseValue)
        if modifiers:
            ret += 'modified by\n'
            for (op, modifyingItemID, modifyingAttributeID,) in modifiers:
                value = self.GetAttributeValue(modifyingItemID, modifyingAttributeID)
                if op in (const.dgmAssPostMul,
                 const.dgmAssPreMul,
                 const.dgmAssPostDiv,
                 const.dgmAssPreDiv) and value == 1.0:
                    continue
                elif op in (const.dgmAssPostPercent, const.dgmAssModAdd, const.dgmAssModAdd) and value == 0.0:
                    continue
                modifyingItem = self.dogmaItems[modifyingItemID]
                modifyingAttribute = cfg.dgmattribs.Get(modifyingAttributeID)
                value = GetFormatAndValue(modifyingAttribute, value)
                ret += '  %s: %s\n' % (cfg.invtypes.Get(modifyingItem.typeID).typeName, value)

        return ret




