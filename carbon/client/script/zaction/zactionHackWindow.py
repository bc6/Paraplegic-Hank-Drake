import base
import uicls
import uiconst
import uthread

class ZactionHackWindow(uicls.Window):
    __guid__ = 'uicls.ZactionHackWindow'
    default_width = 640
    default_height = 400
    default_windowID = 'ZactionHackWindow'
    __notifyevents__ = ['OnEntityActionStart', 'OnActionFail']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.minsize = (540, 200)
        self.zactionClient = sm.GetService('zactionClient')
        self.entityClient = sm.GetService('entityClient')
        self.playerEntID = self.entityClient.GetPlayerEntity().entityID
        self.selectedEntID = self.playerEntID
        self.entityIDs = []
        for (sceneID, scene,) in self.entityClient.scenes.iteritems():
            for (entityID, entity,) in scene.entities.iteritems():
                if entity.HasComponent('action') and entity.HasComponent('info'):
                    displayName = entity.info.name + ' - ' + str(entity.entityID)
                    self.entityIDs.append((displayName, entity.entityID, ''))


        self.currentActionID = None
        self.selected = None
        self.selectedDo = None
        self.selectedForce = None

        def OnSelectEntity(entry, label, value):
            self.selectedEntID = value
            self.availableActions.LoadContent(contentList=self._GetAvailableActions(), keepPosition=True)


        self.curActionLabel = uicls.LabelCore(parent=self.sr.content, align=uiconst.TOTOP, text='Current action:', pos=(0, 0, 0, 0), padding=(5, 5, 5, 5))
        maincontainer = uicls.Container(parent=self.sr.content, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.entityDropdown = uicls.Combo(parent=maincontainer, options=self.entityIDs, select=self.playerEntID, name='entitySelect', callback=OnSelectEntity, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
        splitcontainer = uicls.Container(parent=maincontainer, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        rightcontainer = uicls.Container(parent=splitcontainer, align=uiconst.TORIGHT, pos=(0, 0, 250, 0), padding=(5, 5, 5, 5))
        leftcontainer = uicls.Container(parent=splitcontainer, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(5, 5, 5, 5))
        uicls.LabelCore(parent=leftcontainer, align=uiconst.TOTOP, text='Available Actions:', pos=(0, 0, 0, 0), padding=(5, 5, 5, 5))
        self.buttonContainer = uicls.Container(parent=leftcontainer, align=uiconst.TOBOTTOM, pos=(0, 0, 8, 8), padding=(5, 5, 5, 5))
        self.availableActions = uicls.Scroll(parent=leftcontainer, name='zactionScroll', align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.availableActions.LoadContent(contentList=self._GetAvailableActions(), keepPosition=True)
        self.startButton = uicls.Button(parent=self.buttonContainer, align=uiconst.CENTER, label='Do Action!', func=self.DoAction, pos=(0, 0, 0, 0))
        uicls.LabelCore(parent=rightcontainer, align=uiconst.TOTOP, text='All Actions:', pos=(0, 0, 0, 0), padding=(5, 5, 5, 5))
        self.rightButtonContainer = uicls.Container(parent=rightcontainer, align=uiconst.TOBOTTOM, pos=(0, 0, 8, 8), padding=(5, 5, 5, 5))
        self.allActions = uicls.Scroll(parent=rightcontainer, name='allActionScroll', align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.allActions.LoadContent(contentList=self._GetAllActions(), keepPosition=True)
        self.forceButton = uicls.Button(parent=self.rightButtonContainer, align=uiconst.CENTER, label='Force Action!', func=self.ForceAction, pos=(0, 0, 0, 0))
        sm.RegisterNotify(self)
        self.sr.updateTimer = base.AutoTimer(100, self._UpdateCurrentAction)



    def _OnClose(self, *args):
        uicls.Window._OnClose(self, *args)
        self.sr.updateTimer = None



    def _GetAvailableActions(self):
        contentList = []
        actionTreeInstance = self.zactionClient.GetActionTree().GetTreeInstanceByEntID(self.selectedEntID)
        if not actionTreeInstance:
            return contentList
        availableActions = actionTreeInstance.GetAvailableActionsList(self.zactionClient.GetClientProperties())
        for (actionID, isSibling, isActive, canRequest,) in availableActions:
            actionNode = self.zactionClient.GetActionTree().GetTreeNodeByID(actionID)
            actionLabel = '%s(%d)' % (actionNode.name, actionNode.ID)
            data = {'text': actionLabel,
             'label': actionLabel,
             'id': actionID,
             'actionID': actionID,
             'isActive': isActive,
             'isSibling': isSibling,
             'canRequest': canRequest,
             'showicon': 'hide',
             'showlen': False,
             'openByDefault': False,
             'hideNoItem': True,
             'disableToggle': True,
             'OnClick': self.SelectDoAction,
             'OnDblClick': self.SelectDoAction}
            contentList.append(uicls.ScrollEntryNode(**data))

        contentList.sort(lambda x, y: cmp(x.text, y.text))
        return contentList



    def _GetAllActions(self):
        contentList = []
        allActions = self.zactionClient.GetActionTree().GetAllTreeNodesList()
        for actionNode in allActions:
            if actionNode.actionType != const.ztree.NODE_FOLDER:
                actionLabel = '%s(%d)' % (actionNode.name, actionNode.ID)
                data = {'text': actionLabel,
                 'label': actionLabel,
                 'id': actionNode.ID,
                 'actionID': actionNode.ID,
                 'showicon': 'hide',
                 'showlen': False,
                 'openByDefault': False,
                 'hideNoItem': True,
                 'disableToggle': True,
                 'OnClick': self.SelectForceAction,
                 'OnDblClick': self.SelectForceAction}
                contentList.append(uicls.ScrollEntryNode(**data))

        contentList.sort(lambda x, y: cmp(x.text, y.text))
        return contentList



    def GetDoActionProperties(self):
        if self.selectedEntID == self.playerEntID:
            properties = self.zactionClient.GetClientProperties()
        else:
            properties = {'TargetList': [int(self.playerEntID)]}
        return properties



    def ReloadAvailableActions(self):
        self.availableActions.LoadContent(contentList=self._GetAvailableActions(), keepPosition=True)



    def SelectDoAction(self, scrollEntry):
        self.selectedDo = scrollEntry.sr.node.actionID



    def SelectForceAction(self, scrollEntry):
        self.selectedForce = scrollEntry.sr.node.actionID



    def DoAction(self, *args):
        if self.selectedDo:
            self.zactionClient.StartAction(self.selectedEntID, self.selectedDo, clientProps=self.GetDoActionProperties())



    def ForceAction(self, *args):
        if self.selectedForce:
            self.zactionClient.QA_RequestForceAction(self.selectedEntID, self.selectedForce)



    def OnEntityActionStart(self, entID, actionID, actionStack, propList):
        if self.selectedEntID == entID:
            uthread.new(self.ReloadAvailableActions)



    def OnActionFail(self, entID, actionID, actionStack, proplist):
        if self.selectedEntID == entID:
            uthread.new(self.ReloadAvailableActions)



    def _UpdateCurrentAction(self):
        actionTreeInstance = self.zactionClient.GetActionTree().GetTreeInstanceByEntID(self.selectedEntID)
        if not actionTreeInstance:
            return 
        actionTreeNode = actionTreeInstance.GetCurrentTreeNode()
        if actionTreeNode:
            if actionTreeInstance.debugItem:
                self.curActionLabel.SetText('Current Action: %s  duration: %f' % (actionTreeNode.name, actionTreeInstance.debugItem.duration))
            else:
                self.curActionLabel.SetText('Current Action: %s' % actionTreeNode.name)
            if self.currentActionID != actionTreeNode.ID:
                self.ReloadAvailableActions()
                self.currentActionID = actionTreeNode.ID
        availableActions = actionTreeInstance.GetAvailableActionsList(self.GetDoActionProperties())
        activeDict = {}
        for (id, isSibling, isActive, canRequest,) in availableActions:
            activeDict[id] = (isActive, canRequest)

        for node in self.availableActions.GetNodes():
            if node.id in activeDict:
                label = node.text
                node.disabled = False
                if not activeDict[node.id][1]:
                    label = label + ' (internal)'
                    node.disabled = True
                if not activeDict[node.id][0]:
                    label = label + ' (inactive)'
                    node.disabled = True
                node.label = label
                if node.panel:
                    if node.disabled:
                        node.panel.opacity = 0.5
                        node.panel.state = uiconst.UI_DISABLED
                    else:
                        node.panel.opacity = 1.0
                        node.panel.state = uiconst.UI_NORMAL
                    node.panel.sr.label.text = label
                    node.panel.Show()
            else:
                self.ReloadAvailableActions()
                return 





