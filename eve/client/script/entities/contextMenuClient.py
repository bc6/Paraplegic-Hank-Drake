import entities
import menu
import service
import uicls
import collections
import trinity
import blue

class ContextMenuClient(service.Service):
    __guid__ = 'svc.contextMenuClient'
    __componentTypes__ = ['contextMenu']

    def __init__(self):
        service.Service.__init__(self)
        self.components = {}



    def Run(self, *args):
        service.Service.Run(self, args)
        self.actionObjectClient = sm.GetService('actionObjectClientSvc')



    def CreateComponent(self, name, state):
        component = entities.ContextMenuComponent()
        return component



    def RegisterComponent(self, entity, component):
        self.components[entity.entityID] = component



    def UnRegisterComponent(self, entity, component):
        del self.components[entity.entityID]



    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        for (name, callback,) in component.menuEntries.iteritems():
            report[name] = str(callback).replace('<', '[').replace('>', ']')

        return report



    def AddMenuEntry(self, entityID, label, callback):
        self.components[entityID].AddMenuEntry(label, callback)



    def GetMenuForEntityID(self, entityID):
        m = []
        if session.role & service.ROLE_QA:
            entity = sm.GetService('entityClient').FindEntityByID(entityID)
            if not entity:
                return m
            if entity.HasComponent('info'):
                m.extend(((entity.info.name, None), None))
            QAMenu = ('GM / WM Extras', (('entityID: %s' % entityID, self.CopyEntityID, (entityID,)), ('Entity Monitor', self.ShowEntityMonitor, (entityID,)), None))
            m.append(QAMenu)
            actionList = self.actionObjectClient.GetActionList(session.charid, entityID)
            for (actionID, (label, isEnabled,),) in actionList.iteritems():
                if isEnabled:
                    args = (session.charid, entityID, actionID)
                else:
                    args = menu.DISABLED_ENTRY
                m.append((label, self.actionObjectClient.TriggerActionOnObject, args))

        return m



    def CopyEntityID(self, entityID):
        blue.pyos.SetClipboardData(str(entityID))



    def ShowEntityMonitor(self, entityID):
        if session.role & service.ROLE_QA:
            sm.GetService('window').GetWindow('EntityMonitor_%d' % entityID, create=1, maximize=1, decoClass=uicls.EntityMonitor, entID=entityID)




