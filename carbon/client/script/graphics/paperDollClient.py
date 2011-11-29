import service
import paperDoll
import collections
import GameWorld
import bluepy
import blue

class PaperDollClientComponent:
    __guid__ = 'paperDoll.PaperDollClientComponent'

    def __init__(self):
        self.doll = None
        self.typeID = None
        self.dna = None
        self.gender = None




class PaperDollClient(service.Service):
    __guid__ = 'svc.paperDollClient'
    __notifyevents__ = []
    __dependencies__ = ['cacheDirectoryLimit']
    __componentTypes__ = ['paperdoll']

    def Run(self, *etc):
        self.dollFactory = paperDoll.Factory()
        paperDoll.PerformanceOptions.EnableOptimizations()
        self.dollFactory.compressTextures = True
        self.dollFactory.allowTextureCache = not blue.win32.IsTransgaming()
        self._AppPerformanceOptions()
        self.paperDollManager = paperDoll.PaperDollManager(self.dollFactory, keyFunc=lambda doll: doll.GetName())
        self.renderAvatars = True



    def _AppPerformanceOptions(self):
        raise NotImplementedError('This needs to be implemented in application specific, derived class.')



    def CreateComponent(self, name, state):
        component = PaperDollClientComponent()
        component.gender = state.get('gender', None)
        component.dna = state.get('dna', None)
        component.typeID = state.get('typeID', None)
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['gender'] = self.GetDBGenderToPaperDollGender(component.gender)
        report['autoLOD'] = component.doll.autoLod
        report['overrideLod'] = component.doll.doll.overrideLod
        return report



    def GetDBGenderToPaperDollGender(self, gender):
        if gender:
            return paperDoll.GENDER.MALE
        return paperDoll.GENDER.FEMALE



    def SetupComponent(self, entity, component):
        trinityScene = sm.GetService('graphicClient').GetScene(entity.scene.sceneID)
        gender = self.GetDBGenderToPaperDollGender(component.gender)
        resolution = self.GetInitialTextureResolution()
        realDna = self.GetDollDNA(trinityScene, entity, gender, component.dna, component.typeID)
        if entity.entityID == session.charid:
            shouldLOD = False
            spawnAtLOD = -1
        else:
            shouldLOD = True
            spawnAtLOD = 0
        component.doll = self.SpawnDoll(trinityScene, entity, gender, realDna, shouldLOD, textureResolution=resolution, usePrepass=True, spawnAtLOD=spawnAtLOD)
        component.doll.avatar.display = self.renderAvatars
        if entity.HasComponent('animation'):
            component.doll.avatar.animationUpdater = entity.GetComponent('animation').updater
        else:
            self.LogError('Entity ' + entity + " doesn't have an animation component, so the PaperDoll component didn't load an animationUpdater!")
        component.doll.avatar.name = str(entity.entityID)



    def RegisterComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            component.callback = GameWorld.PlacementObserverWrapper(component.doll.avatar)
            positionComponent.RegisterPlacementObserverWrapper(component.callback)



    def GetPaperDollByEntityID(self, entID):
        return self.paperDollManager.GetPaperDollCharacterByKey(str(entID))



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return {'gender': component.gender,
         'dna': component.dna,
         'typeID': component.typeID}



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.gender = state.get('gender', None)
        component.dna = state.get('dna', None)
        component.typeID = state.get('typeID', None)
        return component



    def GetInitialTextureResolution(self):
        return None



    def GetDollDNA(self, scene, entity, dollGender, dollDnaInfo, typeID):
        return dollDnaInfo



    @bluepy.CCP_STATS_ZONE_METHOD
    def SpawnDoll(self, scene, entity, dollGender, dollDnaInfo, shouldLod, usePrepass = False, textureResolution = None, spawnAtLOD = 0):
        positionComponent = entity.GetComponent('position')
        if dollDnaInfo is not None:
            doll = self.paperDollManager.SpawnPaperDollCharacterFromDNA(scene, str(entity.entityID), dollDnaInfo, position=positionComponent.position, gender=dollGender, lodEnabled=shouldLod, textureResolution=textureResolution, usePrepass=usePrepass, spawnAtLOD=spawnAtLOD)
        else:
            doll = self.paperDollManager.SpawnDoll(scene, point=positionComponent.position, gender=dollGender, autoLOD=shouldLod, usePrepass=usePrepass, lod=spawnAtLOD)
        return doll



    def UnRegisterComponent(self, entity, component):
        if component.callback and entity.HasComponent('position'):
            entity.GetComponent('position').UnRegisterPlacementObserverWrapper(component.callback)
            component.callback = None



    def TearDownComponent(self, entity, component):
        component.doll.avatar.animationUpdater = None
        component.doll.avatar.worldTransformUpdater = None
        self.paperDollManager.RemovePaperDollCharacter(component.doll)
        component.doll = None



    def ToogleRenderAvatars(self):
        self.renderAvatars = not self.renderAvatars
        for doll in self.paperDollManager:
            doll.avatar.display = self.renderAvatars





