import svc
import util

class EffectDict(dict):
    __guid__ = 'dogmax.EffectDict'

    def __init__(self, effectCompiler, *args):
        dict.__init__(self, *args)
        exec "dogma = sm.GetService('dogma')" in globals(), globals()
        self.effectCompiler = effectCompiler



    def __getitem__(self, effectID):
        try:
            return dict.__getitem__(self, effectID)
        except KeyError:
            effect = sm.GetService('clientDogmaStaticSvc').effects[effectID]
            flags = self.effectCompiler.ParseExpressionForInfluences(effect.preExpression)
            self.effectCompiler.flagsByEffect[effectID] = flags
            codez = self.effectCompiler.ParseEffect(effectID)
            d = {}
            exec 'import dogmaXP' in globals(), globals()
            exec codez in globals(), globals()
            self[effectID] = globals().get('Effect_%d' % effectID)()
            return self[effectID]




class ClientEffectCompiler(svc.baseEffectCompiler):
    __guid__ = 'svc.clientEffectCompiler'
    __startupdependencies__ = ['dogma']

    def Run(self, *args):
        self.dogma = sm.GetService('dogma')
        svc.baseEffectCompiler.Run(self, *args)
        self.effects = EffectDict(self)
        self.SetupEffects()
        self.groupsByName = util.Rowset(cfg.invgroups.header, cfg.invgroups.data.values()).Index('groupName')
        self.typesByName = util.Rowset(cfg.invtypes.header, cfg.invtypes.data.values()).Index('typeName')
        self.flagsByEffect = {}



    def GetDogmaStaticMgr(self):
        return sm.GetService('clientDogmaStaticSvc')




