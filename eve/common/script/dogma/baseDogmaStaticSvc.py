import service
import util
import bluepy

class BaseDogmaStaticSvc(service.Service):
    __guid__ = 'svc.baseDogmaStaticSvc'

    def __init__(self):
        service.Service.__init__(self)
        self.attributes = {}
        self.attributesByName = {}
        self.attributesByTypeAttribute = {}
        self.effects = {}
        self.requiredSkills = {}
        self.unwantedEffects = {const.effectHiPower: True,
         const.effectLoPower: True,
         const.effectMedPower: True,
         const.effectSkillEffect: True}



    def Run(self, *args):
        self.Load()



    def Load(self):
        with bluepy.Timer('LoadTypeEffects'):
            self.LoadAttributes()
        typeAttributes = []
        for row in cfg.dgmtypeattribs.itervalues():
            typeAttributes.extend(row)

        with bluepy.Timer('LoadTypeAttributes'):
            self.LoadTypeAttributes(typeAttributes)
        with bluepy.Timer('LoadEffects'):
            self.LoadEffects()
        typeEffects = []
        for row in cfg.dgmtypeeffects.itervalues():
            typeEffects.extend(row)

        with bluepy.Timer('LoadTypeEffects'):
            self.LoadTypeEffects(typeEffects, True)
        self.crystalGroupIDs = cfg.GetCrystalGroups()
        self.controlBunkersByFactionID = {}
        for typeObj in cfg.typesByGroups.get(const.groupControlBunker, []):
            typeID = typeObj.typeID
            factionID = int(self.GetTypeAttribute2(typeID, const.attributeFactionID))
            self.controlBunkersByFactionID[factionID] = typeID

        import re
        cgre = re.compile('chargeGroup\\d{1,2}')
        cgattrs = tuple([ a.attributeID for a in cfg.dgmattribs if cgre.match(a.attributeName) is not None ])
        self.crystalModuleGroupIDs = {}
        for groupID in (const.categoryModule, const.categoryStructure):
            for groupOb in cfg.groupsByCategories.get(groupID, []):
                if groupOb.groupID in cfg.typesByGroups:
                    typeOb = cfg.typesByGroups[groupOb.groupID][0]
                    for attributeID in cgattrs:
                        v = self.GetTypeAttribute(typeOb.typeID, attributeID)
                        if v is not None and v in self.crystalGroupIDs:
                            self.crystalModuleGroupIDs[groupOb.groupID] = True
                            break






    def LoadAttributes(self):
        self.attributes = util.IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeID',))
        self.attributesByName = util.IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeName',))
        self.attributesByCategory = util.IndexedRowLists(cfg.dgmattribs.data.itervalues(), ('attributeCategory',))
        chargedAttributes = []
        for att in self.attributes.itervalues():
            if att.chargeRechargeTimeID and att.attributeCategory != 8:
                chargedAttributes.append(att)

        self.chargedAttributes = util.IndexedRows(chargedAttributes, ('attributeID',))
        self.attributesRechargedByAttribute = util.IndexedRowLists(chargedAttributes, ('chargeRechargeTimeID',))
        self.attributesCappedByAttribute = util.IndexedRowLists(chargedAttributes, ('maxAttributeID',))
        self.attributesByIdx = {}
        self.idxByAttribute = {}
        self.canFitShipGroupAttributes = []
        for att in self.attributesByCategory[const.dgmAttrCatGroup]:
            if att.attributeName.startswith('canFitShipGroup'):
                self.canFitShipGroupAttributes.append(att.attributeID)

        self.canFitShipTypeAttributes = []
        self.requiresSovUpgrade = []
        self.requiredSkillAttributes = {}
        for att in self.attributesByCategory[const.dgmAttrCatType]:
            if att.attributeName.startswith('canFitShipType'):
                self.canFitShipTypeAttributes.append(att.attributeID)
            elif att.attributeName.startswith('anchoringRequiresSovUpgrade'):
                self.requiresSovUpgrade.append(att.attributeID)
            elif att.attributeName.startswith('requiredSkill'):
                levelAttribute = self.attributesByName[(att.attributeName + 'Level')]
                self.requiredSkillAttributes[att.attributeID] = levelAttribute.attributeID

        self.shipHardwareModifierAttribs = [(const.attributeHiSlots, const.attributeHiSlotModifier),
         (const.attributeMedSlots, const.attributeMedSlotModifier),
         (const.attributeLowSlots, const.attributeLowSlotModifier),
         (const.attributeTurretSlotsLeft, const.attributeTurretHardpointModifier),
         (const.attributeLauncherSlotsLeft, const.attributeLauncherHardPointModifier)]



    def LoadEffects(self):
        self.effects = util.IndexedRows(cfg.dgmeffects.data.itervalues(), ('effectID',))
        self.effectsByName = util.IndexedRows(cfg.dgmeffects.data.itervalues(), ('effectName',))



    def LoadTypeEffects(self, rs, run):
        self.effectsByType = util.IndexedRows(rs, ('typeID', 'effectID'))
        self.passiveFilteredEffectsByType = {}
        for typeID in self.effectsByType.iterkeys():
            passiveEffects = []
            for effectID in self.effectsByType[typeID].iterkeys():
                if self.unwantedEffects.has_key(effectID):
                    continue
                effect = self.effects[effectID]
                if effect.effectCategory in [const.dgmEffPassive, const.dgmEffSystem]:
                    passiveEffects.append(effectID)

            if len(passiveEffects):
                self.passiveFilteredEffectsByType[typeID] = passiveEffects

        self.typesByEffect = util.IndexedRows(rs, ('effectID', 'typeID'))
        etec = {}
        defaultEffect = {}
        if len(rs) > 0:
            defaults = util.IndexedRowLists(rs, ('isDefault',))
            for eff in defaults[1]:
                defaultEffect[eff.typeID] = eff.effectID

        else:
            self.LogError('STATIC DATA MISSING: Dogma Type Effects')
        self.defaultEffectByType = defaultEffect



    def LoadTypeAttributes(self, rs):
        self.typesByAttribute = util.IndexedRows(rs, ('attributeID', 'typeID'))
        attRS = util.IndexedRowLists(rs, ('typeID',))
        vals = {}
        for typeID in attRS.iterkeys():
            v = {}
            for attribute in attRS[typeID]:
                v[attribute.attributeID] = attribute.value

            vals[typeID] = v

        atts9 = self.attributesByCategory.get(9, [])
        for typeID in vals.iterkeys():
            v = vals[typeID]
            invtype = cfg.invtypes.GetIfExists(typeID)
            if invtype:
                for attribute in atts9:
                    if attribute.attributeID != 195:
                        v[attribute.attributeID] = getattr(invtype, attribute.attributeName)


        for attributeID1 in self.attributesRechargedByAttribute.iterkeys():
            if self.typesByAttribute.has_key(attributeID1):
                for typeID in self.typesByAttribute[attributeID1].iterkeys():
                    for row1 in self.attributesRechargedByAttribute[attributeID1]:
                        vals[typeID][row1.attributeID] = 0.0



        self.attributesByTypeAttribute.update(vals)



    def GetTypeAttribute(self, typeID, attributeID, defaultValue = None):
        try:
            return self.attributesByTypeAttribute[typeID][attributeID]
        except KeyError:
            return defaultValue



    def GetTypeAttribute2(self, typeID, attributeID):
        try:
            return self.attributesByTypeAttribute[typeID][attributeID]
        except KeyError:
            return self.attributes[attributeID].defaultValue



    def GetRequiredSkills(self, typeID):
        if typeID in self.requiredSkills:
            return self.requiredSkills[typeID]
        ret = {}
        for (attributeID, levelAttributeID,) in self.requiredSkillAttributes.iteritems():
            requiredSkill = self.GetTypeAttribute(typeID, attributeID)
            requiredLevel = self.GetTypeAttribute2(typeID, levelAttributeID)
            if requiredSkill is not None and requiredSkill not in ret:
                ret[int(requiredSkill)] = int(requiredLevel)

        self.requiredSkills[typeID] = ret
        return ret



    def GetEffectTypes(self):
        return self.effects



    def GetEffectType(self, effectID):
        return self.effects[effectID]



    def GetAttributeType(self, attributeID):
        if isinstance(attributeID, str):
            return self.attributesByName[attributeID]
        return self.attributes[attributeID]



    def GetAttributeByName(self, attributeName):
        ret = self.attributesByName[attributeName]
        return ret.attributeID



    def TypeHasAttribute(self, typeID, attributeID):
        return typeID in self.attributesByTypeAttribute and attributeID in self.attributesByTypeAttribute[typeID]



    def TypeGetOrderedEffectIDs(self, typeID, categoryID = None):
        return self.effectsByType[typeID].iterkeys()



    def TypeGetEffects(self, typeID):
        return self.effectsByType.get(typeID, {})



    def TypeExists(self, typeID):
        return typeID in self.attributesByTypeAttribute



    def TypeHasEffect(self, typeID, effectID):
        return self.effectsByType.has_key(typeID) and self.effectsByType[typeID].has_key(effectID)



    def GetAttributesByCategory(self, categoryID):
        return self.attributesByCategory.get(categoryID, [])



    def EffectGetTypes(self, effectID):
        return self.typesByEffect.get(effectID, {})



    def AttributeGetTypes(self, attributeID):
        return self.typesByAttribute.get(attributeID, {})



    def GetCanFitShipGroups(self, typeID):
        import sys
        rtn = []
        for att in self.canFitShipGroupAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn



    def GetCanFitShipTypes(self, typeID):
        import sys
        rtn = []
        for att in self.canFitShipTypeAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn



    def GetDefaultEffect(self, typeID):
        return self.defaultEffectByType[typeID]



    def GetShipHardwareModifierAttribs(self):
        return self.shipHardwareModifierAttribs




