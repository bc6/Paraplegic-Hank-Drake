import geo2
import util
import uicls
import uiconst
import GameWorld

class EveCharControl(uicls.CharControlCore):
    __guid__ = 'uicls.CharControl'

    def ApplyAttributes(self, *args, **kw):
        uicls.CharControlCore.ApplyAttributes(self, *args, **kw)
        self.entityID = None
        self.cameraClient = sm.GetService('cameraClient')
        self.mouseInputHandler = sm.GetService('mouseInput')
        self.contextMenuClient = sm.GetService('contextMenuClient')
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.navigation = sm.GetService('navigation')
        self.entityClient = sm.GetService('entityClient')
        self.menuSvc = sm.GetService('menu')
        self.entityClient.RegisterForSceneLifeCycle(self)



    def Startup(self):
        pass



    def OnOpenView(self):
        uicls.CharControlCore.OnOpenView(self)
        self.state = uiconst.UI_PICKCHILDREN
        sm.GetService('bracketClient').ReloadBrackets()
        self.navigation.Reset()
        player = self.entityClient.GetPlayerEntity()
        if player is not None:
            player.animation.controller.Reset()



    def OnCloseView(self):
        uicls.CharControlCore.OnCloseView(self)



    def OnMouseDown(self, button, *args):
        self.entityID = self._PickObject(uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
        self.mouseInputHandler.OnMouseDown(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def OnMouseUp(self, button, *args):
        self.entityID = self._PickObject(uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y))
        self.mouseInputHandler.OnMouseUp(button, uicore.uilib.x, uicore.uilib.y, self.entityID)



    def GetMenu(self):
        x = uicore.ScaleDpi(uicore.uilib.x)
        y = uicore.ScaleDpi(uicore.uilib.y)
        self.contextMenuClient = sm.GetService('contextMenuClient')
        entityID = self._PickObject(x, y)
        if entityID:
            return self.contextMenuClient.GetMenuForEntityID(entityID)
        altPickObject = self._PickHangarScene(x, y)
        if altPickObject and hasattr(altPickObject, 'name') and altPickObject.name == str(util.GetActiveShip()):
            return self.GetShipMenu()



    def GetShipMenu(self):
        if util.GetActiveShip():
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            hangarItems = hangarInv.List()
            for each in hangarItems:
                if each.itemID == util.GetActiveShip():
                    return self.menuSvc.InvItemMenu(each)

        return []



    def OnDropData(self, dragObj, nodes):
        sm.GetService('loading').StopCycle()
        if len(nodes) == 1:
            node = nodes[0]
            if getattr(node, '__guid__', None) not in ('xtriui.InvItem', 'listentry.InvItem'):
                return 
            if session.shipid == node.item.itemID:
                eve.Message('CantMoveActiveShip', {})
                return 
            if node.item.categoryID == const.categoryShip and node.item.singleton:
                if not node.item.ownerID == eve.session.charid:
                    eve.Message('CantDoThatWithSomeoneElsesStuff')
                    return 
                sm.GetService('station').TryActivateShip(node.item)
        selsvc = sm.GetService('station').GetSvc()
        if selsvc is not None:
            if util.LocalSvcHasAttr(selsvc, 'OnStuffDropOnMainArea'):
                uthread.new(selsvc.OnStuffDropOnMainArea, nodes)



    def OnMouseWheel(self, *args):
        self.mouseInputHandler.OnMouseWheel(uicore.uilib.dz)



    def OnMouseMove(self, *args):
        self.mouseInputHandler.OnMouseMove(uicore.uilib.dx, uicore.uilib.dy, self.entityID)



    def OnClick(self, *args):
        pass



    def OnDblClick(self, *args):
        if self.entityID is None:
            x = uicore.ScaleDpi(uicore.uilib.x)
            y = uicore.ScaleDpi(uicore.uilib.y)
            altPickObject = self._PickHangarScene(x, y)
            if altPickObject and hasattr(altPickObject, 'name') and altPickObject.name == str(util.GetActiveShip()):
                sm.GetService('cmd').OpenCargoHoldOfActiveShip()
                return 
        self.mouseInputHandler.OnDoubleClick(self.entityID)



    def _PickObject(self, x, y):
        if not self.gameWorldClient.HasGameWorld(session.worldspaceid):
            return 
        else:
            gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)
            if gameWorld is None:
                return 
            (startPoint, endPoint,) = self.cameraClient.GetActiveCamera().GetRay(x, y)
            collisionGroups = 1 << GameWorld.GROUP_AVATAR | 1 << GameWorld.GROUP_COLLIDABLE_NON_PUSHABLE
            p = gameWorld.LineTestEntId(startPoint, endPoint, session.charid, collisionGroups)
            if p is not None:
                return p[2]
            return p



    def _PickHangarScene(self, x, y):
        activeCam = self.cameraClient.GetActiveCamera()
        if hasattr(activeCam, 'PickHangarScene'):
            return activeCam.PickHangarScene(x, y)



    def OverridePick(self, x, y):
        overrideObject = None
        entityID = self._PickObject(x, y)
        if entityID:
            entity = sm.GetService('entityClient').FindEntityByID(entityID)
            if entity:
                camera = self.cameraClient.GetActiveCamera()
                (startPoint, endPoint,) = camera.GetRay(x, y)
                direction = geo2.Subtract(endPoint, startPoint)
                uvSvc = sm.GetService('uvPickingClient')
                if entity.HasComponent('UIDesktopComponent') and entity.HasComponent('uvPicking'):
                    uv = uvSvc.PickEntity(entity, startPoint, direction)
                    if not uv:
                        return 
                    desktopComponent = entity.GetComponent('UIDesktopComponent')
                    desktop = desktopComponent.uiDesktop
                    u = int(uv[1][0] * desktop.width)
                    v = int(uv[1][1] * desktop.height)
                    triobj = desktopComponent.uiDesktop.renderObject.PickObject(u, v, None, None, None)
                    if triobj:
                        overrideObject = uicore.uilib.GetPyObjectFromRenderObject(triobj)
        return overrideObject




