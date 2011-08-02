import blue
import util
import uthread
import uicls
import uiutil
import const
import sys
import uiconst

class EntityBrowserCore(uicls.WindowCore):
    __guid__ = 'uicls.EntityBrowserCore'
    default_windowID = 'entityBrowser'

    def ApplyAttributes(self, attributes):
        super(uicls.EntityBrowserCore, self).ApplyAttributes(attributes)
        self.entityClient = sm.GetService('entityClient')
        self.SetMinSize([100, 200])
        self.SetHeight(200)
        self.SetCaption('Entity Browser')
        self.sr.content.SetPadding(5, 5, 5, 5)
        self.sr.content.searchEntryLabel = uicls.LabelCore(parent=self.sr.content, align=uiconst.TOPLEFT, text='Entity ID:  ')
        self.sr.content.searchEntry = uicls.SinglelineEditCore(parent=self.sr.content, align=uiconst.TOPLEFT, left=self.sr.content.searchEntryLabel.width + 10, width=200)
        self.sr.content.searchButton = uicls.ButtonCore(parent=self.sr.content, align=uiconst.TOPLEFT, left=self.sr.content.searchEntry.left + self.sr.content.searchEntry.width + 20, label='View Entity', func=self.ViewEntityButtonFunc)
        self.sr.content.filterEntryLabel = uicls.LabelCore(parent=self.sr.content, align=uiconst.TOPLEFT, top=25, text='Component Filters:  ')
        self.sr.content.filterEntry = uicls.SinglelineEditCore(parent=self.sr.content, align=uiconst.TOPLEFT, hinttext='Comma separated component names', OnReturn=self.FilterEntitiesFunc, left=self.sr.content.filterEntryLabel.width + 10, top=25, width=300)
        self.sr.content.filterButton = uicls.ButtonCore(parent=self.sr.content, align=uiconst.TOPLEFT, left=self.sr.content.filterEntry.left + self.sr.content.filterEntry.width + 20, top=25, label='Filter Entities', func=self.FilterEntitiesFunc)
        self.sceneNodes = {}
        self.sceneDataNodes = {}
        self.componentFilters = []
        self.sr.content.scroll = uicls.ScrollCore(parent=self.sr.content, top=55)
        self.thread = uthread.new(self.LoadScenesThread)



    def LoadScenesThread(self):
        while not self.dead:
            self.LoadScenes()
            blue.pyos.synchro.Sleep(1000)




    def LoadScenes(self, forceUpdate = False):
        newScenes = self.entityClient.scenes.iteritems()
        requiresUpdate = False
        if forceUpdate or len(set(self.sceneNodes.keys()) - set(self.entityClient.scenes.keys())) != 0:
            self.sceneNodes = {}
        for (sceneID, scene,) in newScenes:
            if sceneID not in self.sceneNodes:
                requiresUpdate = True
                name = self.GetSceneName(sceneID)
                data = {'decoClass': uicls.SE_EntityBrowserGroup,
                 'GetSubContent': self.GetSceneListEntries,
                 'label': '%d<t>%s (%s)' % (sceneID, name, len(scene.entities)),
                 'id': ('scene', sceneID),
                 'state': 'locked',
                 'showlen': False,
                 'scene': scene}
                node = uicls.ScrollEntryNode(**data)
                self.sceneNodes[sceneID] = node
            if sceneID in self.sceneDataNodes:
                if len(scene.entities) != len(self.sceneDataNodes[sceneID]):
                    requiresUpdate = True
                else:
                    for entityID in scene.entities:
                        if entityID not in self.sceneDataNodes[sceneID]:
                            requiresUpdate = True
                            break


        if requiresUpdate or forceUpdate:
            self.sr.content.scroll.LoadContent(contentList=self.sceneNodes.values(), headers=['ID', 'Name', 'State'])



    def GetSceneName(self, sceneID):
        return 'Scene Name'



    def GetEntityName(self, entity):
        return 'Entity Name'



    def GetSceneListEntries(self, data, *args):
        scene = data['scene']
        self.sceneDataNodes[scene.sceneID] = {}
        for (entityID, entity,) in scene.entities.iteritems():
            for componentName in self.componentFilters:
                if not entity.HasComponent(componentName):
                    break
            else:
                name = self.GetEntityName(entity)
                data = {'decoClass': uicls.SE_EntityBrowserEntry,
                 'label': '%s<t>%s<t>%s' % (entityID, name, const.cef.ENTITY_STATE_NAMES[entity.state]),
                 'entityID': entityID,
                 'OnDblClick': self.DblClickEntry}
                node = uicls.ScrollEntryNode(**data)
                self.sceneDataNodes[scene.sceneID][entityID] = node


        return self.sceneDataNodes[scene.sceneID].values()



    def DblClickEntry(self, entry):
        entityID = util.GetAttrs(entry, 'sr', 'node', 'entityID')
        self.ViewEntity(entityID)



    def ViewEntityButtonFunc(self, buttonObj):
        entID = self.sr.content.searchEntry.GetValue()
        self.ViewEntity(int(entID))



    def ViewEntity(self, entID):
        entity = self.entityClient.FindEntityByID(entID)
        uicls.EntityMonitor(parent=uicore.layer.main, entID=entID)



    def FilterEntitiesFunc(self, *args):
        oldFilters = self.componentFilters[:]
        self.componentFilters = []
        filters = self.sr.content.filterEntry.GetText()
        for part in filters.split(','):
            componentName = part.strip()
            if componentName:
                self.componentFilters.append(componentName)

        if self.componentFilters != oldFilters:
            self.LoadScenes(forceUpdate=True)




class EntityMonitor(uicls.WindowCore):
    __guid__ = 'uicls.EntityMonitor'
    default_windowID = 'entityMonitor'

    def ApplyAttributes(self, attributes):
        super(uicls.EntityMonitor, self).ApplyAttributes(attributes)
        self.SetMinSize([300, 200])
        self.SetHeight(200)
        self.entityID = attributes.get('entID', 0)
        self.SetCaption('Entity Monitor for %d' % self.entityID)
        self.entityClient = sm.GetService('entityClient')
        self.sr.content.scroll = uicls.ScrollCore(parent=self.sr.content, padding=(5, 5, 5, 5))
        self.componentNodes = {}
        self.componentDataNodes = {}
        clientNodeData = {'decoClass': uicls.SE_ListGroupCore,
         'GetSubContent': self.GetClientNodes,
         'label': 'Client',
         'id': ('location', 'Client'),
         'showicon': 'hide',
         'showlen': False,
         'state': 'locked'}
        self.clientNode = uicls.ScrollEntryNode(**clientNodeData)
        serverNodeData = {'decoClass': uicls.SE_ListGroupCore,
         'GetSubContent': self.GetServerNodes,
         'label': 'Server',
         'id': ('location', 'Server'),
         'showicon': 'hide',
         'showlen': False,
         'state': 'locked'}
        self.serverNode = uicls.ScrollEntryNode(**serverNodeData)
        self.thread = uthread.new(self.LoadEntityThread)



    def LoadEntityThread(self):
        while not self.dead:
            self.LoadEntity()
            blue.pyos.synchro.Sleep(250)




    def LoadEntity(self):
        entity = self.entityClient.FindEntityByID(self.entityID)
        if not entity:
            self.SetCaption('Entity Monitor for %d (NOT FOUND)' % self.entityID)
            self.componentNodes = {}
            self.componentDataNodes = {}
            self.sr.content.scroll.LoadContent(contentList=[])
            return 
        newComponents = entity.components.keys()
        requiresUpdate = False
        for componentName in newComponents:
            locations = ['client']
            if not self.entityClient.IsClientSideOnly(entity.scene.sceneID):
                locations.append('server')
            for location in locations:
                nodeName = '%s - %s' % (componentName, location.upper())
                if nodeName not in self.componentNodes:
                    requiresUpdate = True
                    data = {'decoClass': uicls.SE_ListGroupCore,
                     'GetSubContent': self.GetComponentListEntries,
                     'label': componentName,
                     'id': ('component', nodeName),
                     'showicon': 'hide',
                     'showlen': False,
                     'componentName': componentName,
                     'location': location,
                     'sublevel': 1,
                     'state': 'locked'}
                    node = uicls.ScrollEntryNode(**data)
                    self.componentNodes[nodeName] = node
                if nodeName in self.componentDataNodes:
                    if location == 'client':
                        state = self.entityClient.GetComponentStateByID(self.entityID, componentName)
                    elif location == 'server' and not self.entityClient.IsClientSideOnly(entity.scene.sceneID):
                        state = self.entityClient.ServerReportState(self.entityID, componentName)
                    if state:
                        for (name, value,) in state.iteritems():
                            label = '%s<t>%s' % (name, value)
                            if name in self.componentDataNodes[nodeName]:
                                if self.componentDataNodes[nodeName][name].panel:
                                    self.componentDataNodes[nodeName][name].panel.sr.label.SetText(label)



        if requiresUpdate:
            self.sr.content.scroll.LoadContent(contentList=[self.clientNode, self.serverNode], headers=['name', 'value'])



    def GetClientNodes(self, data, *args):
        clientNodes = []
        for node in self.componentNodes:
            if 'CLIENT' in node:
                clientNodes.append(self.componentNodes[node])

        return clientNodes



    def GetServerNodes(self, data, *args):
        serverNodes = []
        for node in self.componentNodes:
            if 'SERVER' in node:
                serverNodes.append(self.componentNodes[node])

        return serverNodes



    def GetComponentListEntries(self, data, *args):
        componentName = data['componentName']
        location = data['location']
        nodeName = '%s - %s' % (componentName, location.upper())
        self.componentDataNodes[nodeName] = {}
        if location == 'client':
            state = self.entityClient.GetComponentStateByID(self.entityID, componentName)
        elif location == 'server':
            state = self.entityClient.ServerReportState(self.entityID, componentName)
        if state:
            for (name, value,) in state.iteritems():
                data = {'label': '%s<t>%s' % (name, value),
                 'sublevel': 1,
                 'id': (nodeName, name)}
                node = uicls.ScrollEntryNode(**data)
                self.componentDataNodes[nodeName][name] = node

        return self.componentDataNodes[nodeName].values()




class SE_EntityBrowserGroup(uicls.SE_ListGroupCore):
    __guid__ = 'uicls.SE_EntityBrowserGroup'

    def GetMenu(self):
        menu = super(uicls.SE_EntityBrowserGroup, self).GetMenu()
        if not self.sr.node.get('showmenu', True):
            return menu

        def CopyID(id):
            blue.pyos.SetClipboardData(str(id))


        menu += [('Copy Scene ID', CopyID, (self.sr.node.get('id', ('', 0))[1],))]
        return menu




class SE_EntityBrowserEntry(uicls.SE_GenericCore):
    __guid__ = 'uicls.SE_EntityBrowserEntry'

    def GetMenu(self):
        menu = []
        if not self.sr.node.get('showmenu', True):
            return menu

        def CopyID(id):
            blue.pyos.SetClipboardData(str(id))


        menu += [('Copy ID', CopyID, (self.sr.node.get('entityID', 0),))]
        return menu




