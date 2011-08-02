import service

class BaseDogma(service.Service):
    __guid__ = 'svc.baseDogma'

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.restrictedStopList = []



    def AddOwnerRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedOwnerID = arg1[1][0][0]
        affectedSkillID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddOwnerRequiredSkillModifier(affectType, affectedOwnerID, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveOwnerRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedOwnerID = arg1[1][0][0]
        affectedSkillID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(affectType, affectedOwnerID, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def AddLocationRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0][0]
        affectedSkillID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddLocationRequiredSkillModifier(affectType, affectedLocationID, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def RemoveLocationRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0][0]
        affectedSkillID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveLocationRequiredSkillModifier(affectType, affectedLocationID, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def AddGangRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedSkillID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddGangRequiredSkillModifier(env.shipID, affectType, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def AddGangGroupModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedGroupID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddGangGroupModifier(env.shipID, affectType, affectedGroupID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveGangGroupModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedGroupID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddGangGroupModifier(env.shipID, affectType, affectedGroupID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveGangRequiredSkillModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedSkillID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveGangRequiredSkillModifier(env.shipID, affectType, affectedSkillID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def AddGangShipModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedAttributeID = arg1[1]
        affectType = arg1[0]
        env.dogmaLM.AddGangShipModifier(env.shipID, affectType, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveGangShipModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectingCharID = env.charID
        affectingShipID = env.shipID
        affectedAttributeID = arg1[1]
        affectType = arg1[0]
        env.dogmaLM.RemoveGangShipModifier(env.shipID, affectType, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def AddItemModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        if not arg2:
            raise RuntimeError('Expression is wrong.  AIM(%s, %s) - NULL/None value is not allowed' % (arg1, arg2))
        affectingAttributeID = arg2
        affectedModuleID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        if affectedModuleID == 0:
            return 1
        if affectedModuleID is None:
            self.LogWarn('AffectedModuleID is None.  Env:', env)
            return 
        env.dogmaLM.AddModifier(affectType, affectedModuleID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def RemoveItemModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedModuleID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveModifier(affectType, affectedModuleID, affectedAttributeID, affectingModuleID, affectingAttributeID)
        return 1



    def AddOwnerModifier(self, env, arg1, arg2):
        pass



    def AddLocationModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddLocationModifier(affectType, affectedLocationID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveLocationModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveLocationModifier(affectType, affectedLocationID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def AddLocationGroupModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0][0]
        affectedGroupID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.AddLocationGroupModifier(affectType, affectedLocationID, affectedGroupID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def RemoveLocationGroupModifier(self, env, arg1, arg2):
        affectingModuleID = env.itemID
        affectingAttributeID = arg2
        affectedLocationID = arg1[1][0][0]
        affectedGroupID = arg1[1][0][1]
        affectedAttributeID = arg1[1][1]
        affectType = arg1[0]
        env.dogmaLM.RemoveLocationGroupModifier(affectType, affectedLocationID, affectedGroupID, affectedAttributeID, affectingModuleID, affectingAttributeID)



    def SkillCheck(self, env, arg1, arg2):
        dogmaLM = env.dogmaLM
        ownerItem = dogmaLM.GetItem(env.charID)
        if ownerItem.groupID == const.groupCharacter:
            dogmaLM.CheckSkillRequirements(env.charID, env.itemID, arg1)
        return 1



    def UserError(self, env, arg1, arg2):
        dogmaLM = env.dogmaLM
        moduleID = env.itemID
        args = {'moduleName': (TYPEID, env.itemTypeID)}
        if arg1 == 'NotEnoughPower':
            args['require'] = dogmaLM.GetAttributeValue(moduleID, const.attributePower)
            shipID = env.shipID
            powerOutput = dogmaLM.GetAttributeValue(shipID, const.attributePowerOutput)
            args['remaining'] = powerOutput - dogmaLM.GetAttributeValue(shipID, const.attributePowerLoad)
            args['total'] = powerOutput
        elif arg1 == 'NotEnoughCpu':
            args['require'] = dogmaLM.GetAttributeValue(moduleID, const.attributeCpu)
            shipID = env.shipID
            cpuOutput = dogmaLM.GetAttributeValue(shipID, const.attributeCpuOutput)
            args['remaining'] = cpuOutput - dogmaLM.GetAttributeValue(shipID, const.attributeCpuLoad)
            args['total'] = cpuOutput
        raise UserError(arg1, args)




