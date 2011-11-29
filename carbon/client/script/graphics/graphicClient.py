import service
import graphicWrappers
import trinity

class GraphicClient(service.Service):
    __guid__ = 'svc.graphicClient'
    __dependencies__ = ['worldSpaceClient']

    def __init__(self):
        service.Service.__init__(self)
        self.isServiceReady = False
        self.scenes = {}



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True



    def OnLoadEntityScene(self, sceneID):
        worldSpaceTypeID = self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)
        worldSpaceRow = cfg.worldspaces.Get(worldSpaceTypeID)
        if worldSpaceRow.isInterior:
            sceneType = const.world.INTERIOR_SCENE
        else:
            sceneType = const.world.EXTERIOR_SCENE
        self.CreateScene(sceneID, sceneType)
        if sceneID == session.worldspaceid or session.worldspaceid == 0:
            self._AppSetRenderingScene(self.scenes[sceneID])



    def _AppSetRenderingScene(self, scene):
        raise NotImplementedError('Game specific versions of graphicClient must implement _AppSetRenderingScene')



    def OnEntitySceneUnloaded(self, sceneID):
        self.DestroyScene(sceneID)



    def CreateScene(self, sceneID, sceneType):
        if sceneID in self.scenes:
            raise RuntimeError('Trinity Scene Already Exists %d' % sceneID)
        if sceneType == const.world.INTERIOR_SCENE:
            self.scenes[sceneID] = trinity.Tr2InteriorScene()
        elif sceneType == const.world.EXTERIOR_SCENE:
            self.scenes[sceneID] = trinity.WodExteriorScene()
        else:
            raise RuntimeError('Trying to create a nonexistent type of scene')
        graphicWrappers.Wrap(self.scenes[sceneID], convertSceneType=False)
        if hasattr(self.scenes[sceneID], 'SetID'):
            worldSpaceTypeID = self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)
            self.scenes[sceneID].SetID(worldSpaceTypeID)



    def DestroyScene(self, sceneID):
        del self.scenes[sceneID]



    def GetScene(self, sceneID):
        if sceneID in self.scenes:
            return self.scenes[sceneID]
        else:
            return None



    def GetModelFilePath(self, graphicID):
        if prefs.ini.HasKey('noModels') and prefs.noModels.lower() == 'true':
            if self.GetGraphicType(graphicID) == 'Tr2InteriorStatic':
                return const.BAD_ASSET_STATIC
            return const.BAD_ASSET_PATH_AND_FILE
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).graphicFile



    def GetCollisionFilePath(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).collisionFile



    def GetGraphicName(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).graphicName



    def IsCollidable(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).collidable



    def GetPaperdollPresetPath(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).paperdollFile



    def GetTemplateID(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).animationTemplate



    def GetIsServiceReady(self):
        return self.isServiceReady



    def GetGraphicType(self, graphicID):
        if graphicID in cfg.graphics:
            return cfg.graphics.Get(graphicID).graphicType



    def GetBoundingBox(self, graphicID):
        graphicRow = cfg.graphics.Get(graphicID) if graphicID in cfg.graphics else None
        if graphicRow and graphicRow.graphicMinX is not None:
            return ((graphicRow.graphicMinX, graphicRow.graphicMinY, graphicRow.graphicMinZ), (graphicRow.graphicMaxX, graphicRow.graphicMaxY, graphicRow.graphicMaxZ))




