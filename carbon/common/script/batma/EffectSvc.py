import service
import GameWorld
import batma
from catma import catmaDB

class effectSvc(service.Service):
    __guid__ = 'svc.effectSvc'
    __notifyevents__ = ['OnSessionChanged']

    def GetDB(self):
        raise NotImplementedError("effectSvc doesn't implement GetDB()")



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.effectManager = GameWorld.EffectManager()
        self.effectTypeTable = GameWorld.EffectTypeTable()
        self.effectNameDict = {}
        self.catmaDataInitialized = False



    def OnSessionChanged(self, isRemote, sess, change):
        if not self.catmaDataInitialized and 'userid' in change and change['userid'][0] is None:
            self.catmaDataInitialized = True
            self.SetCatmaData(self.GetDB())



    def SetCatmaData(self, cDB):
        effectTypes = cDB.GetTypeNamesOfClass('BatmaEffect')
        self.effectDataDict = {}
        self.effectNameDict = {}
        for effectTypeName in effectTypes:
            try:
                effectType = cDB.GetType(effectTypeName)
                effectID = effectType.GetTypeID()
                attributeID = effectType.GetValue('attribute')
                effectStackingType = effectType.GetValue('effectStackingType')
                effectModifierType = effectType.GetValue('effectModifierType')
            except catmaDB.CatmaDBError as e:
                self.LogError('EffectSvc: CatmaDB error: %s from %s' % (e, effectTypeName))
                continue
            self.effectTypeTable.AddEffectTypeFromPython(effectID, attributeID, batma.EffectStackingTypeEnum[effectStackingType], batma.EffectModifierTypeEnum[effectModifierType])
            self.effectNameDict[effectTypeName] = effectID




    def GetEffectNameToIDDict(self):
        return self.effectNameDict



    def DeleteEffects(self, charID):
        self.effectManager.RemoveEffectTypeList(charID)




