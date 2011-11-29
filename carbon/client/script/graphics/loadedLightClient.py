import blue
import cef
import graphics
import trinity
import util

class LoadedLightClientComponent:
    __guid__ = 'component.LoadedLightClientComponent'


class LightClient(graphics.LightClient):
    __guid__ = 'svc.loadedLightClient'
    __componentTypes__ = [cef.LoadedLightComponentView.GetComponentCodeName()]

    def CreateComponent(self, name, state):
        component = LoadedLightClientComponent()
        component.resPath = state['resPath']
        component.renderObject = blue.os.LoadObject(component.resPath)
        component.renderObject.name = self.GetName(state['_spawnID'])
        component.useBoundingBox = bool(state['useBoundingBox'])
        if component.useBoundingBox:
            component.bbPos = util.UnpackStringToTuple(state['bbPos'])
            component.bbRot = util.UnpackStringToTuple(state['bbRot'])
            component.bbScale = util.UnpackStringToTuple(state['bbScale'])
            component.renderObject.boundingBox = trinity.Tr2InteriorOrientedBoundingBox()
        return component




