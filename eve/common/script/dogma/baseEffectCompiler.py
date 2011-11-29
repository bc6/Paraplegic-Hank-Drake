import service
import string
import cPickle
import util
import blue
import stackless
import cStringIO
import macho
import log
import dogmaXP
import bluepy

class BaseEffectCompiler(service.Service):
    __guid__ = 'svc.baseEffectCompiler'

    def __init__(self):
        service.Service.__init__(self)
        self.globs = {}



    def Run(self, *args):
        self.modifyingExpr = {}
        self.approvedModifierOperands = {const.operandCOMBINE: 2,
         const.operandAIM: 1,
         const.operandRIM: 1,
         const.operandALRSM: 1,
         const.operandRLRSM: 1,
         const.operandAGRSM: 1,
         const.operandRGRSM: 1,
         const.operandAGGM: 1,
         const.operandRGGM: 1,
         const.operandAGIM: 1,
         const.operandRGIM: 1,
         const.operandALM: 1,
         const.operandRLM: 1,
         const.operandALGM: 1,
         const.operandRLGM: 1}
        self.effects = {}
        self.globs['dogma'] = sm.services['dogma']
        self.globs['Effect'] = dogmaXP.Effect


    funcNameByID = {'ALRSM': 'AddLocationRequiredSkillModifier',
     'RLRSM': 'RemoveLocationRequiredSkillModifier',
     'ALGM': 'AddLocationGroupModifier',
     'RLGM': 'RemoveLocationGroupModifier',
     'AORSM': 'AddOwnerRequiredSkillModifier',
     'RORSM': 'RemoveOwnerRequiredSkillModifier',
     'AGRSM': 'AddGangRequiredSkillModifier',
     'RGRSM': 'RemoveGangRequiredSkillModifier',
     'AGIM': 'AddGangShipModifier',
     'RGIM': 'RemoveGangShipModifier',
     'ALM': 'AddLocationModifier',
     'RLM': 'RemoveLocationModifier'}
    evalDict = {'itemID': 'itemID',
     'shipID': 'shipID',
     'charID': 'charID',
     'otherID': 'otherID',
     'targetID': 'targetID'}

    def GetPythonForOperand(self, operand, arg1, arg2, val):
        if 'env' not in self.evalDict:

            class Env:

                def __getattr__(self, attrName):
                    return 'env.%s' % attrName



            self.evalDict['env'] = Env()
        funcName = self.funcNameByID.get(operand.operandID, None)
        if funcName is not None:
            arg1 = eval(arg1, self.evalDict)
            arg2 = eval(arg2, self.evalDict)
            if operand.operandID in (const.operandALRSM,
             const.operandRLRSM,
             const.operandALGM,
             const.operandRLGM,
             const.operandAORSM,
             const.operandRORSM):
                return 'dogmaLM.%s(%s, %s, %s, %s, itemID, %s)' % (funcName,
                 arg1[0],
                 arg1[1][0][0],
                 arg1[1][0][1],
                 arg1[1][1],
                 arg2)
            if operand.operandID in (const.operandAGRSM, const.operandRGRSM):
                return 'dogmaLM.%s(shipID, %s, %s, %s, itemID, %s)' % (funcName,
                 arg1[0],
                 arg1[1][0],
                 arg1[1][1],
                 arg2)
            if operand.operandID in (const.operandAGIM, const.operandRGIM):
                return 'dogmaLM.%s(shipID, %s, %s, itemID, %s)' % (funcName,
                 arg1[0],
                 arg1[1],
                 arg2)
            if operand.operandID in (const.operandALM, const.operandRLM):
                return 'dogmaLM.%s(%s, %s, %s, itemID, %s)' % (funcName,
                 arg1[0],
                 arg1[1][0],
                 arg1[1][1],
                 arg2)



    def SetupEffects(self):
        import dogmaXP
        for item in dogmaXP.__dict__.values():
            if hasattr(item, '__effectIDs__'):
                inst = item()
                for effectID in inst.__effectIDs__:
                    if type(effectID) is str:
                        effectName = effectID
                        effectID = getattr(const, effectName, None)
                        if effectID is None:
                            self.LogError('Namespace item', item, 'has non-existant effect name reference', effectName)
                            continue
                    self.effects[effectID] = inst

                SetGlobal(item.__guid__, 'dogma', sm.services['dogma'])




    def ParseEffect(self, effectID):
        dogmaStaticMgr = self.GetDogmaStaticMgr()
        dogma = sm.services['dogma']
        effect = dogmaStaticMgr.effects[effectID]
        ret = '########################################################################################\n# Effect: %s\n# Description: %s\n' % (effect.effectName, effect.description)
        tnum = len(dogmaStaticMgr.typesByEffect.get(effectID, []))
        if tnum == 0:
            ret += '# Note: No types have this effect.\n'
        elif tnum < 10:
            ret += '# Types with this effect:\n'
            for typeID in dogmaStaticMgr.typesByEffect[effectID]:
                ret += '#    %s (ID:%s)\n' % (cfg.invtypes.Get(typeID)._typeName, typeID)

        else:
            ret += '# %s types have this effect.\n' % tnum
        nonModifiers = 0
        preS = self.ParseExpression(cfg.dgmexpressions[effect.preExpression], '        ', topLevel=1)
        if effect.preExpression not in self.modifyingExpr:
            nonModifiers += 1
        if effect.postExpression:
            postS = self.ParseExpression(cfg.dgmexpressions[effect.postExpression], '        ', topLevel=1)
            if effect.postExpression not in self.modifyingExpr:
                nonModifiers += 1
        ret += '########################################################################################\n'
        ret += 'class Effect_%s(dogmaXP.Effect):\n' % effectID
        ret += "    __guid__ = 'dogmaXP.Effect_%s'\n" % effectID
        ret += '    __effectIDs__ = [%s]\n' % effectID
        if nonModifiers == 0:
            ret += '    __modifier_only__ = True\n'
        flags = self.flagsByEffect.get(effectID, 0)
        if flags == const.dgmExprOwner:
            ret += '    __modifies_character__ = True\n'
        elif flags == const.dgmExprShip:
            ret += '    __modifies_ship__ = True\n'
        ret += '\n'
        ret += '    ########################################################################################\n'
        ret += '    # %s: Start() (expressionID:%s)\n' % (effect.effectName, effect.postExpression)
        ret += '    def Start(self,env, dogmaLM, itemID, shipID, charID, otherID, targetID):\n'
        ret += preS
        ret += '\n\n'
        if effect.postExpression:
            ret += '    ########################################################################################\n'
            ret += '    # %s: Stop() (expressionID:%s)\n' % (effect.effectName, effect.postExpression)
            ret += '    def Stop(self,env, dogmaLM, itemID, shipID, charID, otherID, targetID):\n'
            ret += postS
            ret += '\n\n'
            ret += '    ########################################################################################\n    # %s: RestrictedStop() (expressionID: %s)\n    def RestrictedStop(self,env, dogmaLM, itemID, shipID, charID, otherID, targetID):\n' % (effect.effectName, effect.postExpression) + self.ParseExpression(cfg.dgmexpressions[effect.postExpression], '        ', restricted=1, topLevel=1)
            ret += '\n\n'
        else:
            ret += '    ########################################################################################\n    # %s has no post expression\n' % effect.effectName
            ret += '\n\n'
        return ret



    def ParseExpression(self, expression, indent = '', restricted = 0, topLevel = 0):
        typesByName = self.typesByName
        groupsByName = self.groupsByName
        dogma = sm.GetService('dogma')
        operandID = expression.operandID
        operand = dogma.operands[operandID]
        ret = None
        try:
            if restricted and operand.operandID not in dogma.restrictedStopList:
                return indent + 'pass'
            else:
                if operand.operandID in (const.operandDEFBOOL, const.operandDEFINT) and topLevel:
                    return indent + 'return ' + expression.expressionValue
                if expression.operandID == const.operandUE:
                    a1 = a2 = None
                    if expression.arg1:
                        a1 = self.ParseExpression(cfg.dgmexpressions[expression.arg1])
                    if expression.arg2:
                        a2 = self.ParseExpression(cfg.dgmexpressions[expression.arg2])
                    return indent + 'dogma.UserError(env, ' + str(a1) + ', ' + str(a2) + ')'
                if expression.operandID == const.operandDEFASSOCIATION:
                    if expression.expressionValue == '9':
                        return '9'
                    if expression.expressionValue == 'PreAssignment':
                        return str(const.dgmAssPreAssignment)
                    if expression.expressionValue == 'PostAssignment':
                        return str(const.dgmAssPostAssignment)
                elif expression.operandID == const.operandDEFENVIDX:
                    test = getattr(const, 'dgmEnv' + expression.expressionValue)
                    if test == const.dgmEnvSelf:
                        return 'itemID'
                    if test == const.dgmEnvShip:
                        return 'shipID'
                    if test == const.dgmEnvTarget:
                        return 'targetID'
                    if test == const.dgmEnvChar:
                        return 'charID'
                    if test == const.dgmEnvOther:
                        return 'otherID'
                elif expression.operandID == const.operandAIM:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    affectingAttribute = self.ParseExpression(cfg.dgmexpressions[expression.arg2])
                    affectedStuffExpression = cfg.dgmexpressions[arg1expression.arg2]
                    affectedModule = self.ParseExpression(cfg.dgmexpressions[affectedStuffExpression.arg1])
                    affectedAttribute = self.ParseExpression(cfg.dgmexpressions[affectedStuffExpression.arg2])
                    affectType = self.ParseExpression(cfg.dgmexpressions[arg1expression.arg1])
                    return indent + 'dogmaLM.AddModifier(%(aT)s, %(aM)s, %(aA)s, itemID, %(aA2)s)' % {'aT': affectType,
                     'aA': affectedAttribute,
                     'aM': affectedModule,
                     'aA2': affectingAttribute}
                if expression.operandID == const.operandRIM:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    affectingAttribute = self.ParseExpression(cfg.dgmexpressions[expression.arg2])
                    affectedStuffExpression = cfg.dgmexpressions[arg1expression.arg2]
                    affectedModule = self.ParseExpression(cfg.dgmexpressions[affectedStuffExpression.arg1])
                    affectedAttribute = self.ParseExpression(cfg.dgmexpressions[affectedStuffExpression.arg2])
                    affectType = self.ParseExpression(cfg.dgmexpressions[arg1expression.arg1])
                    return indent + 'dogmaLM.RemoveModifier(%(aT)s, %(aM)s, %(aA)s, itemID, %(aA2)s)' % {'aT': affectType,
                     'aA': affectedAttribute,
                     'aM': affectedModule,
                     'aA2': affectingAttribute}
                if expression.operandID == const.operandDEFATTRIBUTE:
                    if expression.expressionAttributeID:
                        return str(expression.expressionAttributeID)
                elif expression.operandID == const.operandDEFGROUP:
                    if expression.expressionGroupID:
                        return str(expression.expressionGroupID)
                    if expression.expressionValue:
                        groupName = expression.expressionValue.replace(' ', '')
                        groupName = 'group' + groupName[0].upper() + groupName[1:]
                        if hasattr(const, groupName):
                            return str(getattr(const, groupName))
                elif expression.operandID == const.operandDEFTYPEID:
                    if expression.expressionTypeID:
                        return str(expression.expressionTypeID)
                    if expression.expressionValue:
                        typeName = expression.expressionValue.replace(' ', '')
                        typeName = 'type' + typeName[0].upper() + typeName[1:]
                        if hasattr(const, typeName):
                            return str(getattr(const, typeName))
                if expression.operandID == const.operandIF:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    if arg1expression.operandID == const.operandRS and restricted:
                        ret = self.ParseExpression(arg2expression, restricted=restricted)
                    else:
                        ret = 'if %s:\n%s' % (self.ParseExpression(arg1expression, restricted=restricted), self.ParseExpression(arg2expression, '    ', restricted=restricted))
                elif expression.operandID == const.operandINC:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    ret = 'dogmaLM.IncreaseItemAttribute' + self.ParseExpression(arg1expression, restricted=restricted)[:-1] + ', itemID, ' + self.ParseExpression(arg2expression, restricted=restricted) + ')'
                elif expression.operandID == const.operandINCN:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    ret = 'dogmaLM.IncreaseItemAttributeEx' + self.ParseExpression(arg1expression, restricted=restricted)[:-1] + ', ' + self.ParseExpression(arg2expression, restricted=restricted) + ')'
                elif expression.operandID == const.operandDEC:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    ret = 'dogmaLM.DecreaseItemAttribute' + self.ParseExpression(arg1expression, restricted=restricted)[:-1] + ', itemID, ' + self.ParseExpression(arg2expression, restricted=restricted) + ')'
                elif expression.operandID == const.operandDECN:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    ret = 'dogmaLM.DecreaseItemAttributeEx' + self.ParseExpression(arg1expression, restricted=restricted)[:-1] + ', ' + self.ParseExpression(arg2expression, restricted=restricted) + ')'
                elif expression.operandID == const.operandSET:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    ret = 'dogmaLM.SetAttributeValue' + self.ParseExpression(arg1expression, restricted=restricted)[:-1] + ', ' + self.ParseExpression(arg2expression, restricted=restricted) + ')'
                elif expression.operandID == const.operandOR:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    if arg1expression.operandID == const.operandIF:
                        ret = self.ParseExpression(arg1expression, restricted=restricted) + '\nelse:\n' + self.ParseExpression(arg2expression, '    ', restricted=restricted)
                elif expression.operandID == const.operandAND:
                    arg1expression = cfg.dgmexpressions[expression.arg1]
                    arg2expression = cfg.dgmexpressions[expression.arg2]
                    if arg1expression.operandID == const.operandSKILLCHECK:
                        ret = self.ParseExpression(arg1expression, restricted=restricted) + '\n' + self.ParseExpression(arg2expression, restricted=restricted)
                if ret is None:
                    val = expression.expressionValue
                    if expression.arg1:
                        arg1 = self.ParseExpression(cfg.dgmexpressions[expression.arg1], restricted=restricted)
                    else:
                        arg1 = None
                    if expression.arg2:
                        arg2 = self.ParseExpression(cfg.dgmexpressions[expression.arg2], restricted=restricted)
                    else:
                        arg2 = None
                    if arg1 and '\n' not in arg1:
                        arg1 = arg1.strip()
                    if arg2 and '\n' not in arg2:
                        arg2 = arg2.strip()
                    if expression.expressionAttributeID or expression.expressionTypeID or expression.expressionGroupID:
                        return '%s' % expression.expressionAttributeID or expression.expressionTypeID or expression.expressionGroupID
                    if operand.operandID == const.operandDEFGROUP:
                        if groupsByName.has_key(expression.expressionValue):
                            return '%s' % groupsByName[expression.expressionValue].groupID
                        else:
                            if util.ConstValueExists('group' + expression.expressionValue):
                                return '%s' % util.LookupConstValue('group' + expression.expressionValue)
                            self.LogError('no such group, ', expression.expressionValue, expression.expressionID)
                            self.LogError('expression:', expression.expressionID, 'needs fixing')
                            return '-1000'
                    if operand.operandID == const.operandDEFTYPEID:
                        if typesByName.has_key(expression.expressionValue):
                            return '%s' % typesByName[expression.expressionValue].typeID
                        else:
                            self.LogError('no such type, ', expression.expressionValue, expression.expressionID)
                            self.LogError('expression:', expression.expressionID, 'needs fixing')
                            return '-10000'
                    if operand.pythonFormat == ' ':
                        raise RuntimeError('Operand %s has still not been defined' % operand.operandKey)
                    ret = self.GetPythonForOperand(operand, arg1, arg2, val)
                    if ret is None:
                        try:
                            ret = operand.pythonFormat % {'arg1': arg1,
                             'arg2': arg2,
                             'value': val}
                        except ValueError:
                            self.LogError("Operand %s's pythonFormat errored, %s" % (operand.operandID, operand.pythonFormat))
                            raise 
                retlines = ret.split('\n')
                retlines2 = []
                totalIdt = indent
                for line in retlines:
                    retlines2.append(totalIdt + line)

                ret = string.join(retlines2, '\n')
                if ret.startswith('const.'):
                    ret = str(getattr(const, ret[6:]))
                return ret

        finally:
            if not self.modifyingExpr.has_key(expression.expressionID):
                modifierRating = self.approvedModifierOperands.get(expression.operandID, 0)
                if modifierRating == 1:
                    self.modifyingExpr[expression.expressionID] = True
                elif modifierRating == 2:
                    modifiersOnly = 0
                    for sExprID in (expression.arg1, expression.arg2):
                        if sExprID:
                            sExpr = cfg.dgmexpressions[sExprID]
                            sModifierRating = self.approvedModifierOperands.get(sExpr.operandID, 0)
                            if sModifierRating == 1 or sModifierRating == 2 and self.modifyingExpr.get(sExprID, 0):
                                modifiersOnly += 1
                        else:
                            modifiersOnly += 1

                    if modifiersOnly == 2:
                        self.modifyingExpr[expression.expressionID] = True




    def PickledSortedList(self, v):
        v.sort()
        return cPickle.dumps(v)



    def IsEffectPythonOverridden(self, effectID):
        return self.effects.has_key(effectID) and not self.effects[effectID].__class__.__name__.startswith('Effect_')


    __amoconstants__ = {const.operandAIM: 1,
     const.operandAGIM: 1,
     const.operandALM: 1,
     const.operandALGM: 1,
     const.operandALRSM: 1,
     const.operandAORSM: 1,
     const.operandAGRSM: 1,
     const.operandAGGM: 1}

    def AnalyseEffectInfluences(self):
        unwantedEffects = {const.effectHiPower: True,
         const.effectLoPower: True,
         const.effectMedPower: True,
         const.effectTurretFitted: True,
         const.effectLauncherFitted: True,
         const.effectRigSlot: True}
        dogmaStaticMgr = self.GetDogmaStaticMgr()
        effects = dogmaStaticMgr.effects
        effectsByType = dogmaStaticMgr.effectsByType
        flagsByEffect = {}
        cnt = 0
        for (effectID, effect,) in effects.iteritems():
            if effect.effectCategory != const.dgmEffPassive or unwantedEffects.has_key(effectID) or flagsByEffect.has_key(effectID):
                continue
            if self.IsEffectPythonOverridden(effectID):
                continue
            preExpression = cfg.dgmexpressions[effect.preExpression]
            if preExpression.arg1 is None or preExpression.arg2 is None:
                self.LogError('Bad effect', effect.effectName, preExpression.operandKey, preExpression.arg1, preExpression.arg2)
                continue
            flagsByEffect[effectID] = self.ParseExpressionForInfluences(effect.preExpression)
            if flagsByEffect[effectID]:
                cnt += 1

        self.LogInfo('Analysed effect expression influences, found flagged entries:', cnt)
        return flagsByEffect



    def ParseExpressionForInfluences(self, expressionID):
        expression = cfg.dgmexpressions[expressionID]
        if expression.operandID == const.operandCOMBINE:
            return self.ParseExpressionForInfluences(expression.arg1) | self.ParseExpressionForInfluences(expression.arg2)
        if expression.operandID == const.operandAORSM:
            return const.dgmExprOwner
        if not self.__amoconstants__.has_key(expression.operandID):
            return const.dgmExprSkip
        if expression.operandID in [const.operandAGRSM, const.operandAGGM, const.operandAGIM]:
            return const.dgmExprShip
        lExpr1 = cfg.dgmexpressions[expression.arg1]
        if lExpr1.operandID != const.operandEFF:
            raise RuntimeError('UnexpectedInfluenceExpressionLHS', expressionID, expression.arg1)
        rExpr2 = cfg.dgmexpressions[lExpr1.arg2]
        if rExpr2.operandID != const.operandATT:
            if not (rExpr2.operandID == const.operandRSA or expression.operandID == const.operandAGIM and rExpr2.operandID == const.operandIA):
                raise RuntimeError('UnexpectedInfluence', expressionID, rExpr2.operandKey)
            return const.dgmExprSkip
        lExpr3 = cfg.dgmexpressions[rExpr2.arg1]
        if lExpr3.operandID == const.operandDEFENVIDX:
            envExprID = rExpr2.arg1
        elif lExpr3.operandID in (const.operandLS, const.operandLG, const.operandGM):
            envExprID = lExpr3.arg1
        else:
            raise RuntimeError('UnexpectedInfluenceExpressionENVIDX2', expressionID, expression.arg1, lExpr1.arg2, rExpr2.arg1)
        envExpr = cfg.dgmexpressions[envExprID]
        if envExpr.operandID != const.operandDEFENVIDX:
            raise RuntimeError('UnexpectedInfluenceExpressionENVIDX1', expressionID, expression.arg1, lExpr1.arg2, rExpr2.arg1)
        if envExprID == 3:
            return const.dgmExprOwner
        if envExprID == 4:
            return const.dgmExprShip
        return const.dgmExprSkip



    def StartEffect(self, effectID, env):
        return self.effects[effectID].Start(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)



    def PreStartEffectChecks(self, effectID, env):
        self.effects[effectID].PreStartChecks(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)



    def StartEffectChecks(self, effectID, env):
        self.effects[effectID].StartChecks(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)



    def StopEffect(self, effectID, env, restricted = 0):
        if restricted:
            return self.effects[effectID].RestrictedStop(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)
        else:
            return self.effects[effectID].Stop(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)



    def IsEffectModifierOnly(self, effectID):
        return self.effects[effectID].__modifier_only__



    def IsEffectCharacterModifier(self, effectID):
        return self.effects[effectID].__modifies_character__



    def IsEffectShipModifier(self, effectID):
        return self.effects[effectID].__modifies_ship__



    def GetDogmaStaticMgr(self):
        return sm.GetService('dogmaStaticMgr')




