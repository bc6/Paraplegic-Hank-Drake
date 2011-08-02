import blue
import collections
import geo2
import graphics
import graphicWrappers
import service
import trinity
import uthread

class LoadedLightClientComponent:
    __guid__ = 'component.LoadedLightClientComponent'


class LightClient(graphics.LightClient):
    __guid__ = 'svc.loadedLightClient'
    __componentTypes__ = ['loadedLight']

    def CreateComponent(self, name, state):
        component = LoadedLightClientComponent()
        component.resPath = state['resPath']
        component.renderObject = blue.os.LoadObject(component.resPath)
        return component




