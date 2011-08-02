import service
import uthread
import safeThread
import miscUtil
import uiconst
import uicls
import log

class DebugSelectionWindow(uicls.WindowCore):
    __guid__ = 'uicls.DebugSelectionWindow'
    default_windowID = 'DebugSelectionWindow'
    ENTRY_FONTSIZE = 11
    HEADER_FONTSIZE = 12
    ENTRY_FONT = 'res:/UI/Fonts/arial.ttf'
    HEADER_FONT = 'res:/UI/Fonts/arialbd.ttf'
    ENTRY_LETTERSPACE = 1

    def ApplyAttributes(self, attributes):
        super(uicls.DebugSelectionWindow, self).ApplyAttributes(attributes)
        self.SetMinSize([40, 110])
        self.SetSize(420, 110)
        self.SetCaption('Debug Selection')
        self.sr.content.SetPadding(5, 5, 5, 5)
        self.debugSelectionClient = sm.GetService('debugSelectionClient')
        self.debugSelectionClient._SetUpdateFunc(self._UpdateSelectionEntity)
        self.displayName = uicls.Label(parent=self.sr.content, align=uiconst.TOTOP, text=' ', padding=(0, 5, 0, 5))
        topContainer = uicls.Container(parent=self.sr.content, align=uiconst.CENTER, height=25)
        bottomContainer = uicls.Container(parent=self.sr.content, align=uiconst.CENTERBOTTOM, height=25)
        width = 0
        width += uicls.ButtonCore(parent=topContainer, align=uiconst.TOLEFT, label='Select Player', padding=(2, 0, 2, 0), func=self._SelectPlayer).width
        width += uicls.ButtonCore(parent=topContainer, align=uiconst.TOLEFT, label='Select Selected', padding=(2, 0, 2, 0), func=self._SelectSelected).width
        width += uicls.ButtonCore(parent=topContainer, align=uiconst.TOLEFT, label='Clear Selection', padding=(2, 0, 2, 0), func=self._ClearSelection).width
        topContainer.width = width
        width = 0
        width += uicls.ButtonCore(parent=bottomContainer, align=uiconst.TOLEFT, label='Select Previous', padding=(2, 0, 2, 0), func=self._SelectPrevious).width
        width += uicls.ButtonCore(parent=bottomContainer, align=uiconst.TOLEFT, label='Select Next', padding=(2, 0, 2, 0), func=self._SelectNext).width
        bottomContainer.width = width
        self._UpdateSelectionEntity(self.debugSelectionClient.GetSelectedID(), ' ')



    def _UpdateSelectionEntity(self, entityID, entityName):
        if entityID is None:
            self.displayName.text = ' '
        else:
            self.displayName.text = '%s (%s)' % (entityName, entityID)



    def _ClearSelection(self, *args):
        self.debugSelectionClient.ClearSelection()



    def _SelectPlayer(self, *args):
        self.debugSelectionClient.SelectPlayer()



    def _SelectSelected(self, *args):
        self.debugSelectionClient.SelectSelected()



    def _SelectNext(self, *args):
        self.debugSelectionClient.SelectNext()



    def _SelectPrevious(self, *args):
        self.debugSelectionClient.SelectPrevious()




class debugSelectionClient(service.Service):
    __guid__ = 'svc.debugSelectionClient'
    __dependencies__ = ['entityClient']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, *args):
        service.Service.__init__(self, *args)
        self.selectedEntityID = None
        self.updateFunc = None



    def OnSessionChanged(self, isRemote, session, change):
        if 'worldspaceid' in change:
            if session.charid is not None:
                self.selectedEntityID = session.charid



    def Run(self, *args):
        service.Service.Run(self, *args)



    def _GetEntityName(self, entityID):
        return ' '



    def _SetUpdateFunc(self, func):
        self.updateFunc = func



    def _SetEntityID(self, entityID):
        oldID = self.selectedEntityID
        self.selectedEntityID = entityID
        if self.updateFunc is not None:
            self.updateFunc(self.selectedEntityID, self._GetEntityName(self.selectedEntityID))
        if oldID is not entityID:
            sm.ScatterEvent('OnDebugSelectionChanged', entityID)



    def ClearSelection(self):
        self._SetEntityID(None)



    def SelectSelected(self):
        if boot.appname == 'WOD':
            self._SetEntityID(sm.GetService('selection').GetSelectedEntID())
        else:
            self._SetEntityID(sm.GetService('selectionClient').GetSelectedEntityID())



    def SelectPlayer(self):
        entity = self.entityClient.GetPlayerEntity()
        if entity is not None:
            self._SetEntityID(entity.entityID)
        else:
            self._SetEntityID(None)



    def SelectPrevious(self):
        if self.selectedEntityID is None:
            playerEntity = self.entityClient.GetPlayerEntity()
            entityList = self.entityClient.GetEntityIdsInScene(playerEntity.scene.sceneID)
            entityID = entityList[-1]
        else:
            entity = self.GetSelectedEntity()
            entityList = self.entityClient.GetEntityIdsInScene(entity.scene.sceneID)
            try:
                index = entityList.index(self.selectedEntityID)
                listLength = len(entityList)
                entityID = entityList[((index + listLength - 1) % listLength)]
            except:
                entityID = entityList[-1]
        self._SetEntityID(entityID)



    def SelectNext(self):
        if self.selectedEntityID is None:
            playerEntity = self.entityClient.GetPlayerEntity()
            entityList = self.entityClient.GetEntityIdsInScene(playerEntity.scene.sceneID)
            entityID = entityList[0]
        else:
            entity = self.GetSelectedEntity()
            entityList = self.entityClient.GetEntityIdsInScene(entity.scene.sceneID)
            try:
                index = entityList.index(self.selectedEntityID)
                entityID = entityList[((index + 1) % len(entityList))]
            except:
                entityID = entityList[0]
        self._SetEntityID(entityID)



    def GetSelectedID(self):
        return self.selectedEntityID



    def GetSelectedEntity(self):
        return self.entityClient.FindEntityByID(self.selectedEntityID)




