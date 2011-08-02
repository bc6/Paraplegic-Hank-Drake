import service
import uiutil
import util
import uiconst
import uicls
import form
import listentry

class ElevatorWindow(uicls.Window):
    __guid__ = 'form.ElevatorWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption('Elevator Demo')
        self.MakeUnstackable()
        self.MakeUncollapseable()
        self.sr.destinationCont = uicls.Container(name='destinationCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(0, 0, 0, 0))
        self.sr.destinationScroll = uicls.Scroll(parent=self.sr.destinationCont, name='destinationScroll', id='destinationScroll1')
        self.sr.destinationScroll.multiSelect = False



    def Teleport(self, entry):
        worldspaceID = entry.sr.node.value
        elevatorManagerServer = sm.RemoteSvc('elevatorServer')
        elevatorManagerServer.TeleportPlayerToWorldspace(worldspaceID)



    def SetDestinations(self, destinations):
        destinationList = []
        for id in destinations:
            data = util.KeyVal()
            data.label = str(id)
            data.value = id
            data.OnDblClick = self.Teleport
            destinationList.append(listentry.Get('Generic', data=data))

        self.sr.destinationScroll.Load(contentList=destinationList)




class ElevatorComponent:
    __guid__ = 'components.elevator'


class ElevatorClient(service.Service):
    __guid__ = 'svc.elevatorClient'
    __displayname__ = 'elevatorClientService'
    __dependencies__ = []
    __notifyevents__ = ['OnElevatorTriggered']
    __componentTypes__ = ['elevator']

    def CreateComponent(self, name, state):
        c = components.elevator()
        c.destinations = state['destinations']
        return c



    def UnPackFromSceneTransfer(self, component, entity, state):
        component.destinations = state['destinations']
        return component



    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return self.PackUpForClientTransfer(component)



    def PackUpForClientTransfer(self, component):
        state = {}
        state['destinations'] = component.destinations
        return state



    def OnElevatorTriggered(self, elevatorID, bEntered):
        elevatorEntity = self.entityService.FindEntityByID(elevatorID)
        if elevatorEntity is not None:
            if elevatorEntity.HasComponent('elevator'):
                if bEntered:
                    wnd = sm.GetService('window').GetWindow('ElevatorWindow', create=1, decoClass=form.ElevatorWindow)
                    wnd.SetDestinations(elevatorEntity.components['elevator'].destinations)
                else:
                    wnd = sm.GetService('window').GetWindow('ElevatorWindow')
                    if wnd is not None:
                        wnd.Close()
            else:
                self.LogError('Entity has no elevator component but is receiving callbacks for it. ID', elevatorID)
        else:
            self.LogError('Entity does not exist on client. ID', elevatorID)




