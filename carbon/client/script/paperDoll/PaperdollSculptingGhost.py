import paperDoll.AvatarGhost
from paperDoll import SetOrAddMap
import trinity
import math

class PaperdollSculptingGhost(paperDoll.AvatarGhost):
    __guid__ = 'PaperdollSculptingGhost.PaperdollSculptingGhost'

    def __init__(self, zonePath, texturePath, noisePath, meshFilter = [], tiling = 40, ignoreZ = False):
        self.fx = None
        self.zonePath = zonePath
        self.texturePath = texturePath
        self.noisePath = noisePath
        self.tiling = tiling
        self.ignoreZ = ignoreZ
        self.meshFilter = meshFilter
        self.isStarting = False



    def Start(self, avatar):
        if self.isStarting:
            return 
        self.isStarting = True

        def Filter(mesh):
            for f in self.meshFilter:
                if mesh.name.lower().startswith(f):
                    return True

            return False


        fxPath = 'res:/Graphics/Effect/Managed/Interior/Avatar/SculptingOverlay.fx'
        if self.ignoreZ:
            fxPath = 'res:/Graphics/Effect/Managed/Interior/Avatar/SculptingOverlay_NoZ.fx'
        self.fx = self.StartGhostRenderJob(avatar, fxPath, rjName='Sculpting Overlay', meshFilter=Filter, insertFront=False)
        for f in self.fx:
            SetOrAddMap(f, 'ZoneMap', self.zonePath)
            SetOrAddMap(f, 'HexGridMap', self.texturePath)
            SetOrAddMap(f, 'NoiseMap', self.noisePath)
            for tp in f.parameters:
                if tp.name == 'SculptingTexture':
                    tp.v1 = self.tiling
                    tp.v2 = 0.0
                    tp.v3 = 0.0
                    tp.v4 = 0.0


        mouseRed = 113
        mouseGreen = 153
        mouseBlue = 184
        mouseRed = math.pow(mouseRed / 255.0, 2.2)
        mouseGreen = math.pow(mouseGreen / 255.0, 2.2)
        mouseBlue = math.pow(mouseBlue / 255.0, 2.2)
        self.SetMouseColor((mouseRed,
         mouseGreen,
         mouseBlue,
         1.0))
        self.isStarting = False



    def Stop(self):
        self.StopGhostRenderJob()
        self.fx = None



    def IsActive(self):
        return self.fx is not None



    def SetMousePos(self, pos, radius):
        self.UpdateParam('SculptingMousePos', (pos[0],
         pos[1],
         pos[2],
         radius))



    def SetMouseColor(self, rgba):
        self.UpdateParam('SculptingMouseColor', rgba)



    def SetActiveZonePos(self, pos, radius):
        self.UpdateParam('SculptingActiveZone', (pos[0],
         pos[1],
         pos[2],
         radius))



    def SetActiveZoneColor(self, rgba):
        self.UpdateParam('SculptingZoneColor', rgba)



    def UpdateParam(self, name, value):
        if self.fx:
            for f in self.fx:
                for p in f.parameters:
                    if p.name == name:
                        p.value = value






