import service
import GameWorld
import collections
import log
import sys
import util

class BoundingVolumeService(service.Service):
    __guid__ = 'svc.boundingVolume'
    __componentTypes__ = ['boundingVolume']

    def Run(self, *args):
        service.Service.Run(self)



    def CreateComponent(self, name, state):
        c = GameWorld.BoundingVolumeComponent()
        try:
            if isinstance(state['min'], str):
                c.minExtends = util.UnpackStringToTuple(state['min'])
            else:
                c.minExtends = state['min']
            if isinstance(state['max'], str):
                c.maxExtends = util.UnpackStringToTuple(state['max'])
            else:
                c.maxExtends = state['max']
        except KeyError:
            sys.exc_clear()
        return c



    def PackUpForClientTransfer(self, component):
        return {'min': component.minExtends,
         'max': component.maxExtends}



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return self.PackUpForClientTransfer(component)



    def UnPackFromSceneTransfer(self, component, entity, state):
        try:
            component.minExtends = state['min']
            component.maxExtends = state['max']
        except KeyError:
            log.LogException()
            sys.exc_clear()
        return component



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['Min'] = ',\t\t'.join([ '%.2f' % f for f in component.minExtends ])
        report['Max'] = ',\t\t'.join([ '%.2f' % f for f in component.maxExtends ])
        return report




